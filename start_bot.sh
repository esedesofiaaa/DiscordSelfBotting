#!/bin/bash

# Discord Self Bot - Startup Script
# This script starts the Discord Self Bot with proper environment setup

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Discord Self Bot Startup ===${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo -e "${YELLOW}📋 Please copy .env.example to .env and configure it${NC}"
    echo -e "${BLUE}💡 Run: cp .env.example .env${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update requirements
echo -e "${BLUE}📥 Installing/updating requirements...${NC}"
pip install -r requirements.txt

# Create logs directory if it doesn't exist
mkdir -p logs

# Check configuration
echo -e "${BLUE}🔍 Checking configuration...${NC}"
python3 -c "
import sys
sys.path.insert(0, 'src')
from core.config import config
validation = config.validate()
if validation['errors']:
    print('❌ Configuration errors:')
    for error in validation['errors']:
        print(f'  - {error}')
    sys.exit(1)
if validation['warnings']:
    print('⚠️ Configuration warnings:')
    for warning in validation['warnings']:
        print(f'  - {warning}')
print('✅ Configuration is valid')
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Configuration validation failed${NC}"
    exit 1
fi

# Start the bot
echo -e "${GREEN}🚀 Starting Discord Self Bot...${NC}"
echo -e "${BLUE}📋 Press Ctrl+C to stop the bot${NC}"
echo ""

python3 run.py
