import CommentBot

# In some cases the stream may be disconnected and we need to restart it
def run():
	try:
		CommentBot.run()
	except:
		run()

run()
