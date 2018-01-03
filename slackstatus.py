"""
To get legacy token
https://api.slack.com/custom-integrations/legacy-tokens
"""

import os
import time
import sys
import threading
sys.path.append("/home/pi/.local/lib/python2.7/site-packages")
# print sys.path
from enum import Enum
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
    def __init__(self, name, channel_type, unread):
        self.name = name
        self.channel_type = channel_type
        self.unread = unread
    def __str__(self):
        return "%s %s %d" % (self.name, self.channel_type, self.unread)

def main():
    """ mainline
    """
    if not "SLACK_BOT_TOKEN" in os.environ:
        raise "Must supply SLACK_BOT_TOKEN in envrion"

    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    waitForIt(slack_bot_token)
    channels = get_channel_unread(slack_bot_token)

    unreads = [u for u in channels if u.unread > 0]
    if unreads:
        print("There are", len(unreads), "channels with unread items")
        total = 0
        for c in unreads:
            print(c)
            total += c.unread
        print("With a total of",total)
    else:
        print("No unreads")

def checkResult(result):
    if result["ok"]:
        return
    else:
        raise "Error from Slack: "+result["error"]

class runner(threading.Thread):

    def __init__(self,slack_client):
        super(runner,self).__init__()
        self.slack_client = slack_client
        self.lock = threading.Lock()
        self.unread_count = 0

    def get_unread_count(self):
        ret = 0
        with self.lock:
            ret = self.unread_count
        return ret

    def run(self):
        while True:
            events = self.slack_client.rtm_read()
            for l in events:
                if not (l["type"] in ["presence_change","reconnect_url","hello"]):
                    channels = self.__getUnread()
                    unreadCnt = 0
                    for c in channels:
                        unreadCnt += c.unread
                    with self.lock:
                        self.unread_count = unreadCnt
            time.sleep(1)

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
            except:
                print("Exception", i, "trying to get to Slack")
                time.sleep(3)

        checkResult(public_channels)
        my_channels = [x for x in public_channels['channels'] if x['is_member']]
        for y in my_channels:
            channel = self.slack_client.api_call(
                "channels.info",
                channel=y["id"]
            )
            checkResult(channel)
            channels.append(Channel(y["name"], ChannelType.PUBLIC, channel["channel"]["unread_count"]))

        private_channels = self.slack_client.api_call(
            "groups.list",
            exclude_archived="true",
            exclude_members="true"
        )
        checkResult(private_channels)
        my_channels = [x for x in private_channels['groups']]
        for y in my_channels:
            if y["is_mpim"]: # multi-person IM mpdm-<anem>--<name>-1
                name = ", ".join([q for q in y["name"].split("-") if q != 'mpdm' and len(q) > 1])
                channels.append(Channel(name, ChannelType.CONVERSATION, y["unread_count"]))
            else:
                channels.append(Channel(y["name"], ChannelType.PRIVATE, y["unread_count"]))

        return channels

def waitForIt(slack_bot_token):
    """ get the channels with unread counts
    """
    slack_client = SlackClient(slack_bot_token)
    if slack_client.rtm_connect(with_team_state=False):
        thd = runner(slack_client)
        thd.start()

        for i in range(1000):
            print(i,thd.get_unread_count())
            time.sleep(1)
    else:
        print("Connection Failed")


def get_channel_unread(slack_bot_token):
    """ get the channels with unread counts
    """
    slack_client = SlackClient(slack_bot_token)

    channels = []
    for i in range(10):
        try:
            public_channels = slack_client.api_call(
                "channels.list",
                exclude_archived="true"
            )
        except:
            print("Exception", i, "trying to get to Slack")
            time.sleep(3)

    checkResult(public_channels)
    my_channels = [x for x in public_channels['channels'] if x['is_member']]
    for y in my_channels:
        channel = slack_client.api_call(
            "channels.info",
            channel=y["id"]
        )
        checkResult(channel)
        channels.append(Channel(y["name"], ChannelType.PUBLIC, channel["channel"]["unread_count"]))

    private_channels = slack_client.api_call(
        "groups.list",
        exclude_archived="true",
        exclude_members="true"
    )
    checkResult(private_channels)
    my_channels = [x for x in private_channels['groups']]
    for y in my_channels:
        if y["is_mpim"]: # multi-person IM mpdm-<anem>--<name>-1
            name = ", ".join([q for q in y["name"].split("-") if q != 'mpdm' and len(q) > 1])
            channels.append(Channel(name, ChannelType.CONVERSATION, y["unread_count"]))
        else:
            channels.append(Channel(y["name"], ChannelType.PRIVATE, y["unread_count"]))

    return channels

if __name__ == "__main__":
    main()
    print("All done")
