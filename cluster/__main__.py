#!/usr/bin/env python3
# Copyright (c) Deeven Seru.
# Licensed under the MIT License.

"""
cluster Framework Main Entry Point

This module allows cluster framework to be run as a package:
    python -m Alien.cluster --interactive
    python -m Alien.cluster "Create a data pipeline"
"""

import asyncio
import sys
from .cluster import main

if __name__ == "__main__":
    asyncio.run(main())
