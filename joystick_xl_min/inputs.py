"""
Classes to simplify mapping GPIO pins and values to JoystickXL inputs and states.

This module provides a set of classes to aid in configuring GPIO pins and convert
their raw states to values that are usable by JoystickXL.
"""


class Axis:
    """Data source storage and scaling/deadband processing for an axis input."""

    MIN = 0
    """Lowest possible axis value for USB HID reports."""

    MAX = 255
    """Highest possible axis value for USB HID reports."""

    IDLE = 128
    """Idle/Center axis value for USB HID reports."""

    X = 0
    """Alias for the X-axis index."""

    Y = 1
    """Alias for the Y-axis index."""

    Z = 2
    """Alias for the Z-axis index."""

    RX = 3
    """Alias for the RX-axis index."""

    RY = 4
    """Alias for the RY-axis index."""

    RZ = 5
    """Alias for the RZ-axis index."""

    S0 = 6
    """Alias for the S0-axis index."""

    S1 = 7
    """Alias for the S1-axis index."""
