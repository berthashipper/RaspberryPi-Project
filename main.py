from sense_hat import SenseHat
import time

sense = SenseHat()

""" sense.show_message(
    "what's up?",
    scroll_speed=0.05,
    text_colour=[255, 255, 0],
    back_colour=[0, 100, 100]
) """

sense.clear()

Y = [0, 100, 200]
B = [0, 0, 0]

""" smiley1 = [
B, B, Y, Y, Y, Y, B, B,
B, Y, B, B, B, B, Y, B,
Y, B, Y, B, B, Y, B, Y,
Y, B, B, B, B, B, B, Y,
Y, B, Y, B, B, Y, B, Y,
Y, B, B, Y, Y, B, B, Y,
B, Y, B, B, B, B, Y, B,
B, B, Y, Y, Y, Y, B, B
] """

#sense.set_pixels(smiley1)


smiley_open = [
B,B,Y,Y,Y,Y,B,B,
B,Y,B,B,B,B,Y,B,
Y,B,Y,B,B,Y,B,Y,
Y,B,B,B,B,B,B,Y,
Y,B,Y,B,B,Y,B,Y,
Y,B,B,Y,Y,B,B,Y,
B,Y,B,B,B,B,Y,B,
B,B,Y,Y,Y,Y,B,B
]

smiley_wink = [
B,B,Y,Y,Y,Y,B,B,
B,Y,B,B,B,B,Y,B,
Y,B,B,B,B,Y,B,Y,
Y,B,B,Y,Y,B,B,Y,
Y,B,Y,B,B,Y,B,Y,
Y,B,B,Y,Y,B,B,Y,
B,Y,B,B,B,B,Y,B,
B,B,Y,Y,Y,Y,B,B
]

sense.set_pixels(smiley_wink)

""" # Animate!
while True:
    sense.set_pixels(smiley_open)
    time.sleep(0.5)
    sense.set_pixels(smiley_wink)
    time.sleep(0.2) """