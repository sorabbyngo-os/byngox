#!/usr/bin/env python3
"""
byngox.py — Byngox entry point
Delegates to byngox_runtime.py (unified 12-agent runtime).
Kept for backwards compatibility.
"""
import asyncio
from byngox_runtime import main

if __name__ == "__main__":
    asyncio.run(main())
