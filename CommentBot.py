# General Imports
import time, datetime, sys, os, re, random
import json, csv
import requests
import ConfigParser
from bs4 import BeautifulSoup

# Import tweepy
import tweepy

# Scoring methods
from TextUtils import calcPersonalXPScore, calcReadability, calcLength, escape_string

# Image libraries
import PIL, textwrap
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

# Exceptions
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.exceptions import ReadTimeoutError

# Load bot.conf file
config = ConfigParser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + "/config/anecbotalNYT.conf")

#  Twitter keys, message, and bot name:
consumer_key = config.get("TwitterConfig", "consumer_key")
consumer_secret = config.get("TwitterConfig", "consumer_secret")
access_token = config.get("TwitterConfig", "access_token")
access_token_secret = config.get("TwitterConfig", "access_token_secret")
bot_name =  config.get("TwitterConfig", "bot_name")

# Read comments platform info (eg NYT or Disqus keys)
API = config.get("CommentConfig", "API")
comments_keys = json.loads(config.get("CommentConfig", "comments_keys"))
filter_object_ = config.get("CommentConfig", "filter_object")
min_comments_found = config.get("CommentConfig", "min_comments_found")
news_org_url = json.loads(config.get("CommentConfig", "news_org_url"))

# Disqus-only things
forum = config.get("CommentConfig", "disqus_forum")
reputation = config.get("CommentConfig", "reputation")

# Configuring text analysis weights
PersonalXP = config.get("ScoreWeightsConfig", "PersonalXP")
Readability = config.get("ScoreWeightsConfig", "Readability")
Length = config.get("ScoreWeightsConfig", "Length")

# Read cosmetic info (t, background)
font_path = config.get("TextConfig", "font_path")
Font = config.get("TextConfig", "font")
font_size = config.get("TextConfig", "font_size")
font_color = config.get("TextConfig", "font_color")
background_color = config.get("BackgroundConfig", "background_color")
watermark_logo  = config.get("BackgroundConfig", "watermark_logo")

# Authenticate so that the bot can act
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# Function written by Ryan Pitts
def clean_thread_url(url, forum):
	'''
	Most websites use standard story URLs as Disqus thread identifiers,
	but not _all_ websites do. This method provides a place for applying
	custom filters that convert Disqus URLs for websites that need it.
	Params:
		`url`: a string representing the story URL with comments to parse
		`config`: a CONFIG object with a `forum` attribute representing
			the Disqus forum identifier
	Usage:
		url = clean_thread_url(page_url, forum)
	Any URL can be passed into this method; it will only be manipulated
	if the forum in the CONFIG object matches a website known to use
	different Disqus thread identifiers.
	'''

	# ABC News
	# remove slug component of the URL
	if forum == 'abcnewsdotcom':
		bits = url.split('/')
		del bits[-2]
		url = '/'.join(bits)

	# NPR
	# remove querystring with tracking bits
	if forum == 'npr-news':
		bits = url.split('?')
		url = bits[0]

	return url



# This class defines a number of methods for the bots editorial logic and actions.
# As a subclass of StreamListener the bot can listen to the Twitter stream based on the filter_object variable
class CommentBot(tweepy.StreamListener):
	def __init__(self):
		super(CommentBot, self).__init__()

		# Set of bunch of variables we need
		self.num_tweets = 0
		self.twitter_api_count = 0
		self.comments_api_count = 0
		self.old_time = time.time()

		# Defines the filter for Twitter Streams to capture data, can provide a hashtag, word, or screenname
		# Currently set to track all tweets mentioning nytimes.com, see https://dev.twitter.com/streaming/overview/request-parameters
		self.filter_object = [filter_object_]  # eg 'nytimes com'

		# CommentBot needs a reference to the stream so it can disconnect and reconnect after sleeping
		self.stream = None

		# Check if there is a valid API specified
		if API != "NYT" and API != "Disqus":
			print("No valid API selected")
			raise Exception()

	# If a Tweet matches the listener criteria, the on_data function is invoked
	def on_data(self, data):
		try:
			print "-----"
			self.editorial_logic(data)

		except Exception as e:
			print "Exception ", e
			#print data
			pass
		return True

	# Editorial logic for bot
	def editorial_logic(self, data):
		# convert the data to json
		tweet_data = json.loads(data)

		# Only consider tweets in english
		if tweet_data["lang"] != "en":
			return

		# Make sure that the bot never interacts with itself
		user = tweet_data['user']['screen_name']
		user_mentions = tweet_data['entities']['user_mentions']
		user_mentions_list = []
		for u in user_mentions:
			user_mentions_list.append(u["screen_name"])
		# Make sure the bot never responds to itself, or to any tweet where it's mentioned
		if user == bot_name or bot_name in user_mentions_list:
			return

		# Don't bother responding to someone that RTed the thing
		if tweet_data["retweeted"] == True:
			return

		# Get the first URL listed in the tweet
		if len(tweet_data["entities"]["urls"]) == 0:
			return

		# Get the URL shared in the tweet
		url = tweet_data["entities"]["urls"][0]["expanded_url"]
		if url == None:
			return
		url = clean_thread_url(url, forum)
		print(url)

		# Determine if the url is your News Org url by seeing if it includes a specific string e.g. "nytimes" or "nyti.mes", or "npr.org2016" or "n.pr/".
		if any(substring in url for substring in news_org_url) == False:
			print('news_org_url list items not in url')
			return

		self.comments_api_count = self.comments_api_count + 1
		# comments_api_key is a pick of a comments key from the comments_keys list
		comments_api_key = comments_keys[self.comments_api_count % len(comments_keys)]
		if API == "NYT":
			r = requests.get("http://api.nytimes.com/svc/community/v3/user-content/url.json", params={"url": url, "api-key": comments_api_key})
		if API == "Disqus":
			r = requests.get("http://disqus.com/api/3.0/threads/listPosts.json", params={"thread": 'link:'+url, "api_key": comments_api_key, "forum": forum, "limit":100})

		print time.strftime("%H:%M:%S")
		print "comment API count: " + str(self.comments_api_count)
		try:
			print r.url
			comments_data = r.json()
			
			#print(comments_data)
		except:
			response = r.text
			print("Comments collection Failed. If using Disqus, article might use different Disqus forum")
			if response.find("Developer Over Rate"):
				print "Comments API Rate Limit"
				self.api_limit_checker()
				return


		if API == 'NYT':
			num_comments_found = comments_data["results"]["totalParentCommentsFound"]
		if API == "Disqus":
			comments_data = comments_data["response"]
			num_comments_found = len(comments_data)
		print("Number of comments found: " + str(num_comments_found))

		# Check if there are more than 100 comments since we only want to consider articles that have a robust conversation on them
		# Note: this is the total count, but in the API below we just consider  top-level "parent" comments
		if num_comments_found < int(min_comments_found):
			return

		# To slow the bot down we only consider every Nth (in this case 10th) tweet
		self.num_tweets = self.num_tweets + 1
		print "Nth Tweet: " + str(self.num_tweets)
		if self.num_tweets < 3:
			return
		else:
			# Get all the comments on the article
			# Note: Looping through offset only gets you the top level "parent" comments and not the child responses (NYT)
			# 'offset' not required for Disqus comments - parent level comments are specified using 'Parent' tag.
			tagged_comments = []
			if API == 'NYT':
				pagesize = 25
				offset = 0
				while offset < num_comments_found:
					time.sleep (.2) # NYT API is limited to 5 calls per second max
					self.api_limit_checker()
					self.comments_api_count = self.comments_api_count + 1
					comments_api_key = comments_keys[self.comments_api_count % len(comments_keys)]
					r = requests.get("http://api.nytimes.com/svc/community/v3/user-content/url.json", params={"url": url, "api-key": comments_api_key, "offset": offset})
					try:
						r_data = r.json()
						r_data = json.loads(r.text)
						if "comments" in r_data["results"]:
							for comment in r_data["results"]["comments"]:
								# Do a hard filter to remove anything that's less than 25 words
								if calcLength(comment["commentBody"]) > 25:
									tagged_comments.append(comment)
						offset = offset + pagesize
					except:
						pass
			if API == 'Disqus':
				self.api_limit_checker()
				self.comments_api_count = self.comments_api_count + 1
				for comment in comments_data:
					if comment['parent'] == None:
						print(comment['author']['reputation'])
						if comment['author']['reputation'] > float(reputation):   # Trying to only get worthy comments?
							raw_message = comment['raw_message']
					# Do a hard filter to remove anything that's less than 25 words
							if calcLength(raw_message) > 25:
								tagged_comments.append(comment)

			# Initialize the min and max scores which we will need for score normalization
			min_pxp = 1
			max_pxp = 0
			min_readability = 100
			max_readability = 0
			min_length = 10000
			max_length = 0

			print "num comments: " + str(len(tagged_comments))
			if (len(tagged_comments)) < 3:
				return

			for i, comment in enumerate(tagged_comments):
				if API == 'NYT':
					comment["PersonalXP"] = calcPersonalXPScore(comment["commentBody"])
					comment["Readability"] = calcReadability(comment["commentBody"])
					comment["Length"] = calcLength(comment["commentBody"])
				if API == 'Disqus':
					comment["PersonalXP"] = calcPersonalXPScore(comment["raw_message"])
					comment["Readability"] = calcReadability(comment["raw_message"])
					comment["Length"] = calcLength(comment["raw_message"])

				if comment["PersonalXP"] < min_pxp:
					min_pxp = comment["PersonalXP"]
				if comment["PersonalXP"] > max_pxp:
					max_pxp = comment["PersonalXP"]
				if comment["Readability"] < min_readability:
					min_readability = comment["Readability"]
				if comment["Readability"] > max_readability:
					max_readability = comment["Readability"]
				if comment["Length"] < min_length:
					min_length = comment["Length"]
				if comment["Length"] > max_length:
					max_length = comment["Length"]

			# Set weights that are used to linearly weight the sub-scores for the final score
			score_weights = {"PersonalXP": float(PersonalXP), "Readability": float(Readability), "Length": float(Length)}

			# Calculate normalized scores, each is scaled to be between 0 and 1
			for i, comment in enumerate(tagged_comments):
				comment["PersonalXP"] = (comment["PersonalXP"] - min_pxp) / (max_pxp - min_pxp)
				comment["Readability"] = (comment["Readability"] - min_readability) / (max_readability - min_readability)
				comment["Length"] = (comment["Length"] - min_length) / (max_length - min_length)
				comment["Score"] = (score_weights["PersonalXP"] * comment["PersonalXP"]) + (score_weights["Readability"] * comment["Readability"]) + (score_weights["Length"] * comment["Length"])

			# sort comments
			sorted_comments = sorted(tagged_comments, key = lambda k: k["Score"], reverse=True)

			# Randomly select one of the top 3 comments to send as a reply
			top_index = random.randint(0, 2)
			print "top comment score: " + str(sorted_comments[top_index]["Score"])

			# Finally trigger the bot's action to reply
			self.action(sorted_comments[top_index], tweet_data)


	# Take an action, like replying to another tweet in this case
	def action(self, comment, tweet):
		# Check to see if we've crossed a Twitter API limit
		self.api_limit_checker() #we invoke the API limit checker code

		# Invoke a reply
		self.tweet_reply(comment, tweet)

		# Reset counter and increment the API use count
		self.num_tweets = 0
		self.twitter_api_count = self.twitter_api_count + 1

		# Limit the bot's output by going to sleep for 15 minutes
		self.stream.disconnect()
		time.sleep(900)
		self.stream.filter(track=self.filter_object)
		return

	#This is the API limit checker function which checks if we do not exceed 140 Tweets per 15 minutes as per Twitter API limits
	def api_limit_checker(self):
		if time.time() - self.old_time > 900:	#If we are outside a 15 min window
			self.old_time = time.time()	#Reset the timer of window since new window started & Twitter limits refreshed
			self.twitter_api_count = 0	#Reset the api counter to 0 since new window started & Twitter limits refreshed
		else:
			# If we've surpassed the api count during a 15 minute window
			if self.twitter_api_count > 140:
				self.stream.disconnect()
				time.sleep(900 - (time.time() - self.old_time))	#We put the code to sleep for 15-x minutes where x is the current time - old time (when the window started)... So if within 6 minutes we tweet more than 140 times, then the script will halt for the next 15-6=9 minutes until a new window starts
				self.stream.filter(track=self.filter_object)
				self.twitter_api_count = 0	#Since we have slept through the remainder, a new window has started and we reset the API Count as well
				self.old_time = time.time() #Similarly as above, we reset the timer as well since new window has started

		if API == 'NYT':
			if self.comments_api_count > 1000 * len(comments_keys):
				# once we exhaust NYT API calls we go to sleep for 24 hours
				print "No more NYT API calls today. Going to sleep for 24 hours, see you tomorrow"
				self.comments_api_count = 0
				self.stream.disconnect()
				time.sleep (86400)
				self.stream.filter(track=self.filter_object)
		if API == 'Disqus':
			if self.comments_api_count > 1000 * len(comments_keys):
				# once we exhaust Disqus API calls we go to sleep for 24 hours
				print "No more Disqus API calls today. Going to sleep for 24 hours, see you tomorrow"
				self.comments_api_count = 0
				self.stream.disconnect()
				time.sleep (86400)
				self.stream.filter(track=self.filter_object)

	#This function takes the Tweet JSON as an input
	#This module takes the Tweet JSON and then calls extract which will help in extracting the key requirements from it
	def tweet_reply(self, comment, tweet):
		print("Starting tweet_reply")
		# Generate image with comment
		if API == 'NYT':
			text = '"'+comment["commentBody"]+'"'
			#text = text.replace('<br/>',' ')
		if API == 'Disqus':
			text = '"'+comment["raw_message"]+'"'

		# Replace a double <br/> (a paragraph break) with just a space.
		text = re.sub("<br\/><br\/>"," ", text)
		soup = BeautifulSoup(text, "html.parser") # BeautifulSoup still prints that warning...ugh
		text = soup.get_text()
		# remove any extra spaces
		text = re.sub("\s+"," ", text)
		if API == 'NYT':
			self.create_image(text, comment["userDisplayName"], comment["userLocation"])
		if API == 'Disqus':
			self.create_image(text, comment["author"]["name"], comment["author"]["location"])

		# Grab user info and generate text for status
		user = tweet['user']['screen_name']
		at = "@"+user
		tweet_id = tweet['id']
		url = tweet["entities"]["urls"][0]["expanded_url"]
		url = clean_thread_url(url, forum)
		# at+" "+
		# In case you're interested, here's a personal
		# see here for info on RT quoting a tweet: https://twittercommunity.com/t/method-to-retweet-with-comment/35330/17
		status = "HT " + at + " for sharing this NYT article: " + url + " Here's an anecdote from the comments:" # + "https://twitter.com/"+user+"/status/"+str(tweet_id)

		image = "tweet_reply.png"

		api.update_with_media(filename=image,status=status,in_reply_to_status_id=tweet_id)

	#===============Image Module=======================
	#Since Twitter allows only 140 character limit, we use an image in the reply
	#This module allows wrapping the text so that is can be converted to an image properly
	def wrap_text(self, wrap,font,draw,max_line_height):
		margin = offset = 20
		for line in wrap:
			draw.text((margin,offset),line,font=font,fill=font_color)
			offset += max_line_height
			#offset += font.getsize(line)[1]
			#print font.getsize(line)[1]

	#This module takes in the message and converts it to an image. It has internal helper module which help in
	def create_image(self, message, user, location):
		
		font = ImageFont.truetype(os.path.join(font_path, Font), int(font_size))
		margin = offset = 20
		attribution_text = u" \u2014 "  + user + ", " + location

		# Define the box which should be the position of the logo on your canvas. Here is Top left corner (800 across; 0 down) and bottom-right corner
		# 900 across; 100 down. Logo dimension is 100 x 100 pixels. )
		if watermark_logo:
			wrap = textwrap.wrap(message,width=50)
		else:
			# No logo then make the lines a bit wider
			wrap = textwrap.wrap(message,width=55)

		# The height of different lines sometimes varies but want to make consistent
		line_heights = []
		for l in wrap:
			line_heights.append(font.getsize(l)[1])
		print(line_heights)
		max_line_height = max(line_heights)

		text_height = max_line_height * len(wrap)
		#for l in wrap:
		#	text_height = text_height + font.getsize(l)[1]
		#	print(text_height)

		# add in the height of hte attribution text too 
		attribution_height = font.getsize(attribution_text)[1]
		#line_height = font.getsize(wrap[0])[1]
		print "total text height: " + str(text_height + attribution_height)
		print wrap 

		
		# Make the image double the size to start with, so that we can apply a antialis function when we scale down. Text looks better (I think)
		# enough space for "margin" at the top and bottom and also a .5 margin between the comment and the attribution
		img=Image.new("RGBA", (900,int(2.5*margin+text_height+attribution_height)),(background_color))
		draw = ImageDraw.Draw(img)
		self.wrap_text(wrap,font,draw,max_line_height)			
		draw.text((margin,int(1.5*margin+text_height)), attribution_text,font=font,fill=font_color) 

		if watermark_logo:
			# If there's a logo file provided then make space for it and paste it into the upper right corner
			logo = Image.open(watermark_logo)
			box = (800, 0, 900, 100)
			img.paste(logo, box)

  		img_resized = img.resize((int(img.size[0]*.5), int(img.size[1]*.5)), Image.ANTIALIAS)
  		draw = ImageDraw.Draw(img_resized)
		img_resized.save("tweet_reply.png")
		


	def on_error(self, status):
		print ("This is an on_error() issue", status)
		if status_code == 420:
			return False


	def on_exception(self, exception):
		"""Called when an unhandled exception occurs."""
		print("Here's my on_exception", exception)
		raise exception
		return


# Function to start the bot listening to the Twitter stream
def run():
	#This handles Twitter authetification and the connection to Twitter Streaming API
	try:
		cb = CommentBot()
		stream = tweepy.Stream(auth, cb)
		cb.stream = stream
		stream.filter(track=cb.filter_object) # async=True, 
	except (Timeout, ssl.SSLError, ReadTimeoutError, ConnectionError, ProtocolError, IncompleteRead, AttributeError) as exc:
		print ("This is a run() exception ", exc)
		pass
	except:
		print ("This is a run() exception 2", exc)
		pass 

#def start_stream(stream, tb)
