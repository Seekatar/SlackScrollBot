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
from slackclient import SlackClient
from websocket import WebSocketConnectionClosedException
from processor import Runner

# pylint: disable=W0703

class ChannelType(Enum):
    """ Type of channel
    """
    PUBLIC = 1
    PRIVATE = 2
    CONVERSATION = 3

class Channel:
    """ Channel object
    """
    def __init__(self, name, channel_type, unread, channel_id):
        self.channel_id = channel_id
        self.name = name
        self.channel_type = channel_type
        self.unread = unread
    def __str__(self):
        return "%s %s %d" % (self.name, self.channel_type, self.unread)

class SlackPoller(Runner):
    """ Background thread to do polling to Slack
    """

    def __init__(self, slack_bot_token: str, poll_rate: int = 10, verbose=False):
        super(SlackPoller, self).__init__("SlackPoller")
        self.slack_bot_token = slack_bot_token
        self.slack_client = None
        self.lock = threading.Lock()
        self.unread_count = 0
        self.verbose = verbose
        self.channel_counts = {}
        self.user_id = None
        self.delay = poll_rate
        self.reconnects = 0

    def __check_result__(self, result):
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

    def __set_unreads__(self):
        unreads = 0
        for channel in self.channel_counts.values():
            if self.verbose and channel.unread != 0:
                print(channel.unread, "unread for", channel.name)
            unreads += channel.unread
        with self.lock:
            self.unread_count = unreads
        print("New unread count is", unreads)

    def __reconnect__(self):
        time.sleep(self.reconnects)
        self.setup()
        self.reconnects += 1

    def setup(self):
        self.slack_client = SlackClient(self.slack_bot_token)
        connected = False
        for i in range(20):
            try:
                if self.slack_client.rtm_connect(with_team_state=False):
                    connected = True
                    break
            except Exception:
                pass
            print("Try", i, "to get to Slack")
            time.sleep(5)
        if not connected:
            raise Exception("Never connected to slack after 20 tries!")

        self.__get_unread__()

        identity = self.slack_client.api_call(
            "auth.test",
            token=self.slack_client.token
        )
        self.user_id = identity["user_id"]

    def process(self):
        """ override to do work
        """
        hasError = False
        try:
            events = self.slack_client.rtm_read()
            for event in events:
                print("Got event", event["type"])
                if "unread_count_display" in event.keys():
                    ## channels = self.__get_unread__()
                    channel = self.__get_channel__(ChannelType.CONVERSATION, event)
                    print("Set count on", channel.name, "to", event["unread_count_display"])
                    channel.unread = event["unread_count_display"]
                    self.__set_unreads__()
                elif event["type"] == "message" and not "subtype" in event.keys() \
                        and not "edit" in event.keys() \
                        and event["user"] != self.user_id:
                    channel = self.__get_channel__(ChannelType.CONVERSATION, event)
                    print("Added 1 to ", channel.name)
                    channel.unread += 1
                    self.__set_unreads__()
            time.sleep(1)
        except ConnectionAbortedError as abort_exception:
            hasError = True
            print("Lost connection, retrying", abort_exception)
            self.__reconnect__()
        except WebSocketConnectionClosedException as conn_exception:
            hasError = True
            print("Socket closed, retrying", conn_exception)
            self.__reconnect__()
        except Exception as exception:
            hasError = True
            if "event" in dir():
                print("Exception in run thread on event", event, exception, type(exception))
            else:
                print("Exception in run thread", exception, type(exception))
            traceback.print_tb(sys.exc_info()[2])

        return self.delay,hasError

    def __get_channel__(self, channel_type, event):
        """ get the channel, adding it if needed
        """
        channel_id = event["channel"]
        if channel_id in self.channel_counts.keys():
            return self.channel_counts[channel_id]
        else:
            print("Adding on-the-fly for", event)
            new_channel = Channel("Added one", channel_type, 0, channel_id)
            self.channel_counts[channel_id] = new_channel
            return new_channel

    def __get_unread__(self):
        """ get the channels with unread counts
        """
        for i in range(10):
            try:
                public_channels = self.slack_client.api_call(
                    "channels.list",
                    exclude_archived="true",
                    exclude_members="true"
                )
                break
            except Exception:
                print("Exception", i, "trying to get to Slack")
                time.sleep(3)

        self.__check_result__(public_channels)
        my_channels = [x for x in public_channels['channels'] if x['is_member']]
        for y in my_channels:
            channel = self.slack_client.api_call(
                "channels.info",
                channel=y["id"]
            )
            self.__check_result__(channel)
            self.channel_counts[y["id"]] = Channel(y["name"], ChannelType.PUBLIC,
                                                   channel["channel"]["unread_count_display"],
                                                   y["id"])

        private_channels = self.slack_client.api_call(
            "groups.list",
            exclude_archived="true",
            exclude_members="true"
        )
        self.__check_result__(private_channels)
        my_channels = [x for x in private_channels['groups']]
        for channel in my_channels:
            if channel["is_mpim"]: # multi-person IM mpdm-<anem>--<name>-1
                name = ", ".join([q for q in channel["name"].split("-")
                                  if q != 'mpdm' and len(q) > 1])
                self.channel_counts[channel["id"]] = Channel(name, ChannelType.CONVERSATION,
                                                             channel["unread_count_display"],
                                                             channel["id"])
            else:
                self.channel_counts[channel["id"]] = Channel(channel["name"], ChannelType.PRIVATE,
                                                             channel["unread_count_display"],
                                                             channel["id"])
        self.__set_unreads__()

if __name__ == "__main__":
    # pylint: disable=C0103
    key = os.environ["SLACK_BOT_TOKEN"]
    sp = SlackPoller(key, True)
    sp.setup()
    sp.process()
    print("Current count is", sp.get_unread_count())
    print("All done")
