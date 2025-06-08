# Environment Variable Protection Implementation Plan

## Problem Statement
- `DEV_MODE=false` in `.env` file is being overridden by system environment variable `DEV_MODE=true`
- Pydantic's default behavior prioritizes system environment variables over `.env` file values
- Need to force `.env` file precedence and add protection against future conflicts

## Solution Architecture

### 1. Custom Settings Loader with .env Priority
```python
class ProtectedSettings(BaseSettings):
    """Settings class that prioritizes .env file over system environment variables"""
    
    def __init__(self, **kwargs):
        # First load from .env file only
        env_file_values = self._load_env_file_values()
        
        # Then check for system conflicts
        system_conflicts = self._check_system_conflicts(env_file_values)
        
        # Warn about conflicts but use .env values
        if system_conflicts:
            self._warn_about_conflicts(system_conflicts)
        
        # Initialize with .env priority
        super().__init__(**kwargs)
```

### 2. Environment Variable Conflict Detection
- Scan system environment variables for keys that exist in `.env`
- Compare values and warn about conflicts
- Provide clear resolution guidance

### 3. Enhanced Debugging Output
- Show exactly where each configuration value comes from
- Display system vs .env file conflicts
- Provide actionable remediation steps

### 4. Transparency Variable Auditing
- Check for Windows transparency-related environment variables
- Ensure no system variables interfere with transparency settings

## Implementation Steps

### Step 1: Create Custom Settings Class
- Override Pydantic's default loading mechanism
- Implement `.env` file priority loading
- Add conflict detection and warning system

### Step 2: Environment Variable Scanner
- Create function to scan for conflicting system variables
- Generate detailed conflict reports
- Provide specific PowerShell commands to fix conflicts

### Step 3: Enhanced Debug Output
- Expand `print_config_debug()` function
- Show configuration source hierarchy
- Display conflict resolution status

### Step 4: Protection Utilities
- Add utility functions to check and clean environment variables
- Provide system-level environment variable management
- Include transparency-specific variable checks

## Expected Outcomes

1. **Immediate Fix**: `DEV_MODE=false` from `.env` will be respected
2. **Future Protection**: System environment variables won't override `.env` values
3. **Clear Diagnostics**: Enhanced debugging will show exactly what's happening
4. **Conflict Resolution**: Specific guidance on resolving environment variable conflicts

## File Changes Required

- `core/config.py` - Implement custom settings loader with protection
- Add new utility functions for environment variable management
- Enhanced debugging and conflict detection

## Testing Plan

1. Test with existing `DEV_MODE=true` system variable
2. Verify `.env` file values take precedence
3. Test conflict detection and warning system
4. Verify transparency settings are not affected by system variables

This implementation will solve the current issue and prevent similar problems in the future.