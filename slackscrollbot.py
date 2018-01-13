#! /usr/bin/python
import os
import time
import scrollphathd as hat
from scrollphathd.fonts import font5x5
import slackstatus

hat.rotate(180)
BRIGHTNESS = .25
BRIGHTERNESS = .7

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

def main():
    """ mainline
    """
    unread_count = -1

    if not "SLACK_BOT_TOKEN" in os.environ:
        raise "Must supply SLACK_BOT_TOKEN in envrion"

    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]

    poller = slackstatus.start_poller(slack_bot_token)

    try:
        while True:
            hat.clear_rect(0, 0, 17, 6)
            time_string = time.strftime("%I:%M")
            x_coord = 0
            if time_string[0] == '0':
                x_coord = 4
                time_string = time_string[1:]
            hat.write_string(time_string,
                             x=x_coord, y=1,
                             font=font5x5,
                             brightness=BRIGHTNESS)

            now = int(time.time())
            if now % 2 == 0:
                hat.clear_rect(8, 1, 1, 5)
            hat.show()

            new_unreads = poller.get_unread_count()
            if unread_count != new_unreads:
                print("New count for UI is", new_unreads)
                show_unreads(unread_count, new_unreads)
            unread_count = new_unreads
            time.sleep(.5)
    except KeyboardInterrupt:
        poller.stop()

if __name__ == "__main__":
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
