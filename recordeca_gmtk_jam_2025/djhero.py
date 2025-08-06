import sys
from linux_joystick import Joystick
from pynput.keyboard import Key, Controller

keyboard = Controller()
js = Joystick(int(sys.argv[1]))

while True:
	event = js.poll()
	if event:
		print(event.id, event.value)
		if event.id == 0:
			if event.value:
				keyboard.press('f')
			else:
				keyboard.release('f')
		if event.id == 2:
			if event.value:
				keyboard.press('j')
			else:
				keyboard.release('j')




