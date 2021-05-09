#! /usr/bin/python
""" main module for running slack scroll bot
"""
import os
import time
import argparse
import scrollphathd as hat
import os
import logging
from logging.handlers import RotatingFileHandler
from scrollphathd.fonts import font5x5
from processor import Processor
from slackstatus import SlackPoller
from current_weather import CurrentWeather

hat.rotate(180)
BRIGHTNESS = .25
BRIGHTERNESS = .7

def fade_text(curr_text: str, next_text: str, curr_x: int = 1, next_x: int = 1, fade_time: int = 1):
    """ fade from one text to another
    """
    curr_brightness = BRIGHTNESS
    second_brightness = 0
    step = .01
    range_limit = int(BRIGHTNESS / step)
    sleep_time = fade_time / range_limit

    # pylint: disable=W0612
    for i in range(range_limit):
        curr_brightness -= step
        if curr_brightness < 0:
            curr_brightness = 0
        second_brightness += step

        if curr_brightness < second_brightness:
            hat.write_string(curr_text, brightness=curr_brightness, x=curr_x, y=1, font=font5x5)
            hat.write_string(next_text, brightness=second_brightness, x=next_x, y=1, font=font5x5)
        else:
            hat.write_string(next_text, brightness=second_brightness, x=next_x, y=1, font=font5x5)
            hat.write_string(curr_text, brightness=curr_brightness, x=curr_x, y=1, font=font5x5)
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
    for i in range(new_count, prev_count):
        hat.set_pixel(i, 6, 0)
        hat.show()

def get_time_str():
    """ get the time, removing leading 0, calculate x
    """
    time_string = time.strftime("%I:%M")
    x_coord = 0
    if time_string[0] == '0':
        time_string = time_string[1:]
        x_coord = 4
    return time_string, x_coord

def show_time():
    """ show the time
    """
    hat.clear_rect(0, 1, 17, 5)
    time_string, x_coord = get_time_str()
    hat.write_string(time_string,
                     x=x_coord, y=1,
                     font=font5x5,
                     brightness=BRIGHTNESS)

    now = int(time.time())

    # make colon flash
    if now % 2 == 0:
        hat.clear_rect(8, 1, 1, 5)
    hat.show()
    return time_string, x_coord

def get_temp_str(temperature):
    """ get the string version of temp, and x
    """
    return " "+str(round(temperature)), 0

def show_temp(temperature):
    """ show the current temperature
    """
    hat.clear_rect(0, 1, 17, 5)
    temp_str, x_coord = get_temp_str(temperature)
    hat.write_string(temp_str,
                     y=1,
                     font=font5x5,
                     brightness=BRIGHTNESS)

    return temp_str, x_coord

def main():
    """ mainline
    """
    # unread_count = -1
    verbose = False

    if not "SLACK_BOT_TOKEN" in os.environ:
        raise "Must supply SLACK_BOT_TOKEN in envrion"

    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]

    if not "SLACK_BOT_WEATHER_KEY" in os.environ:
        raise "Must supply SLACK_BOT_WEATHER_KEY in envrion"

    parser = argparse.ArgumentParser(description="SlackScroll Bot")
    parser.add_argument('--zip',type=str,help="Zip code for temperature",default="30022")
    parser.add_argument('--slackPoll',type=int,help="Slack polling rate in seconds",default=2)
    parser.add_argument('--weatherPoll',type=int,help="Weather rate in seconds",default=60)
    parser.add_argument('--linger',type=int,help="How long to show an item in seconds",default=1)
    args = parser.parse_args()

    weather_key = os.environ["SLACK_BOT_WEATHER_KEY"]

    handler = RotatingFileHandler("/var/slackscrollbot/log.txt", maxBytes=5000000, backupCount=3)
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',handlers=[handler],level=logging.INFO)
    logging.info("Scrollbot starting with config:")
    logging.info("  zip         = %s", args.zip)
    logging.info("  slackPoll   = %d", args.slackPoll)
    logging.info("  weatherPoll = %d", args.weatherPoll)
    logging.info("  linger      = %d", args.linger)

    weather = CurrentWeather(args.zip, weather_key, args.weatherPoll)
    # poller = SlackPoller(slack_bot_token, args.slackPoll, verbose)

    processor = Processor(verbose)
    processor.add_runner(weather)
    # processor.add_runner(poller)
    processor.start()

    showing_time = True
    prev_string = ""
    prev_x = 1
    linger_time = args.linger
    last_change_time = time.time()
    last_loop_count = 0
    loop_brightness = 1

    try:
        errorTime = None
        while True:

            if time.time() > last_change_time + linger_time:
                if showing_time:
                    next_string, next_x = get_temp_str(weather.get_temperature())
                else:
                    next_string, next_x = get_time_str()

                showing_time = not showing_time
                fade_text(prev_string, next_string, prev_x, next_x, 1)
                last_change_time = time.time()

            if showing_time:
                prev_string, prev_x = show_time()
            else:
                prev_string, prev_x = show_temp(weather.get_temperature())

            # new_unreads = poller.get_unread_count()
            # if unread_count != new_unreads:
            #     print("New count for UI is", new_unreads)
            #     show_unreads(unread_count, new_unreads)
            # unread_count = new_unreads
            # time.sleep(.5)
            loop_count = processor.get_loop_count()

            if processor.has_error():
                if not errorTime:
                    errorTime = time.time()
                if time.time() > errorTime + 120:
                    logging.fatal('Rebooting since has errors for 2 minutes')
                    os.system('sudo reboot')
                errorPixel = BRIGHTNESS
            else:
                errorTime = None
                errorPixel = 0

            hat.set_pixel(1, 0, errorPixel)
            hat.show()

            if loop_count != last_loop_count:
                loop_brightness = int(not loop_brightness)
                last_loop_count = loop_count
                hat.set_pixel(0, 0, BRIGHTNESS*loop_brightness)
                hat.show()

    except KeyboardInterrupt:
        processor.stop()

if __name__ == "__main__":

    DEBUG = False
    if DEBUG:
        show_unreads(0, 5)
        time.sleep(.5)
        show_unreads(5, 1)
        print("5 to 1")
        time.sleep(3)
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
        exit(0)

    main()
    print("All done")
