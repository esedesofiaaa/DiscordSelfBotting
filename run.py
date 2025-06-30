"""
Discord Self Bot - Entry Point
Simple entry point that imports and runs the organized bot
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.client import main

if __name__ == "__main__":
    main()
