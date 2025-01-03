# SlackScrollBot

These are some Python scripts to get unread counts from Slack and temperature from openweathermap to display on [Pimoroni's Scroll Phat HD](https://shop.pimoroni.com/products/scroll-phat-hd).

> NOTE: The `RPi` branch has a variation currently running on the Raspberry Pi Zero W.

## Setup

Install these dependent Python modules

```bash
sudo apt-get install libopenblas-dev
pip3 install scrollphathd
pip3 install slackclient
pip3 install websocket-client # for slack client
pip3 install requests         # for openweathermap
```

Create the log folder and file

```bash
sudo mkdir /var/slackscrollbot
sudo chmod 0777 /var/slackscrollbot
touch /var/slackscrollbot/log.txt
```

## Running it

After updating the Pi Zero W to Pi OS update of January 2025, you must run in a Python vm. I created one for my user on the Pi Zero W. To run it you have to switch to the vm.

```bash
. ./token.sh                         # sets the environment variables
. /home/seekatar/.env/bin/activate   # activates the virtual environment
python3 ./slackscrollbot.py --logLevel=Debug
deactivate                           # deactivates the virtual environment
```

I use a `token.sh` script to set the tokens as an environment variables `SLACK_BOT_TOKEN` (optional) and `SLACK_BOT_WEATHER_KEY` (required) and then dot-source that into the shell session.

I used `/etc/rc.local` to run the app on startup. [Five ways to run a program at startup](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/)

## Features

* Shows count of unread Slack messages in a line along the bottom of the display, if configured
* Shows time with blinking colon (mainly from sample code)
* Shows temperature
* Fades between time and temperature
* Blinks a pixel to indicate the background thread that gets counts and temp is still running
* [Logging](https://docs.python.org/3/howto/logging.html#logging-basic-tutorial)

## Testing

```bash
(cd /home/seekatar/SlackScrollBot/ && . ./token.sh && . /home/seekatar/.env/bin/activate && python3 ./slackscrollbot.py --logLevel=Debug 2>&1 > /var/slackscrollbot/std.log ) &
tail /var/slackscrollbot/log.txt -f
killall -s 2 python3

```

## Docker

Used VSCode Ctrl+Shift+P Docker Add file to add Dockerfile

```bash
pip freeze > requirements.txt
```
