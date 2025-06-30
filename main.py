"""
Discord Self Bot - Compatibility Entry Point
This file maintains compatibility with the old structure while using the new organized code
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the new organized bot
from bot.client import main

if __name__ == "__main__":
    print("⚠️ Note: main.py has been reorganized. Consider using 'run.py' or './start_bot.sh' instead.")
    print("🔄 Running with new organized structure...")
    main()
