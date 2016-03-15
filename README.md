# Comment Bot
This repository contains the code to run the [AnecbotalNYT](https://twitter.com/anecbotalnyt) News Bot on Twitter.  It's being open sourced as a reference implementation for other news bots that listen and respond on Twitter. 

For more information on News Bots see the following article: 
- T. Lokot and N. Diakopoulos. News Bots: Automating News and Information Dissemination on Twitter. Digital Journalism. 2016. [PDF](http://www.nickdiakopoulos.com/wp-content/uploads/2011/07/newsbots_final.pdf)

This project makes extensive use of the code from the [CommentIQ repository](https://github.com/comp-journalism/commentIQ), but has been repurposed. 

### Editorial Transparency


### Setup
If you'd like to run this bot (or repurpose it) first clone the repository to your system. 

**Keys**  
Rename `example-bot.conf` to `bot.conf` and add your Twitter API keys and NYT Community API keys (more instructions follow). 

To sign up for a Twitter API key and App follow the instructions here: http://www.compjour.org/tutorials/getting-started-with-tweepy/ to create a Twitter app. You need to do this in order to get the necessary authentication tokens to log in to Twitter programmatically. Put these tokens in the `bot.conf` file. 

To sign up for NYT Community API Keys see the documentation: http://developer.nytimes.com/docs/community_api/The_Community_API_v3/. Also put these tokens in the `bot.conf` file. 

**Software Dependencies**  
Before you can run the bot you must install the following dependencies (setting up a virtual environment is recommended, tutorial [here](http://www.simononsoftware.com/virtualenv-tutorial/)):
- Python v 2.7
- Tweepy v 3.5.0
- Beautiful Soup v 4.3.2
- NLTK
- Lxml v 3.4.3
- Pillow v 2.8.1 (may also rely on freetype, libjpeg, and libpng, or freetype-devel)

**Running**  
To set the bot up to run indefinitely but to continually output status information to file run a command like:
- `nohup python -u run.py > nohup.txt &`

