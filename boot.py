# stdlib
import usb_hid

# this package
from joystick_xl.hid import create_joystick

# This will enable all of the standard CircuitPython USB HID devices along with a
# USB HID joystick.
usb_hid.enable((
		usb_hid.Device.KEYBOARD,
		usb_hid.Device.MOUSE,
		usb_hid.Device.CONSUMER_CONTROL,
		create_joystick(axes=6, buttons=13, hats=0),
		))
