"""
Legacy logger compatibility
This maintains compatibility for any old imports
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# Import the new logger
from core.logger import MessageLogger

# Maintain backward compatibility
__all__ = ['MessageLogger']
