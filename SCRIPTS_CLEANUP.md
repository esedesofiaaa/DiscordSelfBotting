# 🧹 Scripts Cleanup Recommendations

## Current Scripts Analysis

### Production Scripts (Keep):
- `setup-linode.sh` - Initial server setup
- `check_env.sh` - Environment verification (useful for debugging)

### Development Scripts (Local only - consider moving to dev folder):
- `start_bot.sh` - Local development with validations
- `start_bot_simple.sh` - Simple local execution

### Redundant Scripts (Can be removed):
- `fix-deployment.sh` - Functionality covered by setup-linode.sh
- `configure-sudo.sh` - Same as fix-deployment.sh but less complete

## Issues Found:

### 1. Virtual Environment Inconsistency
- **Local scripts**: Use `discord_selfbotting/` venv
- **Production**: Uses `venv/` 
- **Fix**: Standardize on `venv/` everywhere

### 2. Configuration Inconsistency  
- **Local scripts**: Look for `.env` file
- **Production**: Uses `config.py`
- **Fix**: Update local scripts to use config.py or create .env support in production

### 3. Path Conflicts
- Scripts assume different working directories
- **Fix**: Use absolute paths or consistent directory structure

## Recommended Actions:

1. **Remove redundant scripts:**
   ```bash
   rm fix-deployment.sh configure-sudo.sh
   ```

2. **Move development scripts to dev folder:**
   ```bash
   mkdir dev/
   mv start_bot.sh start_bot_simple.sh dev/
   ```

3. **Update remaining scripts for consistency**

4. **Add .gitignore entries for local development files**
