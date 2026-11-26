"""Jetson Orin Nano battery charge/discharge monitor.

The electrical design and the datasheet citations live in ``battery/README.md``.
This package reads the INA228, counts coulombs, and writes the state file.
UART logging is optional and off unless the profile sets ``uart_enabled``.
It does not serve a web page.
"""

__version__ = "1.0.0"
