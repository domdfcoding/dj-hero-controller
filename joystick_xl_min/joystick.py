"""
The base JoystickXL class for updating input states and sending USB HID reports.

This module provides the necessary functions to create a JoystickXL object,
retrieve its input counts, associate input objects and update its input states.
"""

import struct, usb_hid

# These typing imports help during development in vscode but fail in CircuitPython
try:
    from typing import Tuple
except ImportError:
    pass

from joystick_xl.inputs import Axis


def _get_device():
    """Find a JoystickXL device in the list of active USB HID devices."""
    for device in usb_hid.devices:
        if (
            device.usage_page == 0x01
            and device.usage == 0x04
            and hasattr(device, "send_report")
        ):
            return device
    raise ValueError("Could not find JoystickXL HID device - check boot.py.)")


class Joystick:
    """Base JoystickXL class for updating input states and sending USB HID reports."""

    _num_axes = 0
    """The number of axes this joystick can support."""

    _num_buttons = 0
    """The number of buttons this joystick can support."""

    _report_size = 0
    """The size (in bytes) of USB HID reports for this joystick."""

    @property
    def num_axes(self) -> int:
        """Return the number of available axes in the USB HID descriptor."""
        return self._num_axes

    @property
    def num_buttons(self) -> int:
        """Return the number of available buttons in the USB HID descriptor."""
        return self._num_buttons

    def __init__(self) -> None:
        """
        Create a JoystickXL object with all inputs in idle states.

        .. code::

           from joystick_xl.joystick import Joystick

           js = Joystick()

        .. note:: A JoystickXL ``usb_hid.Device`` object has to be created in
           ``boot.py`` before creating a ``Joystick()`` object in ``code.py``,
           otherwise an exception will be thrown.
        """
        # load configuration from ``boot_out.txt``
        try:
            with open("/boot_out.txt", "r") as boot_out:
                for line in boot_out.readlines():
                    if "JoystickXL" in line:
                        config = [int(s) for s in line.split() if s.isdigit()]
                        if len(config) < 4:
                            raise (ValueError)
                        Joystick._num_axes = config[0]
                        Joystick._num_buttons = config[1]
                        Joystick._report_size = config[3]
                        break
            if Joystick._report_size == 0:
                raise (ValueError)
        except (OSError, ValueError):
            raise (Exception("Error loading JoystickXL configuration."))

        self._device = _get_device()
        self._report = bytearray(self._report_size)
        self._last_report = bytearray(self._report_size)
        self._format = "<"

        self._axis_states = list()
        for _ in range(self.num_axes):
            self._axis_states.append(Axis.IDLE)
            self._format += "B"

        self._button_states = list()
        for _ in range((self.num_buttons // 8) + bool(self.num_buttons % 8)):
            self._button_states.append(0)
            self._format += "B"

        try:
            self.reset_all()
        except OSError:
            time.sleep(1)
            self.reset_all()

    @staticmethod
    def _validate_axis_value(axis: int, value: int) -> bool:
        """
        Ensure the supplied axis index and value are valid.

        :param axis: The 0-based index of the axis to validate.
        :type axis: int
        :param value: The axis value to validate.
        :type value: int
        :raises ValueError: No axes are configured for the JoystickXL device.
        :raises ValueError: The supplied axis index is out of range.
        :raises ValueError: The supplied axis value is out of range.
        :return: ``True`` if the supplied axis index and value are valid.
        :rtype: bool
        """
        if Joystick._num_axes == 0:
            raise ValueError("There are no axes configured.")
        if axis + 1 > Joystick._num_axes:
            raise ValueError("Specified axis is out of range.")
        if not Axis.MIN <= value <= Axis.MAX:
            raise ValueError("Axis value must be in range 0 to 255")
        return True

    @staticmethod
    def _validate_button_number(button: int) -> bool:
        """
        Ensure the supplied button index is valid.

        :param button: The 0-based index of the button to validate.
        :type button: int
        :raises ValueError: No buttons are configured for the JoystickXL device.
        :raises ValueError: The supplied button index is out of range.
        :return: ``True`` if the supplied button index is valid.
        :rtype: bool
        """
        if Joystick._num_buttons == 0:
            raise ValueError("There are no buttons configured.")
        if not 0 <= button <= Joystick._num_buttons - 1:
            raise ValueError("Specified button is out of range.")
        return True

    def update(self, always: bool = False) -> None:
        """
        Update all inputs in associated input lists and generate a USB HID.

        :param always: When ``True``, send a report even if it is identical to the last
           report that was sent out.  Defaults to ``False``.
        :type always: bool, optional
        """
      
        # Generate a USB HID report.
        report_data = list()

        report_data.extend(self._axis_states)

        report_data.extend(self._button_states)

        struct.pack_into(self._format, self._report, 0, *report_data)

        # Send the USB HID report if required.
        if always or self._last_report != self._report:
            self._device.send_report(self._report)
            self._last_report[:] = self._report

    def reset_all(self) -> None:
        """Reset all inputs to their idle states."""
        for i in range(self.num_axes):
            self._axis_states[i] = Axis.IDLE
        for i in range(len(self._button_states)):
            self._button_states[i] = 0
        self.update(always=True)

    def update_axis(
        self,
        *axis: Tuple[int, int],
        defer: bool = False,
        skip_validation: bool = False,
    ) -> None:
        """
        Update the value of one or more axis input(s).

        :param axis: One or more tuples containing an axis index (0-based) and value
           (``0`` to ``255``, with ``128`` indicating the axis is idle/centered).
        :type axis: Tuple[int, int]
        :param defer: When ``True``, prevents sending a USB HID report upon completion.
           Defaults to ``False``.
        :type defer: bool
        :param skip_validation: When ``True``, bypasses the normal input number/value
           validation that occurs before they get processed.  This is used for *known
           good values* that are generated using the ``Joystick.axis[]``,
           ``Joystick.button[]`` and ``Joystick.hat[]`` lists.  Defaults to ``False``.
        :type skip_validation: bool

        .. code::

           # Updates a single axis
           update_axis((0, 42))  # 0 = x-axis

           # Updates multiple axes
           update_axis((1, 22), (3, 237))  # 1 = y-axis, 3 = rx-axis

        .. note::

           ``update_axis`` is called automatically for any axis objects added to the
           built in ``Joystick.axis[]`` list when ``Joystick.update()`` is called.
        """
        for a, value in axis:
            if skip_validation or self._validate_axis_value(a, value):
                if self.num_axes > 7 and a > 5:
                    a = self.num_axes - a + 5  # reverse sequence for sliders
                self._axis_states[a] = value

        if not defer:
            self.update()

    def update_button(
        self,
        *button: Tuple[int, bool],
        defer: bool = False,
        skip_validation: bool = False,
    ) -> None:
        """
        Update the value of one or more button input(s).

        :param button: One or more tuples containing a button index (0-based) and
           value (``True`` if pressed, ``False`` if released).
        :type button: Tuple[int, bool]
        :param defer: When ``True``, prevents sending a USB HID report upon completion.
           Defaults to ``False``.
        :type defer: bool
        :param skip_validation: When ``True``, bypasses the normal input number/value
           validation that occurs before they get processed.  This is used for *known
           good values* that are generated using the ``Joystick.axis[]``,
           ``Joystick.button[]`` and ``Joystick.hat[]`` lists.  Defaults to ``False``.
        :type skip_validation: bool

        .. code::

           # Update a single button
           update_button((0, True))  # 0 = b1

           # Updates multiple buttons
           update_button((1, False), (7, True))  # 1 = b2, 7 = b8

        .. note::

           ``update_button`` is called automatically for any button objects added to the
           built in ``Joystick.button[]`` list when ``Joystick.update()`` is called.
        """
        for b, value in button:
            if skip_validation or self._validate_button_number(b):
                _bank = b // 8
                _bit = b % 8
                if value:
                    self._button_states[_bank] |= 1 << _bit
                else:
                    self._button_states[_bank] &= ~(1 << _bit)
        if not defer:
            self.update()
