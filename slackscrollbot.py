import os
import time
import scrollphathd as hat
from scrollphathd.fonts import font5x5
import slackstatus

hat.rotate(180)
BRIGHTNESS = .25
BRIGHTERNESS = .7

unread_count = -1

def show_unreads(prev_count,new_count):
	if prev_count < new_count:
		# flash to end
		for i in range(17):
			hat.set_pixel(i,6,BRIGHTERNESS)
			hat.show()
		for i in range(16,-1,-1):
			hat.set_pixel(i,6,0)
			hat.show()
	if new_count > 0:
		if new_count > 17:
			new_count = 17
		for i in range(new_count):
			hat.set_pixel(i,6,BRIGHTNESS)
			hat.show()
		for i in range(new_count,prev_count):
			hat.set_pixel(i,6,0)
			hat.show()

if False:
	show_unreads(0,5)
	time.sleep(.5)
	show_unreads(5,6)
	time.sleep(.5)
	show_unreads(6,9)
	time.sleep(.5)
	show_unreads(9,9)
	print "same number"
	time.sleep(2)
	show_unreads(9,6)
	print "lower"
	time.sleep(.5)
	show_unreads(6,16)
	time.sleep(.5)
	show_unreads(16,20)
	print("20")
	time.sleep(5)


if not "SLACK_BOT_TOKEN" in os.environ:
	raise "Must supply SLACK_BOT_TOKEN in envrion"

slack_bot_token = os.environ["SLACK_BOT_TOKEN"]

while True:
	hat.clear_rect(0,0,17,6)
	hat.write_string(time.strftime("%H:%M"),
		x=0,y=1,
		font=font5x5,
		brightness=BRIGHTNESS )

	now = int(time.time())
	if now % 2 == 0:
		hat.clear_rect(8,1,1,6)
	hat.show()

	if now % 60 == 0 or unread_count == -1:
		channels = slackstatus.get_channel_unread(slack_bot_token)

		unreads = [u for u in channels if u.unread > 0]
		print("There are", len(unreads), "channels with unread items")
		new_unreads = len(unreads)
		if unread_count != new_unreads and new_unreads > 0:
			print("New count is", new_unreads)
			show_unreads(unread_count, new_unreads)
		unread_count = new_unreads
	time.sleep(.5)
