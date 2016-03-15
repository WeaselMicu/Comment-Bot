# Comment Bot
This repository contains the code to run the [AnecbotalNYT](https://twitter.com/anecbotalnyt) News Bot on Twitter.  It's being open sourced as a reference implementation for other news bots that listen and respond on Twitter. 

### Setup - Keys & Tokens
First rename `example-bot.conf` to `bot.conf` and add your Twitter API keys and NYT Community API keys. 

To sign up for a Twitter API key and App follow the instructions here: http://www.compjour.org/tutorials/getting-started-with-tweepy/ to create a Twitter app. You need to do this in order to get the necessary authentication tokens to log in to Twitter programmatically. Put these tokens in the `bot.conf` file. 

To sign up for NYT Community API Keys see the documentation: http://developer.nytimes.com/docs/community_api/The_Community_API_v3/. Also put these tokens in the `bot.conf` file. 

### Software Dependencies
- Python v 2.7
- Tweepy v 3.5.0
- Beautiful Soup v 4.3.2
- Lxml v 3.4.3
- Pillow v 2.8.1 (may also rely on freetype, libjpeg, and libpng, or freetype-devel)

