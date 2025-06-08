from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application settings and loads them from a .env file.
    All defaults should be production-safe values that match .env file settings.
    """
    # Required API Keys (no defaults - must be provided)
    DEEPGRAM_API_KEY: str
    
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    # Development Mode - Controls debugging features
    # Default to False for production safety, .env file controls actual value
    DEV_MODE: bool = False
    
    # AI Configuration - Defaults match .env file values
    TRACK_CANDIDATE_RESPONSES: bool = True
    INCLUDE_CONVERSATION_HISTORY: bool = True
    MAX_CONVERSATION_HISTORY: int = 5
    GENERATE_FULL_ANSWERS: bool = True
    PERSONALIZE_ANSWERS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True
    )

# Create a single, reusable instance of the settings
settings = Settings()

def print_config_debug():
    """Debug function to show current configuration values and their sources"""
    print("🔧 CONFIGURATION DEBUG:")
    print(f"   📁 DEV_MODE = {settings.DEV_MODE} (from .env: {settings.DEV_MODE})")
    print(f"   📊 LOG_LEVEL = {settings.LOG_LEVEL}")
    print(f"   🤖 AI Settings:")
    print(f"      TRACK_CANDIDATE_RESPONSES = {settings.TRACK_CANDIDATE_RESPONSES}")
    print(f"      INCLUDE_CONVERSATION_HISTORY = {settings.INCLUDE_CONVERSATION_HISTORY}")
    print(f"      MAX_CONVERSATION_HISTORY = {settings.MAX_CONVERSATION_HISTORY}")
    print(f"      GENERATE_FULL_ANSWERS = {settings.GENERATE_FULL_ANSWERS}")
    print(f"      PERSONALIZE_ANSWERS = {settings.PERSONALIZE_ANSWERS}")
    print(f"   🔑 API Keys: DEEPGRAM={'*' * 20}")
    
    # Verify .env file is being read
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
            dev_mode_in_file = 'DEV_MODE=false' in env_content.lower()
            print(f"   📄 .env file check: DEV_MODE=false found = {dev_mode_in_file}")
    except Exception as e:
        print(f"   ❌ Could not read .env file: {e}")