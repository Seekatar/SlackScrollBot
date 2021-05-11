# SlackScrollBot

These are some Python scripts to get unread counts from Slack and temperature from openweathermap to display on [Pimoroni's Scroll Phat HD](https://shop.pimoroni.com/products/scroll-phat-hd).

## Setup

Install these dependent Python modules

```bash
sudo apt-get install python3-scrollphathd
sudo apt-get install python3-requests
sudo apt install python3-pip
sudo apt install python3-websocket
sudo pip3 install slackclient
```

I use a `token.sh` script to set the tokens as an environment variables `SLACK_BOT_TOKEN` (optional) and `SLACK_BOT_WEATHER_KEY` (required) and then dot-source that into the shell session.

~~Directions for starting it on startup using `slackscrollbot` script via init.d see
[here](http://www.stuffaboutcode.com/2012/06/raspberry-pi-run-program-at-start-up.html)~~

I used /etc/rc.local instead. [Five ways to run a program at startup](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/)

## Features

* Shows count of unread Slack messages in a line along the bottom of the display, if configured
* Shows time with blinking colon (mainly from sample code)
* Shows temperature
* Fades between time and temperature
* Blinks a pixel to indicate the background thread that gets counts and temp is still running
* [Logging](https://docs.python.org/3/howto/logging.html#logging-basic-tutorial)

## Testing

```bash
(cd /home/pi/SlackScrollBot/ && . ./token.sh && python3 ./slackscrollbot.py --logLevel=Debug 2>&1 > /var/slackscrollbot/std.log ) &
tail /var/slackscrollbot/log.txt -f
killall -s 2 python3

```
