#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Receptionist AI - Main Entry Point
Chạy ứng dụng AI Receptionist với giao diện streaming
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.main_streaming import StreamingAIReceptionist

def main():
    """Main function to start the AI Receptionist"""
    try:
        print("Starting Receptionist AI...")
        receptionist = StreamingAIReceptionist()
        receptionist.run()
    except KeyboardInterrupt:
        print("\nShutting down Receptionist AI...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()