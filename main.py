#!/usr/bin/env python3

# This is the main entry point for the Redstar server
# All functionality has been moved to redstar_main.py for better organization

import sys
import os

# Add current directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from redstar_main import main

if __name__ == "__main__":
    main()