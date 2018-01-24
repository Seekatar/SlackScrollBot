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
    key = os.environ["SLACK_BOT_WEATHER_KEY"]
    cw = current_weather.CurrentWeather("30022", key, 60)

    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    slack_poller = slackstatus.SlackPoller(slack_bot_token)

    processor = processor.Processor(True)

    processor.add_processor(cw)
    processor.add_processor(slack_poller)
    processor.add_processor(Thrower())

    processor.start()

    print("Testing, press a key to stop...")
    try:
        while True:
            total = slack_poller.get_unread_count()
            print("[", processor.get_loop_count(), "] Total unreads",
                  total, "temp", cw.get_temperature())
            time.sleep(5)
    except KeyboardInterrupt:
        processor.stop()

    print("All done")
