import os
import time
import scrollphathd as hat
from scrollphathd.fonts import font5x5

hat.rotate(180)

BRIGHTNESS = .25
BRIGHTERNESS = .7

def fade_text(curr_text: str, next_text: str, fade_time: int):
    """ fade from one text to another
    """
    curr_brightness = BRIGHTNESS
    second_brightness = 0
    sleep_time = fade_time / 100.0
    step = .01
    range_limit = int(BRIGHTNESS / step)
    sleep_time = fade_time / range_limit

    for i in range(range_limit):
        curr_brightness -= step
        if curr_brightness < 0:
            curr_brightness = 0
        second_brightness += step

        if curr_brightness < second_brightness:
            hat.write_string(curr_text, brightness=curr_brightness, y=1, font=font5x5)
            hat.write_string(next_text, brightness=second_brightness, y=1, font=font5x5)
        else:
            hat.write_string(next_text, brightness=second_brightness, y=1, font=font5x5)
            hat.write_string(curr_text, brightness=curr_brightness, y=1, font=font5x5)
        hat.show()
        time.sleep(sleep_time)


first_string = "12:34"
firstBrightness = .25
second_string = " 34"
second_brightness = 0.0

hat.set_pixel(0,6,.5)
hat.set_pixel(1,6,.5)
hat.set_pixel(2,6,.5)
hat.set_pixel(3,6,.5)
hat.show()

fade_text(first_string, second_string, 1)
time.sleep(3)
fade_text(second_string, first_string, 1)
time.sleep(3)

for i in range(25):
    firstBrightness -= .01
    if firstBrightness < 0:
        break
    second_brightness += .01
    if firstBrightness < second_brightness:
        hat.write_string(first_string, brightness=firstBrightness, y=1,font=font5x5)
        hat.write_string(second_string, brightness=second_brightness, y=1,font=font5x5)
    else:
        hat.write_string(second_string, brightness=second_brightness, y=1,font=font5x5)
        hat.write_string(first_string, brightness=firstBrightness, y=1,font=font5x5)
    hat.show()
    time.sleep(.01)

time.sleep(10)
