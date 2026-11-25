"""Jetson Nano battery charge/discharge monitor.

The electrical design and the datasheet citations live in ``battery/README.md``.
This package reads the INA228, counts coulombs, and writes the state file
and the UART log. It does not serve a web page.
"""

__version__ = "1.0.0"
