# Anecbotal Comment Bot
This repository contains the code to run a News Bot on Twitter that shares anecdotes.  It's being open sourced as a reference implementation for other news bots that listen and respond on Twitter. Currently, we have versions that use different commenting systems that live on different branches:
- [AnecbotalNYT](https://twitter.com/anecbotalnyt) configured example that lives on [Anecbotal_NYT](https) branch using the NYT bespoke comments systems
- [__TestB0t__](https://twitter.com/__TestB0t__) configured example that lives on [Anecbotal_Disqus](https) branch using the Disqus commenting system, tweeting from NPR's `npr-news` Disqus forum. [__TestB0t__](https://twitter.com/__TestB0t__) is not running currently, but exists with an example of a `.png` output.

We hope to expand this is the future to include configurations for other comment systems such as LiveFyre and Facebook.

For more information on News Bots see the following article:
- T. Lokot and N. Diakopoulos. News Bots: Automating News and Information Dissemination on Twitter. Digital Journalism. 2016. [PDF](http://www.nickdiakopoulos.com/wp-content/uploads/2011/07/newsbots_final.pdf)

This project makes extensive use of the code from the [CommentIQ repository](https://github.com/comp-journalism/commentIQ), but has been repurposed.

### Editorial Transparency
In addition to full source code transparency for the bot, a more accessible version that describes the key aspects of the bot is provided here.

The goal of Anecbotal is to find interesting anecdotes from comments made on a news article and make them more visible to people tweeting about those stories on Twitter. The hope is that some of the more thoughtful personal stories and opinions that people make in the comments can be interesting and engaging content on Twitter as well.

[Nick Diakopoulos](http://www.nickdiakopoulos.com) [@ndiakopoulos](http://www.twitter.com/ndiakopoulos) from the Computational Journalism Lab at the University of Maryland is the author of AnecbotalNYT, and [@_JAStark](https://twitter.com/_jastark) who is a postdoc in the lab wrote the Disqus implementation. The bot itself tweets autonomously once run. There is no additional human filtering or oversight of the bot.

The Disqus part of this bot was written at OpenNews (Mozilla Foundation) Code Convening Austin 2016 as part of Bot Week (insert links to bot week source)

**Input Data**  

Data is drawn directly from the [NYT Community API](http://developer.nytimes.com/docs/community_api/The_Community_API_v3/) or the [Disqus requests API](https://disqus.com/api/docs/requests/) and consists of the raw comment text as well as some of the metadata of the comment such as the user name and location. Other data that the bot uses as input comes from Twitter.

*Sampling*  
- The bot only considers top level comments (and filters out comments that are responses to other comments) as they're more likely to be responding directly to the ideas in the article.
- The bot listens to the free Twitter stream for people tweeting a link containing a link to your news site of choice, e.g. "nytimes.com". It considers the first link it finds in the tweet only. Tweets that are retweets, tweets not in english, and tweets that refer to the bot's own account are filtered out. The article link must have comments, and it must have 100 or more comments in order to be considered. Every 10th article link that meets these criteria will have a comment selected for the bot to tweet out.

*Personal Information*  
- The bot does not collect any personal information that is not available from the NYT Community API. The comments that the bot shares are attributed to the name and the location of the user who shared the comment if that data is available.
- The bot stores no information.

**Model** (calculations performed on a comment)

The bot relies on the composition of three scores in order to rank and select the comments that it tweets. Each of these scores is calculated for each comment. This is how the scores are defined:

- *Length.* The Length score is computed as the number of words in a comment.
- *Readability.* The Readability score is calculated as the [SMOG](http://www.readabilityformulas.com/smog-readability-formula.php) index or reading grade level of the text.
- *Personal Experience.* Measures the rate of use of words in Linguistic Inquiry and Word Count ([LIWC](http://liwc.wpengine.com/)) categories “I”, “We”, “Family”, and “Friends”. This score was validated in previously [published research](http://www.nickdiakopoulos.com/wp-content/uploads/2011/07/ISOJ_Journal_V5_N1_2015_Spring_Diakopoulos_Picking-NYT-Picks.pdf).

The three scores are weighted in a linear combination in order to calculate an overall "anecbotal" score for each comment. The weights are Length: 0.25, Readability: 0.25, Personal Experience: 0.50 in order to prioritize comments that have substantial personal experience scores. The final comment tweeted out is a random selection from the top 3 comments on an article according to the ranking.

At some point we will introduce these editorial logic to the `bot.conf` file so you can select your own weights.

*Additional Editorial Rules*  
- Comments with less than 25 words are filtered out as being too short.
- If the bot exhausts its NYT Community API or Disqus limits for the day it goes to sleep for a full 24 hours before continuing.

**Interface**  

The bot is clearly labeled as a bot in its bio (and with a link to this page) in order to avoid any confusion.


## Setup
If you'd like to run this bot (or repurpose it) first clone the repository to your system.

**Keys**  

Rename `example-bot.conf` to `bot.conf` and add your Twitter API keys, NYT Community API keys, or Disqus keys (more instructions follow).

To sign up for a Twitter API key and App follow the instructions here: http://www.compjour.org/tutorials/getting-started-with-tweepy/ to create a Twitter app. You need to do this in order to get the necessary authentication tokens to log in to Twitter programmatically. Put these tokens in the `bot.conf` file.

To sign up for NYT Community API Keys see the documentation: http://developer.nytimes.com/docs/community_api/The_Community_API_v3/. Also put these tokens in the `bot.conf` file.

To sign up for Disqus API keys, sign in to Disqus (if you're using this bot for Disqus comments, I am assuming your organization already has an account), and then register a new App.

**A Note About Disqus**
The Disqus commenting community relies on forums with unique names. Some news organizations like NPR use several section-specific forums (eg `npred` for their education section, and `npr-news` for their general news section). Therefore, be sure to use the correct forum for your Bot. This code does not currently support more than one forum at a time, so you can only have your Bot tweet from one specified forum.


**Software Dependencies**  
Before you can run the bot you must install the following dependencies (setting up a virtual environment is recommended, tutorial [here](http://www.simononsoftware.com/virtualenv-tutorial/)) using `pip install -r requirements.txt`:
- Python v 2.7
- Tweepy v 3.5.0
- Beautiful Soup v 4.3.2
- NLTK
- Lxml v 3.4.3
- Pillow v 2.8.1 (may also rely on freetype, libjpeg, and libpng, or freetype-devel)

*NB* If you are using Anaconda's python distribution, create your virtual environment thus:
- In the command line, type `conda create -n commentbot python=2.7`
- Then activate the new environment by typing `source activate commentbot`
- Open `requirements.txt` in a text editor and comment out `python==2.7` line and save.
- On the command line, type `pip install -r requirements.txt`, and you should see everything successfully installing.
- To check you have the requirements installed, you can type `pip freeze` which will print the installed modules to your screen.


### Testing

**Twitter Bot**
- Keep Bot Private and put in the "Bio" to not follow, just so people know exactly who and what you are.
- Reduce [CommentConfig] `min_comments_found = 50` comment limit to a lower number (like 10 or 50) so when testing it will tweet something sooner.
- Stop App to iterate code, start App to test, watch `nohup.txt` populate to check for errors and know when it's tweeted. Check the tweet, stop App, re-code... etc etc and delete tweet so as not to annoy anyone ;)
- Once happy, reconfig [CommentConfig] to 100 (or whatever you like), undo twitterbot privacy and edit Bio.

**Tips and Tricks working with Disqus forum queries**
To check you have the correct forum name, use the Disqus console https://disqus.com/api/console/#!/ which you can access after registering your App with Disqus. Here, fill in:
- `Application` field with your App name (secret or public doesn't _seem_ to matter)
- `Headers and Methods` with `GET` and from the dropdown menu, under `Posts` select `list`. In the next field, select `json`
- `Parameters` with `forum` = `npr-news` or the forum name of your choice;
- New line of `Parameters` with `thread:link` = `http.....` or real example of a link you want to be able to get comments from
- Then press the `Send Request` button.

You'll know it worked when you get a nice JSON response. Now you can enter that forum name into the [CommentConfig] `disqus_forum` section. If it doesn't work, you likely have something wrong with the **forum** selected _or_ with the url link being queried.

***Explain clean_thread_url...***

More tips for Disqus found in the Disqus Branch.


### Configuring the Bot using bot.conf


`[TwitterConfig]
# insert your various keys below. No quotes around keys required
consumer_key =
consumer_secret =
access_token =
access_token_secret =
bot_name = ''



[CommentConfig]
# info from disqus or NYT comments api.
# API should be NYT or Disqus. No quotes.
API =
# comments keys should be a comma delimited list. Wrap the keys with quotes
comments_keys = []
filter_object =
#min_comments_found can be between 0 and 100 (pages of 25 comments each). NYT will count comments, while Disqus seems to count pages (each of which contain 25 comments).
min_comments_found =
news_org_url_1 = nytimes
news_org_url_2 = nyti.mes
# requests_get_URL will be the api requests URL eg "http://api.nytimes.com/svc/community/v3/user-content/url.json", or "http://disqus.com/api/3.0/threads/listPosts.json"
#requests_get_URL =

# DISQUS ONLY
# reputation is an integer
reputation =
disqus_forum =



[TextConfig]
# enter your desired font information (eg your news orgs signature font). No quotes required.
font_path =
# I find sans serif is best
font = xxx.ttf
# enter font size. 30 is recommended. Choose a size double what you want, cos later the image with the text gets resampled to a smaller size with antialiasing.
font_size = 30
font_color = ###


``
`[BackgroundConfig]
# enter your desired background information eg. company's signature colors or logo
background_color = ###
# logo size should be 100x100 pixels. If you want to change the size, please experiment using `test_imageModle.py`
`watermark_logo = ./xxx.png```



#### Things to mess with directly in the code:

**Disqus Forum-Specific URL**
In `CommentBot.py` starting at line 65:
`def clean_thread_url(url, forum):`
The instructions are written within the function, and refers to the fact that a news site will format their URLs differently depending on the forum. However, to access the forum comments, the URL grabbed from the tweet needs to be formatted. The specifics of how it needs to be formatted depends on the news organization, and maybe also the specific forum within that news organization. For example, NPR has several Disqus forums.

Most websites use standard story URLs as Disqus thread identifiers, but not _all_ websites do. This method provides a place for applying custom filters that convert Disqus URLs for websites that need it.

**The tweeted message**
In `CommentBot.py`:
`def tweet_reply(comment, tweet):`

Currently the line reads:
`status = "h/t to " + at + " for sharing this article. In case you're interested, here's an anecdote from the article's comments:"`
You may what some other message here, so feel free to reorganize this line as you wish. For example, you may not want to hat-tip (`h/t`).



**Running**  

To set the bot up to run indefinitely but to continually output status information to file run a command like:
- `nohup python -u run.py > nohup.txt &`
- Don't forget to rename `example-bot.config` to just `bot.config` and to complete the relevant fields in the file.

#Funding
This project was funded by a grant from the Tow Center for Digital Journalism to study computational and data journalism in the context of algorithmic accountability reporting.

#Feedback
Email Jennifer A Stark at starkja@umd.edu with any comments, suggestions or questions. You can also find me on Twitter [@_JAStark](https://twitter.com/_jastark)
