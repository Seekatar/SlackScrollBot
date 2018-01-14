#! /usr/bin/python
import os
import time
import scrollphathd as hat
from scrollphathd.fonts import font5x5
from processor import Processor
from slackstatus import SlackPoller
from current_weather import CurrentWeather

hat.rotate(180)
BRIGHTNESS = .25
BRIGHTERNESS = .7

def fade_text(curr_text: str, next_text: str, fade_time: int):
    """ fade from one text to another
    """
    curr_brightness = BRIGHTNESS
    second_brightness = 0
    sleep_time = fade_time / 100.0
    step = BRIGHTNESS / 100.0

    for i in range(100):
        curr_brightness -= step
        second_brightness += step
        if curr_brightness < second_brightness:
            hat.write_string(curr_text, brightness=curr_brightness, y=1, font=font5x5)
            hat.write_string(next_text, brightness=second_brightness, y=1, font=font5x5)
        else:
            hat.write_string(curr_text, brightness=second_brightness, y=1, font=font5x5)
            hat.write_string(next_text, brightness=curr_brightness, y=1, font=font5x5)
        hat.show()
        time.sleep(sleep_time)

def show_unreads(prev_count, new_count):
    """ show the unread count along the bottom
    """
    if prev_count < new_count:
        # flash to end
        for i in range(17):
            hat.set_pixel(i, 6, BRIGHTERNESS)
            hat.show()
        for i in range(16, -1, -1):
            hat.set_pixel(i, 6, 0)
            hat.show()
    if new_count > 17:
        new_count = 17
    for i in range(new_count):
        hat.set_pixel(i, 6, BRIGHTNESS)
        hat.show()
    for i in range(new_count-1, prev_count):
        hat.set_pixel(i, 6, 0)
        hat.show()

def get_time_str():
    time_string = time.strftime("%I:%M")
    if time_string[0] == '0':
        time_string = time_string[1:]
    return time_string

def show_time():
    """ show the time
    """
    hat.clear_rect(0, 0, 17, 6)
    x_coord = 0
    time_string = get_time_str()
    if len(time_string) == 4:
        x_coord = 4
    hat.write_string(time_string,
                     x=x_coord, y=1,
                     font=font5x5,
                     brightness=BRIGHTNESS)

    now = int(time.time())

    # make colon flash
    if now % 2 == 0:
        hat.clear_rect(8, 1, 1, 5)
    hat.show()
    return time_string

def get_temp_str(temperature):
    return " "+int(temperature)

def show_temp(temperature):
    """ show the current temperature
    """
    hat.clear_rect(0, 0, 17, 6)
    hat.write_string(get_temp_str(temperature),
                     y=1,
                     font=font5x5,
                     brightness=BRIGHTNESS)

    return temperature

def main():
    """ mainline
    """
    unread_count = -1
    verbose = True

    if not "SLACK_BOT_TOKEN" in os.environ:
        raise "Must supply SLACK_BOT_TOKEN in envrion"

    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]

    if not "SLACK_BOT_WEATHER_KEY" in os.environ:
        raise "Must supply SLACK_BOT_WEATHER_KEY in envrion"

    weather_key = os.environ["SLACK_BOT_WEATHER_KEY"]

    cw = CurrentWeather("30022", weather_key, 60)
    poller = SlackPoller(slack_bot_token, verbose)

    processor = Processor(verbose)
    processor.add_processor(cw)
    processor.add_processor(poller)

    processor.start()

    showing_time = True
    prev_string = ""
    linger_time = 10
    last_change_time = time.time()
    try:
        while True:

            if time.time() > last_change_time + linger_time:
                if showing_time:
                    next_string = get_temp_str(cw.get_temperature())
                else:
                    next_string = get_time_str()

                showing_time = not showing_time
                fade_text(prev_string, next_string, 1)
                last_change_time = time.time()

            if showing_time:
                prev_string = show_time()
            else:
                prev_string = show_temp(cw.get_temperature())

            new_unreads = poller.get_unread_count()
            if unread_count != new_unreads:
                print("New count for UI is", new_unreads)
                show_unreads(unread_count, new_unreads)
            unread_count = new_unreads
            time.sleep(.5)
    except KeyboardInterrupt:
        processor.stop()

if __name__ == "__main__":

    debug = False
    if debug:
        show_unreads(0, 5)
        time.sleep(.5)
        show_unreads(5, 6)
        time.sleep(.5)
        show_unreads(6, 9)
        time.sleep(.5)
        show_unreads(9, 9)
        print("same number")
        time.sleep(2)
        show_unreads(9, 6)
        print("lower")
        time.sleep(.5)
        show_unreads(6, 16)
        time.sleep(.5)
        show_unreads(16, 20)
        print("20")
        time.sleep(5)

    main()
    print("All done")
