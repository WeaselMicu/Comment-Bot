#-*- coding: utf-8 -*-

#===============Image Module=======================
#Since Twitter allows only 140 character limit, we use an image in the reply
#This module allows wrapping the text so that is can be converted to an image properly

# Image libraries
import PIL, textwrap
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import ConfigParser
import time, datetime, sys, os, re, random

# Do not change these two lines.
config = ConfigParser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + "/config/bot.conf")

# Do not edit this section. This part reads the configuration information
# determined in the bot.conf file.
font_path = config.get("TextConfig", "font_path")
Font = config.get("TextConfig", "font")
font_size = config.get("TextConfig", "font_size")
font_color = config.get("TextConfig", "font_color")
watermark_logo = config.get("BackgroundConfig", "watermark_logo")
background_color = config.get("BackgroundConfig", "background_color")

# Do not change this.
offset = 1

# This wrap_text function should not be edited.
def wrap_text(wrap,font,draw):
  margin = offset = 20
  for line in wrap:
    draw.text((margin,offset),line,font=font,fill=font_color)
    offset += font.getsize(line)[1]

#This module takes in the message and converts it to an image. It has internal helper module which help in
def create_image(message, user, location):

	font = ImageFont.truetype(os.path.join(font_path, Font), int(font_size))
	margin = offset = 20

	if watermark_logo:
		wrap = textwrap.wrap(message,width=50)
	else:
		# No logo then make the lines a bit wider
		wrap = textwrap.wrap(message,width=55)

	line_height = font.getsize(wrap[0])[1]
	print "line height: " + str(line_height)
	print wrap

	# Make the image double the size to start with, so that we can apply a anti-alias function when we scale down. Text looks better (I think)
	# enough space for "margin" at the top and bottom and also a .5 margin between the comment and the attribution
	img=Image.new("RGBA", (900,int(2.5*margin+line_height*(len(wrap)+1))),(background_color))
	draw = ImageDraw.Draw(img)
	wrap_text(wrap,font,draw)
	draw.text((margin,int(1.5*margin+line_height*len(wrap))), u" \u2014 "  + user + ", " + location,font=font,fill=font_color)

	if watermark_logo:
		# If there's a logo file provided then make space for it and paste it into the upper right corner.
		logo = Image.open(watermark_logo)
		box = (800, 0, 900, 100)
		img.paste(logo, box)

	img_resized = img.resize((450, int(2.5*.5*margin+(line_height * .5)*(len(wrap)+1))), Image.ANTIALIAS)
	draw = ImageDraw.Draw(img_resized)
	img_resized.save("test_tweet_reply.png")

# you can put your own message to test here. Do not `return` at the end of lines. Our `wrap_text` function will wrap for you when making the image.
message = "The three scores are weighted in a linear combination in order to calculate an overall 'anecbotal' score for each comment. The weights are Length: 0.25, Readability: 0.25, Personal Experience: 0.50 in order to prioritize comments that have substantial personal experience scores. The final comment tweeted out is a random selection from the top 3 comments on an article according to the ranking."

# fake twitter username and location. Only required for this testing script.
user = "@spam&eggs"
location = "Camelot"

# call the function to make it go!
create_image(message, user, location)
