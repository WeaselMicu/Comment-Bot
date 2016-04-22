# General Imports
import time, datetime, sys, os, re, random
import json, csv
import requests
import ConfigParser
from bs4 import BeautifulSoup


# Import tweepy and DisqusAPIs
import tweepy
from disqusapi import DisqusAPI

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
config.read(os.path.dirname(os.path.abspath(__file__)) + "/bot.conf")

# Read Twitter keys...
consumer_key = config.get("TwitterConfig", "consumer_key")
consumer_secret = config.get("TwitterConfig", "consumer_secret")
access_token = config.get("TwitterConfig", "access_token")
access_token_secret = config.get("TwitterConfig", "access_token_secret")

# Read Disqus info
disqus_API_key = config.get("CommentConfig", "disqus_API_key")

# Read cosmetic info (font, background)
font_path = config.get("TextConfig", "font_path")
Font = config.get("TextConfig", "font")
font_size = config.get("TextConfig", "font_size")
font_color = config.get("TextConfig", "font_color")
background_color = config.get("BackgroundConfig", "background_color")

# enter items specific to where your comments will come from
#comment_keys = config.get("CommentConfig", "comment_keys")
#filter_object_ = config.get("CommentConfig", "filter_object")
bot_name =  config.get("CommentConfig", "bot_name")
forum = config.get("CommentConfig", "disqus_forum")
reputation = config.get("CommentConfig", "reputation")

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
		self.comment_api_count = 0
		self.old_time = time.time()

		# Defines the filter for Twitter Streams to capture data, can provide a hashtag, word, or screenname
		# Currently set to track all tweets mentioning nytimes.com, see https://dev.twitter.com/streaming/overview/request-parameters
		self.filter_object = ['npr org']

	# If a Tweet matches the listener criteria, the on_data function is invoked
	def on_data(self, data):
		try:
			print "-----"
			self.editorial_logic(data)

		except Exception as e:
			print "Exception ", e
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
		url = clean_thread_url(url, forum)

		# Determine if the url is a NYTimes url by seeing if it includes the string "nytimes"
		if not ("npr.org/2016" in url or "n.pr/" in url):
			return

		#if "npr.org/sections/" in url:
		#	return

		self.comment_api_count = self.comment_api_count + 1
		#nytk = disqus_API_key[self. % len(disqus_API_key)]
		#http://stackoverflow.com/questions/4755278/is-it-possible-to-use-the-disqus-api-to-get-comments-from-a-specific-url
		r = requests.get("http://disqus.com/api/3.0/threads/listPosts.json", params={"thread": 'link:'+url, "api_key": disqus_API_key, "forum": forum, "limit":100})
		print time.strftime("%H:%M:%S")
		print "comment API: " + str(self.comment_api_count)
		try:
			#print "http://disqus.com/api/3.0/threads/listPosts.json" + url + "&api_key=" + disqus_API_key + "&forum=" + "npr"
			comments_data = r.json()["response"]
		except:
			response = r.text
			if response.find("Developer Over Rate"):
				print "Disqus Rate Limit"
				self.api_limit_checker()
				return

		print comments_data
		num_comments_found = len(comments_data)
		print "Number of comments:  " + str(num_comments_found)

		# Check if there are more than 100 comments since we only want to consider articles that have a robust conversation on them
		# Note: this is the total count, but in the API below we just consider  top-level "parent" comments
		if num_comments_found < 50: #This was 100! -> Parameterise this for testing purposes?
			return

		# To slow the bot down we only consider every Nth (in this case 10th) tweet
		self.num_tweets = self.num_tweets + 1
		print "ntweets: " + str(self.num_tweets)
		if self.num_tweets < 10:
			return

		else:
			# Get all the comments on the article
			tagged_comments = []
			self.api_limit_checker()
			self.comment_api_count = self.comment_api_count + 1
			for comment in comments_data:
				if comment['parent'] == None:
					print(comment['repuation'])
					if comment['reputation'] > int(reputation):   # Trying to only get top-level comments
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
			for i, comment in enumerate(tagged_comments):
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
			score_weights = {"PersonalXP": .5, "Readability": .25, "Length": .25}

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
		time.sleep(900)
		return

	#This is the API limit checker function which checks if we do not exceed 140 Tweets per 15 minutes as per Twitter API limits
	def api_limit_checker(self):
		if time.time() - self.old_time > 900:	#If we are outside a 15 min window
			self.old_time = time.time()	#Reset the timer of window since new window started & Twitter limits refreshed
			self.twitter_api_count = 0	#Reset the api counter to 0 since new window started & Twitter limits refreshed
		else:
			# If we've surpassed the api count during a 15 minute window
			if self.twitter_api_count > 140:
				time.sleep(900 - (time.time() - self.old_time))	#We put the code to sleep for 15-x minutes where x is the current time - old time (when the window started)... So if within 6 minutes we tweet more than 140 times, then the script will halt for the next 15-6=9 minutes until a new window starts
				self.twitter_api_count = 0	#Since we have slept through the remainder, a new window has started and we reset the API Count as well
				self.old_time = time.time() #Similarly as above, we reset the timer as well since new window has started

		if self.comment_api_count > 1000 * len(disqus_API_key):
			# once we exhaust Disqus API calls we go to sleep for 24 hours
			print "No more Disqus API calls today. Going to sleep for 24 hours, see you tomorrow"
			self.comment_api_count = 0
			time.sleep (86400)

	#This function takes the Tweet JSON as an input
	#This module takes the Tweet JSON and then calls extract which will help in extracting the key requirements from it
	def tweet_reply(self, comment, tweet):
		# Generate image with comment
		text = '"'+comment["raw_message"]+'"'
		#text = text.replace('<br/>',' ')
		soup = BeautifulSoup(text)
		text = soup.get_text()
		# remove any extra spaces
		text = re.sub("\s+"," ", text)
		self.create_image(text, comment["author"]["name"], comment["author"]["location"])

		# Grab user info and generate text for status
		user = tweet['user']['screen_name']
		at = ".@"+user
		tweet_id = tweet['id']
		# see here for info on RT quoting a tweet: https://twittercommunity.com/t/method-to-retweet-with-comment/35330/17
		status = "HT to " + at + " for sharing this article. Here's an anecdote from the article's comments:" # + "https://twitter.com/"+user+"/status/"+str(tweet_id)

		image = "tweet_reply.png"

		api.update_with_media(filename=image,status=status,in_reply_to_status_id=tweet_id)


	#===============Image Module=======================
	#Since Twitter allows only 140 character limit, we use an image in the reply
	#This module allows wrapping the text so that is can be converted to an image properly
	def wrap_text(self, wrap,font,draw):
		margin = offset = 20
		margin = 20
		for line in wrap:
			draw.text((margin,offset),line,font=font,fill=font_color)
			offset += font.getsize(line)[1]

	#This module takes in the message and converts it to an image. It has internal helper module which help in
	def create_image(self, message, user, location):
		wrap = textwrap.wrap(message,width=50)
		print(wrap)
		font = ImageFont.truetype(os.path.join(font_path, Font), int(font_size))
		logo = Image.open(watermark_logo)

		img=Image.new("RGBA", (900,140+34*len(wrap)),(background_color))
		draw = ImageDraw.Draw(img)
		self.wrap_text(wrap,font,draw)
		margin = offset = 20
		# Define the box which should be the position of the logo on your canvas. Here is Top left corner (800 across; 0 down) and bottom-right corner
		# 900 across; 100 down. My image dimension is 100 x 100 pixels. )
		box = (800, 0, 900, 100)
		img.paste(logo, box)
		draw.text((margin,offset+10+38*len(wrap))," -- "  + user + ", " + location,font=font,fill=font_color) # Make into 'm' dash, not double dash #Values orig (margin, offset+10+17*len(wrap))
  		img_resized = img.resize((450, 70+17*len(wrap)), Image.ANTIALIAS)
  		draw = ImageDraw.Draw(img_resized)
		img_resized.save("tweet_reply.png")


	def on_error(self, status):
		print status

# Function to start the bot listening to the Twitter stream
def run():
	#This handles Twitter authetification and the connection to Twitter Streaming API
	tb = CommentBot()
	stream = tweepy.Stream(auth, tb)

	try:
		stream.filter(track=tb.filter_object, async=True)
	except (Timeout, ssl.SSLError, ReadTimeoutError, ConnectionError, ProtocolError, IncompleteRead, AttributeError) as exc:
		print exc
		pass
	except:
		pass
