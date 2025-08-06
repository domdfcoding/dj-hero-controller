# stdlib
import board

# this package
from joystick_xl.joystick import Joystick
from wiichuck import dj_table

joystick = Joystick()
i2c = board.STEMMA_I2C()
controller = dj_table.DJTable(i2c)

# Buttons
GREEN_L = 0
RED_L = 1
BLUE_L = 2
GREEN_R = 3
RED_R = 4
BLUE_R = 5
EUPHORIA = 6
MINUS = 9  # Select
PLUS = 10  # Start

# Axes
X = 0
Y = 1
SLIDER = 2
DIAL = 3
LEFT_TT = 4
RIGHT_TT = 5

# TODO: get midpoint of joystick on boot and split range into two

output_start = 0
output_end = 255  # TODO: non-linear range


def convert_range(value, start=0, end=63):
	"""
	Convert the range of values from an axis into the appropriate joystick range.

	:param value: The turntable value.
	"""

	a = value - start
	b = end - start
	c = output_end - output_start
	return round(a / b * c + output_start)


def convert_turntable_range(value: int) -> int:
	"""
	Convert the range of values from the turntable into the appropriate joystick range.

	:param value: The turntable value.
	"""

	# TODO: average out to get rid of random zeros

	if value < 0:
		value = -(value + 32)

	return convert_range(value, -31, 31)


def convert_y(value: int, invert: bool = False) -> int:
	"""
	Convert the range of values from the joystick y-axis into the appropriate joystick range.

	:param value: The joystick y-axis value.
	:param invert: Whether to invert the y-axis.
	"""

	if invert:
		return (convert_range(value))
	else:
		return -(convert_range(63 - value, end=-63))


# Press euphoria while plugging in to invert y axis
y_inverted = controller.buttons.euphoria

while True:

	values = controller.values

	joystick.update_button(
			(GREEN_L, values.turntables.left.green),
			(BLUE_L, values.turntables.left.blue),
			(RED_L, values.turntables.left.red),
			(GREEN_R, values.turntables.right.green),
			(BLUE_R, values.turntables.right.blue),
			(RED_R, values.turntables.right.red),
			(EUPHORIA, values.buttons.euphoria),
			(MINUS, values.buttons.minus),
			(12, values.buttons.minus),
			(PLUS, values.buttons.plus),
			(11, values.buttons.plus),
			)

	# x midpoint 32
	# y midpoint 30
	joystick.update_axis(
			(X, convert_range(values.joystick.x)),
			(Y, convert_y(values.joystick.y, y_inverted)),
			(SLIDER, convert_range(values.slider, end=15)),
			(DIAL, convert_range(values.dial, end=31)),
			(LEFT_TT, convert_turntable_range(values.turntables.left.value)),
			(RIGHT_TT, convert_turntable_range(values.turntables.right.value)),
			)
