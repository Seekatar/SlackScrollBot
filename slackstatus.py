"""
To get legacy token
https://api.slack.com/custom-integrations/legacy-tokens
"""

import os
import time
import sys
import threading
import traceback
from enum import Enum

sys.path.append("/home/pi/.local/lib/python2.7/site-packages")
from slackclient import SlackClient

class ChannelType(Enum):
    """ Type of channel
    """
    PUBLIC = 1
    PRIVATE = 2
    CONVERSATION = 3

class Channel:
    """ Channel object
    """
    def __init__(self, name, channel_type, unread, id):
        self.id = id
        self.name = name
        self.channel_type = channel_type
        self.unread = unread
    def __str__(self):
        return "%s %s %d" % (self.name, self.channel_type, self.unread)

class SlackPoller(threading.Thread):
    """ Background thrad to do polling to Slack
    """
    
    def __init__(self,slack_client,verbose=False):
        super(SlackPoller, self).__init__()
        self.slack_client = slack_client
        self.lock = threading.Lock()
        self.unread_count = 0
        self.verbose = verbose
        self.channel_counts = {}

    def checkResult(self,result):
        if result["ok"]:
            return
        else:
            if result["error"] == "ratelimited":
                time.sleep(1)
            raise Exception("Error from Slack: "+result["error"])

    def get_unread_count(self):
        """ get the total unreads
        """
        ret = 0
        with self.lock:
            ret = self.unread_count
        return ret

    def run(self):
        self.__getUnread()
        while True:
            try:
                events = self.slack_client.rtm_read()
                for event in events:
                    if not (event["type"] in ["presence_change","reconnect_url", "hello"]):
                        channels = self.__getUnread()
                        unreads = 0
                        for channel in channels:
                            if self.verbose:
                                print(channel.name, "has", channel.unread, "unreads")
                            unreads += channel.unread
                        with self.lock:
                            self.unread_count = unreads
                time.sleep(1)
            except Exception as e:
                print("Exception in run thread", e)
                traceback.print_tb(sys.exc_info()[2])

    def __getUnread(self):
        """ get the channels with unread counts
        """
        channels = []
        for i in range(10):
            try:
                public_channels = self.slack_client.api_call(
                    "channels.list",
                    exclude_archived="true"
                )
            except Exception:
                print("Exception", i, "trying to get to Slack")
                time.sleep(3)

        self.checkResult(public_channels)
        my_channels = [x for x in public_channels['channels'] if x['is_member']]
        for y in my_channels:
            channel = self.slack_client.api_call(
                "channels.info",
                channel=y["id"]
            )
            self.checkResult(channel)
            channels.append(Channel(y["name"], ChannelType.PUBLIC,
                                    channel["channel"]["unread_count_display"]))

        private_channels = self.slack_client.api_call(
            "groups.list",
            exclude_archived="true",
            exclude_members="true"
        )
        self.checkResult(private_channels)
        my_channels = [x for x in private_channels['groups']]
        for y in my_channels:
            if y["is_mpim"]: # multi-person IM mpdm-<anem>--<name>-1
                name = ", ".join([q for q in y["name"].split("-") if q != 'mpdm' and len(q) > 1])
                channels.append(Channel(name, ChannelType.CONVERSATION, y["unread_count_display"]))
            else:
                channels.append(Channel(y["name"], ChannelType.PRIVATE, y["unread_count_display"]))

        return channels

def start_poller(slack_bot_token, verbose=False):
    """ get the channels with unread counts
    """
    slack_client = SlackClient(slack_bot_token)
    for i in range(20):
        try:
            if slack_client.rtm_connect(with_team_state=False):
                thd = SlackPoller(slack_client, verbose)
                thd.start()

                return thd
        except:
                pass
        print("Trying", i ,"to get to Slack")
    time.sleep(5)
    raise Exception("Never connected after 60 secs!")

def main():
    """ mainline
    """
    if not "SLACK_BOT_TOKEN" in os.environ:
        raise Exception("Must supply SLACK_BOT_TOKEN in envrion")

    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    thd = start_poller(slack_bot_token, True)
    while True:

        total = thd.get_unread_count()
        if total > 0:
            print("Total unreads", total)
        else:
            print("No unreads")
        time.sleep(5)


if __name__ == "__main__":
    main()
    print("All done")
