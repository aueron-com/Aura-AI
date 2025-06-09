import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.llm_service import MultiLLMManager, verify_provider_connection
from services.stt_service import verify_deepgram_api_key, DeepgramManager
from services.vision_service import vision_service, verify_vision_provider_connection

router = APIRouter()

async def send_json(websocket: WebSocket, type: str, payload: dict):
    """Helper function to send JSON data to the client with error handling."""
    try:
        if websocket.client_state.name == 'CONNECTED':
            await websocket.send_text(json.dumps({"type": type, "payload": payload}))
        else:
            print(f"⚠️ WebSocket not connected, cannot send {type}")
            return False
    except Exception as e:
        print(f"⚠️ Failed to send {type}: {e}")
        return False
    return True

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔗 WebSocket connection established")
    
    dg_manager = None
    multi_llm_manager = None
    
    # --- State Management ---
    session_state = {
        "is_muted": False,
        "process_all_speakers": True,
        "is_universally_muted": False # System-wide pause
    }
    
    # --- DECOUPLED TRANSCRIPT BUFFERING (FINAL) ---
    # This new system is robust against unreliable `is_final` flags and speaker diarization.
    # It accumulates final transcripts and only processes them after a period of true silence.
    aggregated_final_transcript = ""
    silence_timer = None

    async def process_aggregated_transcript():
        nonlocal aggregated_final_transcript
        
        if aggregated_final_transcript:
            print(f"✅ Silence detected. Processing transcript: {aggregated_final_transcript}")
            
            if multi_llm_manager:
                try:
                    # Check if WebSocket is still connected before processing
                    if websocket.client_state.name != 'CONNECTED':
                        print("⚠️ WebSocket disconnected, skipping transcript processing")
                        aggregated_final_transcript = ""
                        return
                    
                    # Send AI processing started signal
                    send_success = await send_json(websocket, "ai_processing_started", {
                        "question": aggregated_final_transcript,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    if not send_success:
                        print("⚠️ Failed to send processing started signal, aborting")
                        aggregated_final_transcript = ""
                        return
                    
                    # Create streaming callback for real-time response with error handling
                    async def stream_callback(chunk: str, chunk_type: str):
                        try:
                            if websocket.client_state.name == 'CONNECTED':
                                return await send_json(websocket, "ai_answer_chunk", {
                                    "chunk": chunk,
                                    "chunk_type": chunk_type,
                                    "timestamp": datetime.now().isoformat()
                                })
                            else:
                                print(f"⚠️ WebSocket not connected, skipping chunk: {chunk[:50]}...")
                                return False  # Signal to stop streaming
                        except Exception as e:
                            print(f"⚠️ Stream callback error (continuing): {e}")
                            return False  # Signal to stop streaming
                    
                    # Get AI answer with streaming
                    answer, result_info = await multi_llm_manager.get_ai_answer(
                        aggregated_final_transcript, 
                        stream_callback
                    )
                    
                    # Check connection again before sending final response
                    if websocket.client_state.name != 'CONNECTED':
                        print("⚠️ WebSocket disconnected during processing, skipping final response")
                        aggregated_final_transcript = ""
                        return
                    
                    # Send final response with metadata
                    response_data = {
                        "answer": answer,
                        "preset_used": result_info.get("preset_used", {}),
                        "success": result_info.get("success", False),
                        "is_final": True
                    }
                    
                    # Include additional info for errors or fallbacks
                    if result_info.get("fallback_used"):
                        response_data["fallback_info"] = {
                            "fallback_used": True,
                            "original_preset": result_info.get("original_preset")
                        }
                    
                    if result_info.get("error"):
                        response_data["error_info"] = {
                            "error_type": result_info.get("error"),
                            "provider": result_info.get("provider"),
                            "model": result_info.get("model")
                        }
                    
                    final_success = await send_json(websocket, "ai_answer_complete", response_data)
                    if final_success:
                        print(f"🤖 AI STREAMING COMPLETE: {answer[:100]}...")
                    else:
                        print("⚠️ Failed to send final AI response")
                    
                except WebSocketDisconnect:
                    print("🔌 Client disconnected during transcript processing")
                    aggregated_final_transcript = ""
                    return
                except Exception as e:
                    print(f"❌ CRITICAL: Error processing transcript: {e}")
                    # Try to send error response if WebSocket is still connected
                    if websocket.client_state.name == 'CONNECTED':
                        try:
                            await send_json(websocket, "ai_answer_complete", {
                                "answer": "I'm sorry, there was an error processing your question. Please try again.",
                                "error_info": {"error_type": "processing_error", "message": str(e)},
                                "success": False,
                                "is_final": True
                            })
                        except Exception as send_error:
                            print(f"⚠️ Failed to send error response: {send_error}")
                    else:
                        print("⚠️ Cannot send error response - WebSocket disconnected")
            
            # IMPORTANT: Reset the buffer after processing.
            aggregated_final_transcript = ""
        # If buffer is empty, do nothing.

    async def on_transcript(data):
        nonlocal aggregated_final_transcript, silence_timer
        try:
            if session_state.get("is_universally_muted", False):
                return

            # Check if WebSocket is still connected before sending updates
            if websocket.client_state.name != 'CONNECTED':
                print("⚠️ WebSocket disconnected, stopping transcript processing")
                return

            send_success = await send_json(websocket, "transcript_update", data)
            if not send_success:
                print("⚠️ Failed to send transcript update, connection may be lost")
                return

            transcript = data.get('transcript', '').strip()
            is_final = data.get('is_final', False)

            # --- 1. Universal Silence Timer Management ---
            # Any transcript activity, interim or final, proves the user is not silent.
            # We unconditionally cancel any pending processing and reset the silence timer.
            if transcript:
                if silence_timer and not silence_timer.done():
                    silence_timer.cancel()
                
                async def delayed_processing():
                    await asyncio.sleep(0.8)  # Reduced from 1.3s to 0.8s for faster processing
                    await process_aggregated_transcript() # Fire the processor after silence
                
                silence_timer = asyncio.create_task(delayed_processing())

            # --- 2. Final Transcript Accumulation ---
            # Determine if this transcript should be processed based on settings
            speaker = data.get('speaker')
            if session_state["is_muted"]:
                should_process = True
            elif session_state["process_all_speakers"]:
                should_process = True
            else:
                should_process = (speaker == 0)

            # We only add to our buffer if the transcript is final and should be processed.
            if is_final and should_process:
                aggregated_final_transcript = (aggregated_final_transcript + " " + transcript).strip()
                print(f"📝 Appended to aggregate buffer. New buffer: '{aggregated_final_transcript}'")
            elif is_final and not should_process: # Candidate speech
                 print(f"👤 CANDIDATE (FINAL): {transcript}")
                 if multi_llm_manager:
                     multi_llm_manager.process_candidate_response(transcript)

        except WebSocketDisconnect:
            print("🔌 Client disconnected while sending transcript/answer")
            # Clear the buffer and stop processing
            aggregated_final_transcript = ""
            if silence_timer and not silence_timer.done():
                silence_timer.cancel()
            return
        except Exception as e:
            print(f"❌ ERROR: Error in transcript callback: {e}")
            # Check if it's a connection issue and handle gracefully
            if "WebSocket" in str(e) or "connection" in str(e).lower():
                print("🔌 Connection-related error in transcript callback")
                aggregated_final_transcript = ""
                if silence_timer and not silence_timer.done():
                    silence_timer.cancel()
                return

    try:
        # 1. Immediately check the Deepgram key upon connection
        print("🔑 Verifying Deepgram API key...")
        is_deepgram_valid = verify_deepgram_api_key()
        await send_json(websocket, "api_key_status", {"service": "deepgram", "valid": is_deepgram_valid})
        # AI provider verification is now done on the frontend before starting

        # 2. Listen for messages from the client
        while True:
            try:
                message = await websocket.receive()
            except Exception as e:
                print(f"❌ ERROR: Failed to receive message: {e}")
                break
                
            if 'text' in message:
                data = json.loads(message['text'])
                if data['type'] == 'start_interview':
                    print("🎬 Starting interview session...")
                    payload = data.get('payload', {})
                    primary_provider_config = payload.get('aiProvider')
                    secondary_provider_config = payload.get('aiSecondaryProvider')
                    primary_vision_config = payload.get('visionProvider')
                    secondary_vision_config = payload.get('visionSecondaryProvider')
                    onboarding_context = payload.get('onboardingData', {})
                    session_state["is_muted"] = payload.get('is_muted', False)
                    session_state["process_all_speakers"] = payload.get('process_all_speakers', True)
                    session_state["is_universally_muted"] = payload.get('is_universally_muted', False)

                    if not primary_provider_config:
                        print("❌ Cannot start interview: Primary AI provider not selected.")
                        await send_json(websocket, "error", {"message": "Primary AI provider not selected."})
                        return

                    try:
                        # Create and configure MultiLLMManager
                        multi_llm_manager = MultiLLMManager()
                        
                        # Load configuration with primary and optional secondary
                        config_loaded = multi_llm_manager.load_configuration(
                            primary_config={
                                "provider": primary_provider_config.get("name"),
                                "model": primary_provider_config.get("model")
                            },
                            secondary_config={
                                "provider": secondary_provider_config.get("name") if secondary_provider_config else None,
                                "model": secondary_provider_config.get("model") if secondary_provider_config else None
                            } if secondary_provider_config else None
                        )
                        
                        if not config_loaded:
                            await send_json(websocket, "error", {"message": "Failed to load AI provider configuration."})
                            return
                        
                        # Initialize shared candidate context
                        multi_llm_manager.initialize_candidate_context(onboarding_context)
                        
                        # Share context manager with vision service for conversation history
                        vision_service.set_context_manager(multi_llm_manager.shared_context)
                        
                        # Perform initial health checks
                        health_results = await multi_llm_manager.perform_health_checks()
                        
                        # Log the context and configuration
                        print(f"📋 Interview context loaded:")
                        print(f"   - Name: {onboarding_context.get('name', 'Not provided')}")
                        print(f"   - Company: {onboarding_context.get('company', 'Not provided')}")
                        print(f"   - Role: {onboarding_context.get('role', 'Not provided')}")
                        print(f"   - Focus areas: {onboarding_context.get('focus', [])}")
                        print(f"🎯 AI Configuration:")
                        print(f"   - Primary: {primary_provider_config.get('name')} - {primary_provider_config.get('model')}")
                        if secondary_provider_config:
                            print(f"   - Secondary: {secondary_provider_config.get('name')} - {secondary_provider_config.get('model')}")
                        if primary_vision_config:
                            print(f"   - Vision Primary: {primary_vision_config.get('name')} - {primary_vision_config.get('model')}")
                        if secondary_vision_config:
                            print(f"   - Vision Secondary: {secondary_vision_config.get('name')} - {secondary_vision_config.get('model')}")
                        print(f"🏥 Health Status: {health_results}")
                        
                        # Send initial preset information to frontend
                        current_preset = multi_llm_manager.get_current_preset_info()
                        await send_json(websocket, "preset_initialized", {
                            "current_preset": current_preset,
                            "available_presets": list(multi_llm_manager.presets.keys()),
                            "health_status": health_results
                        })
                        
                        # Initialize vision service
                        vision_service.load_vision_providers(
                            primary_config=primary_vision_config,
                            secondary_config=secondary_vision_config
                        )
                        print("✅ Vision service configured with selected providers")
                        
                        # Start Deepgram manager with user's programming languages for better keyterm accuracy
                        user_languages = onboarding_context.get('selectedLanguages', [])
                        dg_manager = DeepgramManager(on_transcript, user_languages)
                        await dg_manager.start()
                        
                    except Exception as e:
                        print(f"❌ CRITICAL: Failed to initialize MultiLLMManager: {e}")
                        await send_json(websocket, "error", {"message": f"Failed to initialize AI providers: {str(e)}"})
                        return
                elif data['type'] == 'config_update':
                    payload = data.get('payload', {})
                    if 'processAllSpeakers' in payload:
                        session_state["process_all_speakers"] = payload['processAllSpeakers']
                        print(f"🎯 Process All Speakers config updated: {session_state['process_all_speakers']}")
                    if 'isUniversallyMuted' in payload:
                        session_state["is_universally_muted"] = payload['isUniversallyMuted']
                        print(f"⏸️ Universal Mute config updated: {session_state['is_universally_muted']}")
                        
                elif data['type'] == 'switch_preset':
                    # Handle preset switching requests
                    if not multi_llm_manager:
                        await send_json(websocket, "error", {"message": "AI providers not initialized"})
                        continue
                        
                    payload = data.get('payload', {})
                    preset_key = payload.get('preset_key')
                    
                    if not preset_key:
                        await send_json(websocket, "error", {"message": "Preset key is required"})
                        continue
                    
                    try:
                        success, result = await multi_llm_manager.switch_preset(preset_key)
                        
                        if success:
                            await send_json(websocket, "preset_switched", {
                                "success": True,
                                "current_preset": result.get("current_preset"),
                                "previous_preset": result.get("previous_preset"),
                                "auto_selected": result.get("auto_selected", False),
                                "health_results": result.get("health_results"),
                                "message": f"Switched to {result.get('current_preset', {}).get('description', 'Unknown')}"
                            })
                            print(f"✅ Preset switched successfully to: {preset_key}")
                        else:
                            error_msg = result.get("error", "Failed to switch preset")
                            await send_json(websocket, "preset_switch_failed", {
                                "success": False,
                                "error": error_msg,
                                "available_presets": result.get("available_presets", []),
                                "health_results": result.get("health_results")
                            })
                            print(f"❌ Preset switch failed: {error_msg}")
                            
                    except Exception as e:
                        print(f"❌ CRITICAL: Error switching preset: {e}")
                        await send_json(websocket, "error", {"message": f"Error switching preset: {str(e)}"})
                        
                elif data['type'] == 'get_system_status':
                    # Handle system status requests
                    if multi_llm_manager:
                        try:
                            status = multi_llm_manager.get_system_status()
                            await send_json(websocket, "system_status", status)
                        except Exception as e:
                            print(f"❌ Error getting system status: {e}")
                            await send_json(websocket, "error", {"message": f"Error getting system status: {str(e)}"})
                    else:
                        await send_json(websocket, "error", {"message": "AI providers not initialized"})
                        
                elif data['type'] == 'vision_analysis':
                    # Handle vision analysis requests
                    payload = data.get('payload', {})
                    
                    try:
                        prompt = payload.get('prompt', '')
                        screenshots = payload.get('screenshots', [])
                        vision_config = payload.get('visionConfig', {})
                        languages = payload.get('languages', [])
                        
                        if not screenshots:
                            await send_json(websocket, "vision_analysis_result", {
                                "success": False,
                                "error": "No screenshots provided for analysis"
                            })
                            continue
                        
                        if not vision_config or not vision_config.get('provider') or not vision_config.get('model'):
                            await send_json(websocket, "vision_analysis_result", {
                                "success": False,
                                "error": "Vision provider configuration missing"
                            })
                            continue
                        
                        print(f"🔍 Processing vision analysis request:")
                        print(f"   Provider: {vision_config['provider']}")
                        print(f"   Model: {vision_config['model']}")
                        print(f"   Screenshots: {len(screenshots)}")
                        print(f"   Languages: {languages}")
                        
                        # Perform vision analysis
                        analysis, result_info = await vision_service.analyze_coding_problem(
                            provider_name=vision_config['provider'],
                            model_name=vision_config['model'],
                            screenshots=screenshots,
                            languages=languages
                        )
                        
                        # Send result back to client
                        await send_json(websocket, "vision_analysis_result", {
                            "success": result_info.get("success", False),
                            "analysis": analysis,
                            "metadata": result_info,
                            "screenshot_count": len(screenshots),
                            "languages": languages
                        })
                        
                        if result_info.get("success"):
                            print(f"✅ Vision analysis completed successfully")
                        else:
                            print(f"❌ Vision analysis failed: {result_info.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        print(f"❌ CRITICAL: Error processing vision analysis: {e}")
                        await send_json(websocket, "vision_analysis_result", {
                            "success": False,
                            "error": f"Vision analysis processing failed: {str(e)}"
                        })
                elif data['type'] == 'audio_chunk':
                    if dg_manager:
                        # If universally muted, do not process audio chunks
                        if session_state.get("is_universally_muted", False):
                            # Log occasionally to confirm it's working
                            # print("⏸️ System paused. Ignoring audio chunk.")
                            return

                        payload = data.get('payload', {})
                        audio_data = bytes(payload.get('audio', []))
                        session_state["is_muted"] = payload.get('is_muted', False) # Update mic mute state
                        
                        if len(audio_data) > 0:
                            await dg_manager.send_audio(audio_data)
                        else:
                            print("⚠️ WARNING: Received empty audio data")
                elif data['type'] == 'end_interview':
                    print("🛑 Ending interview session...")
                    if dg_manager:
                        await dg_manager.finish()
                    break  # End the session
            elif 'bytes' in message: # Legacy support, should be deprecated
                if dg_manager:
                    audio_data = message['bytes']
                    if len(audio_data) > 0:
                        await dg_manager.send_audio(audio_data)
                    else:
                        print("⚠️ WARNING: Received empty audio data")
                else:
                    print("⚠️ WARNING: Received audio but dg_manager is None")

    except WebSocketDisconnect:
        print("🔌 WebSocket connection closed by client")
    except Exception as e:
        print(f"❌ ERROR: WebSocket error: {e}")
    finally:
        if dg_manager:
            await dg_manager.finish()
        print("🧹 WebSocket resources cleaned up")