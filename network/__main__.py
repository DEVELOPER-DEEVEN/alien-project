#!/usr/bin/env python3

"""
Network Framework Main Entry Point

This module allows Network framework to be run as a package:
    python -m alien.network --interactive
    python -m alien.network "Create a data pipeline"
"""

import asyncio
import sys
from .network import main

if __name__ == "__main__":
    asyncio.run(main())
