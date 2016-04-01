# AnecbotalNYT Comment Bot
This repository contains the code to run the [AnecbotalNYT](https://twitter.com/anecbotalnyt) News Bot on Twitter.  It's being open sourced as a reference implementation for other news bots that listen and respond on Twitter. 

For more information on News Bots see the following article: 
- T. Lokot and N. Diakopoulos. News Bots: Automating News and Information Dissemination on Twitter. Digital Journalism. 2016. [PDF](http://www.nickdiakopoulos.com/wp-content/uploads/2011/07/newsbots_final.pdf)

This project makes extensive use of the code from the [CommentIQ repository](https://github.com/comp-journalism/commentIQ), but has been repurposed. 

### Editorial Transparency
The goal of AnecbotalNYT is to find interesting anecdotes from the NYT comments made on NYTimes.com and make them more visible to people tweeting about those stories on Twitter. The hope is that some of the more thoughtful personal stories and opinions that people make in the comments can be interesting and engaging content on Twitter as well. 

[Nick Diakopoulos](http://www.nickdiakopoulos.com) [@ndiakopoulos](http://www.twitter.com/ndiakopoulos) is the author of AnecbotalNYT, but the bot itself tweets autonomously once run. There is no editional human filtering or oversight of the bot. 

####Data Inputs
**Provenance** 
- Data is drawn directly from the [NYT Community API](http://developer.nytimes.com/docs/community_api/The_Community_API_v3/). The bot is accurate and reliable as the data delivered from that API. 
**Sampling & Filtering**  

- The bot only considers top level comments (and filters out comments that are responses to other comments) as they're more likely to be responding directly to the ideas in the article. 
- The bot listens to the free Twitter stream for people tweeting a link containing "nytimes.com". It considers the first link it finds in the tweet only. Filtered out are tweets that are retweets, tweets not in english, and tweets that refer to the bot's account. The article link must have comments, and it must have 100 or more comments in order to be considered. Every 10th article link that meets these criteria will have a comment selected for the bot to tweet out. The comments are selected by ranking and scoring them according to the scores described below. The final comment tweeted out is a random selection from the top 3 according to the ranking. 
**Personal Information**  

- The bot does not share any personal information that is not available from the NYT Community API. The comments that the bot shares are attributed to the name and the location of the user who shared the comment. 

**Variable Definitions**   
The bot relies on the composition of three scores in order to rank and select the comments that it tweets. 
- Length. The Length score is computed as the number of words in a comment.
- Readability. The Readability score is calculated as the [SMOG](http://www.readabilityformulas.com/smog-readability-formula.php) index or reading grade level of the text.
- Personal Experience. Measures the rate of use of words in Linguistic Inquiry and Word Count ([LIWC](http://liwc.wpengine.com/)) categories “I”, “We”, “Family”, and “Friends”. This score was validated in previously [published research](http://www.nickdiakopoulos.com/wp-content/uploads/2011/07/ISOJ_Journal_V5_N1_2015_Spring_Diakopoulos_Picking-NYT-Picks.pdf). 


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

