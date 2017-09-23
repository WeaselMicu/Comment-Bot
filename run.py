from CommentBot import CommentBot
import tweepy
import ConfigParser
import os


config = ConfigParser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + "/config/anecbotalNYT.conf")

#  Twitter keys, message, and bot name:
consumer_key = config.get("TwitterConfig", "consumer_key")
consumer_secret = config.get("TwitterConfig", "consumer_secret")
access_token = config.get("TwitterConfig", "access_token")
access_token_secret = config.get("TwitterConfig", "access_token_secret")
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

cb = CommentBot()

while 1 != 0:
	print ("starting a new run.")
	cb.stream = tweepy.Stream(auth, cb)
	cb.stream.filter(track=cb.filter_object)
