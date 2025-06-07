import asyncio
import requests
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)
from core.config import settings

def verify_deepgram_api_key():
    """
    Verifies the Deepgram API key by making a direct HTTP request.
    This is the most reliable method, independent of SDK changes.
    Returns True if the key is valid, False otherwise.
    """
    if not settings.DEEPGRAM_API_KEY:
        return False

    url = "https://api.deepgram.com/v1/projects"
    headers = {
        "Authorization": f"Token {settings.DEEPGRAM_API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("INFO: Deepgram API key is valid.")
            return True
        else:
            print(f"ERROR: Deepgram API key verification failed. Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: A network error occurred while verifying Deepgram key: {e}")
        return False


class DeepgramManager:
    """
    Manages the connection to Deepgram for live transcription.
    """
    def __init__(self, transcript_callback):
        self.transcript_callback = transcript_callback
        self.dg_connection = None
        self.is_connected = False
        self.stop_event = asyncio.Event()
        
        # No buffering - process final results immediately for faster response
        
        # Setup Deepgram client
        config = DeepgramClientOptions(
            verbose=False,  # Disable verbose logging to reduce spam
            options={"keepalive": "true"}
        )
        self.deepgram = DeepgramClient(settings.DEEPGRAM_API_KEY, config)

    async def start(self):
        """Starts the Deepgram transcription connection."""
        self.dg_connection = self.deepgram.listen.asynclive.v("1")
        
        self.dg_connection.on(LiveTranscriptionEvents.Open, self.on_open)
        self.dg_connection.on(LiveTranscriptionEvents.Transcript, self.on_message)
        self.dg_connection.on(LiveTranscriptionEvents.Error, self.on_error)
        self.dg_connection.on(LiveTranscriptionEvents.Close, self.on_close)

        # Optimized settings for real-time transcription with Nova-3
        options = LiveOptions(
            model="nova-3",  # Updated to Nova-3 for better accuracy
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=48000,  # Ensure this matches your audio source
            diarize=True,
            punctuate=True,
            # Critical speech detection parameters
            utterance_end_ms=1800,    # Wait 1.2 seconds after speech ends to finalize
            endpointing=1100,          # Wait 0.8 seconds of silence before endpoint detection
            # Additional settings
            vad_events=True,          # Enable VAD for better pause handling
            interim_results=True,     # Enable interim results for real-time feedback
            filler_words=True,        # Handle filler words naturally
            numerals=True,            # Better number processing
            multichannel=False,
            alternatives=1,
        )
        
        try:
            await self.dg_connection.start(options)
            print("✅ Deepgram connection started successfully")
        except Exception as e:
            print(f"❌ ERROR: Could not start Deepgram connection: {e}")

    async def on_open(self, *args, **kwargs):
        print("🔗 Deepgram connection opened")
        self.is_connected = True

    async def on_message(self, *args, **kwargs):
        if self.stop_event.is_set():
            return
        
        try:
            result = kwargs['result']
            
            # Check if result has the expected structure and non-empty transcript
            if (hasattr(result, 'channel') and 
                hasattr(result.channel, 'alternatives') and 
                len(result.channel.alternatives) > 0):
                
                alternative = result.channel.alternatives[0]
                transcript = alternative.transcript
                
                if len(transcript.strip()) > 0:  # Only process non-empty transcripts
                    # Check if this is a final result or interim
                    is_final = getattr(result, 'is_final', True)
                    
                    # Debug logging to track final vs interim
                    result_type = "FINAL" if is_final else "interim"
                    print(f"🔍 Deepgram result type: {result_type}, is_final: {is_final}")
                    
                    # Get speaker from words array (Deepgram's diarization format)
                    speaker = 0  # Default to candidate
                    
                    # For live streaming, speaker info is in the words array
                    if hasattr(alternative, 'words') and len(alternative.words) > 0:
                        # Use the speaker of the first word
                        first_word = alternative.words[0]
                        if hasattr(first_word, 'speaker') and first_word.speaker is not None:
                            speaker = first_word.speaker
                        else:
                            # Fallback: try to access speaker as dictionary key
                            if hasattr(first_word, '__getitem__') and 'speaker' in first_word:
                                speaker = first_word['speaker']
                    
                    if is_final:
                        # Process final results immediately - no buffering
                        print(f"✅ FINAL RESULT: Speaker {speaker} - '{transcript.strip()}'")
                        await self.send_final_result(speaker, transcript.strip())
                    else:
                        # Show interim results immediately for real-time feedback
                        print(f"📝 TRANSCRIPT (interim): Speaker {speaker} - '{transcript.strip()}'")
                        
                        # Send interim updates to client for real-time display
                        interim_data = {
                            "speaker": speaker,
                            "transcript": transcript.strip(),
                            "is_final": False
                        }
                        await self.transcript_callback(interim_data)
                        
        except Exception as e:
            print(f"❌ ERROR: Exception in transcript processing: {e}")

    # Removed buffering system - final results are now processed immediately

    async def send_final_result(self, speaker, transcript):
        """Send the final result to the callback."""
        print(f"📝 TRANSCRIPT (FINAL): Speaker {speaker} - '{transcript}'")
        
        transcript_data = {
            "speaker": speaker,
            "transcript": transcript,
            "is_final": True
        }
        await self.transcript_callback(transcript_data)

    async def on_error(self, *args, **kwargs):
        if self.stop_event.is_set():
            return
        error = kwargs['error']
        print(f"❌ Deepgram error: {error}")

    async def on_close(self, *args, **kwargs):
        print("🔌 Deepgram connection closed")
        self.is_connected = False

    async def send_audio(self, audio_chunk, source='unknown'):
        """Sends an audio chunk to Deepgram."""
        if self.is_connected and self.dg_connection and not self.stop_event.is_set():
            await self.dg_connection.send(audio_chunk)

    async def finish(self):
        """Signals the connection to close and finishes it."""
        print("🛑 Closing Deepgram connection...")
        self.stop_event.set()
        
        if self.dg_connection:
            await self.dg_connection.finish()
            print("✅ Deepgram connection closed successfully")