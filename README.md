# SlackScrollBot
These are some Python scripts to get unread counts from Slack and temperature from openweathermap to display on [Pimoroni's Scroll Phat HD](https://shop.pimoroni.com/products/scroll-phat-hd).

## Setup
I use a `token.sh` script to set the tokens as an environment variables `SLACK_BOT_TOKEN` and `SLACK_BOT_WEATHER_KEY` and then dot-source that into the shell session.

Directions for starting it on startup using `slackscrollbot` script via init.d see
http://www.stuffaboutcode.com/2012/06/raspberry-pi-run-program-at-start-up.html

## Features
* Shows count of unread Slack messages in a line along the bottom of the display
* Shows time with blinking colon (mainly from sample code)
* Shows temperature
* Fades between time and temparture
* Blinks a pixel to indicate the background thread that gets counts and temp is still running

[Wiki](Wiki)
