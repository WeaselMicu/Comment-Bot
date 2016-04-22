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
config.read(os.path.dirname(os.path.abspath(__file__)) + "/bot.conf")

# Do not edit this section. This part reads the configuration information
# determined in the bot.conf file.
font_path = config.get("TextConfig", "font_path")
Font = config.get("TextConfig", "font")
font_size = config.get("TextConfig", "font_size")
font_color = config.get("TextConfig", "font_color")
background_color = config.get("BackgroundConfig", "background_color")
watermark_logo = config.get("BackgroundConfig", "watermark_logo")

# Do not change this.
offset = 1

# This wrap_text function should not be edited.
def wrap_text(wrap,font,draw):
  margin = offset = 20
  margin = 20
  for line in wrap:
    draw.text((margin,offset),line,font=font,fill=font_color)
    offset += font.getsize(line)[1]

#This module takes in the message and converts it to an image. It has internal helper module which help in
def create_image(message, user, location):
  wrap = textwrap.wrap(message,width=50) # responds to number of characters in a line. Will wrap text after 50 characters.
  print(wrap)
  font = ImageFont.truetype(os.path.join(font_path, Font), int(font_size), encoding='unic') # Need to make use configured fontsize!!
  logo = Image.open("CJ_logo.png")
  # 70 = 35 space at top and bottom; 17 is line height. Correct way would be calculate line height based on font size
  # replace 70 with 140, and 17 by 34. 17 determins the leading. MIght be different for different fonts.
  img = Image.new("RGBA", (900,140+34*len(wrap)),background_color)
  draw = ImageDraw.Draw(img)
  wrap_text(wrap,font,draw)
  margin = offset = 20
  # Define the box which should be the position of the logo on your canvas. Here is Top left corner (800 across; 0 down) and bottom-right corner
  # 900 across; 100 down. My image dimension is 100 x 100 pixels. )
  box = (800, 0, 900, 100)
  img.paste(logo, box)
  draw.text((margin,offset+10+38*len(wrap))," -- "  + user + ", " + location,font=font,fill=font_color) # Make into 'm' dash, not double dash #Values orig (margin, offset+10+17*len(wrap))
  img_resized = img.resize((450, 70+17*len(wrap)), Image.ANTIALIAS)
  draw = ImageDraw.Draw(img_resized)
  img_resized.save("test_TextConfig_resized.png")


# you can put your own message to test here. Do not `return` at the end of lines. Our `wrap_text` function will wrap for you.
message = "The three scores are weighted in a linear combination in order to calculate an overall 'anecbotal' score for each comment. The weights are Length: 0.25, Readability: 0.25, Personal Experience: 0.50 in order to prioritize comments that have substantial personal experience scores. The final comment tweeted out is a random selection from the top 3 comments on an article according to the ranking."

# fake twitter username and location. Only required for this testing script.
user = "@spam&eggs"
location = "Camelot"

# call the function to make it go!
create_image(message, user, location)
