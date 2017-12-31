# To get token
# https://api.slack.com/custom-integrations/legacy-tokens

import os
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
    channels = get_channel_unread(slack_bot_token)

    unreads = [u for u in channels if u.unread > 0]
    if len(unreads):
        print("There are",len(unreads),"channels with unread items")
        for c in unreads:
            print(c)
    else:
        print("No unreads")

def get_channel_unread(slack_bot_token):
    """ get the channels with unread counts
    """
    slack_client = SlackClient(slack_bot_token)

    channels = []
    public_channels = slack_client.api_call(
        "channels.list",
        exclude_archived="true"
    )
    my_channels = [x for x in public_channels['channels'] if x['is_member']]
    for y in my_channels:
        channel = slack_client.api_call(
            "channels.info",
            channel=y["id"]
        )
        channels.append(Channel(y["name"], ChannelType.PUBLIC, channel["channel"]["unread_count"]))

    private_channels = slack_client.api_call(
        "groups.list",
        exclude_archived="true",
        exclude_members="true"
    )
    my_channels = [x for x in private_channels['groups']]
    for y in my_channels:
        if y["is_mpim"]: # multi-person IM mpdm-<anem>--<name>-1
            name = ", ".join([y for y in y["name"].split("-") if y != 'mpdm' and len(y) > 1])
            channels.append(Channel(name, ChannelType.CONVERSATION, y["unread_count"]))
        else:
            channels.append(Channel(y["name"], ChannelType.PRIVATE, y["unread_count"]))

    return channels

if __name__ == "__main__":
    main()
    print("All done")