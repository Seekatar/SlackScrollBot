# SlackScrollBot
Python script to get unread counts from slack to display on [Pimoroni's Scroll Phat HD](https://shop.pimoroni.com/products/scroll-phat-hd).  It calls into Slack to get counts from your public and private channels.  Your token must be supplied.

## Setup
I use a `token.sh` script to set the token as an environment variable `SLACK_BOT_TOKEN` and then dot-source that into the shell session.

Directions for starting it on startup using `slackscrollbot` script via init.d see 
http://www.stuffaboutcode.com/2012/06/raspberry-pi-run-program-at-start-up.html