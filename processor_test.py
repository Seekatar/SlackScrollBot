# pylint: disable=C0103,c0111
import os
import time
import processor
import slackstatus
import current_weather

class Thrower(processor.Runner):

    def __init__(self):
        super(Thrower,self).__init__("Thrower")

    def process(self):
        raise Exception("ow ow ow")

if __name__ == "__main__":
    if "SLACK_BOT_TOKEN" in os.environ:
        slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    else:
        slack_bot_token = None

    if not "SLACK_BOT_WEATHER_KEY" in os.environ:
        raise ValueError("Must supply SLACK_BOT_WEATHER_KEY in os.envrion")

    key = os.environ["SLACK_BOT_WEATHER_KEY"]
    cw = current_weather.CurrentWeather("30022", key, 60)

    if slack_bot_token:
        slack_poller = slackstatus.SlackPoller(slack_bot_token)
    else:
        slack_poller = None

    processor = processor.Processor(True)

    processor.add_runner(cw)
    if slack_bot_token:
        processor.add_runner(slack_poller)
    processor.add_runner(Thrower())

    processor.start()

    print("Testing, press a key to stop...")
    try:
        while True:
            if slack_poller:
                total = slack_poller.get_unread_count()
            else:
                total = 0
            print(f"[{processor.get_loop_count()}] Total unreads {total} temp = {cw.get_temperature()}")
            time.sleep(5)
    except KeyboardInterrupt:
        processor.stop()

    print("All done")
