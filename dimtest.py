import os
import time
import scrollphathd as hat
from scrollphathd.fonts import font5x5

hat.rotate(180)

first_string = "12:34"
firstBrightness = 1.0
second_string = " 34"
second_brightness = 0.0

hat.set_pixel(1,6,.5)
hat.set_pixel(2,6,.5)
hat.set_pixel(3,6,.5)
hat.show()
time.sleep(2)
for i in range(99):
    firstBrightness -= .01
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
