# Comment Bot
This repository contains the code to run the [AnecbotalNYT](https://twitter.com/anecbotalnyt) News Bot on Twitter in the Master Branch.  It's being open sourced as a reference implementation for other news bots that listen and respond on Twitter.

The Twitterbot example tweeting Disqus comments is [__TestB0t__](https://twitter.com/__TestB0t__), and the code is in the Anecbotal_Disqus branch. It has only one tweet. I deleted the rest while testing.

For more information on News Bots see the following article:
- T. Lokot and N. Diakopoulos. News Bots: Automating News and Information Dissemination on Twitter. Digital Journalism. 2016. [PDF](http://www.nickdiakopoulos.com/wp-content/uploads/2011/07/newsbots_final.pdf)

This project makes extensive use of the code from the [CommentIQ repository](https://github.com/comp-journalism/commentIQ), but has been repurposed.

### Editorial Transparency


### Setup
If you'd like to run this bot (or repurpose it) first clone the repository to your system.

**Keys**  
Rename `example-bot.conf` to `bot.conf` and add your Twitter API keys and NYT Community API keys (more instructions follow).

To sign up for a Twitter API key and App follow the instructions here: http://www.compjour.org/tutorials/getting-started-with-tweepy/ to create a Twitter app. You need to do this in order to get the necessary authentication tokens to log in to Twitter programmatically. Put these tokens in the `bot.conf` file. Make sure to do all this with your twitter-bot account.

To sign up for NYT Community API Keys see the documentation: http://developer.nytimes.com/docs/community_api/The_Community_API_v3/. Also put these tokens in the `bot.conf` file.

To sign up for Disqus API keys, sign in to Disqus (if you're using this bot for Disqus comments, I am assuming your organization already has an account), and then register a new App with the

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
- Open `requirements.txt` in a text editor and comment out `python==2.7` line
- Type `pip install -r requirements.txt`, and you should see everything successfully installing.
- To check you have the requirements installed, you can type `pip freeze` which will print the installed modules to your screen.


**Running**  
To set the bot up to run indefinitely but to continually output status information to file run a command like:
- `nohup python -u run.py > nohup.txt &` to run the NYT version in `Master`, or
- `nohup python -u runDisqus.py > nohup.txt &` to run the version that uses Disqus comment system in `Branch Anecbotal_Disqus`..

And to quit it type:
- type on the command line: `ps aux | grep python`
- read the left-most digit
- type `kill -9 xxxx` replacing the `xxxx` with those digits


### Testing

**Twitter Bot**
- Keep Bot Private and put in the "Bio" to not follow, just so people know exactly who and what you are.
- Reduce [CommentConfig] `min_comments_found = 50` comment limit to a lower number (like 10 or 50) so when testing it will tweet something sooner.
- Stop App to iterate code, start App to test, watch `nohup.txt` populate to check for errors and know when it's tweeted. Check the tweet, stop App, re-code... etc etc and delete tweet so as not to annoy anyone ;)
- Once happy, reconfig [CommentConfig] to 100 (or whatever you like), undo twitterbot privacy and edit Bio.

**Tips and Tricks working with Disqus queries**
To check you have the correct forum name, use the Disqus console https://disqus.com/api/console/#!/ which you can access after registering your App with Disqus. Here, fill in:
- `Application` field with your App name (secret or public doesn't _seem_ to matter)
- `Headers and Methods` with `GET` and from the dropdown menu, under `Posts` select `list`. In the next field, select `json`
- `Parameters` with `forum` = `npr-news` or the forum name of your choice;
- New line of `Parameters` with `thread:link` = `http.....` or real example of a link you want to be able to get comments from
- Then press the `Send Request` button.

You'll know it worked when you get a nice JSON response. Now you can enter that forum name into the [CommentConfig] `disqus_forum` section. If it doesn't work, you likely have something wrong with the **forum** selected.

**More Troubleshooting**
When running the App and watching the `nohup.txt` output when testing, you may see a line :
`Invalid argument, 'thread': Unable to find thread 'link:http://www.npr.org/2016/04/22/475261626/we-know-nothing-about-jon-snow-as-game-of-thrones-returns'`
This likely means your forum doesn't quite match with the URLs passed. This happens with NPR because it is difficult to filter the forum based on the URL alone. When a URL passes the URL filter, it then tries to access the named Disqus forum associated with the article URL. If the forum name in the HTML source code doesn't match the one specified in your code, it will print this error. Practically, this does not _really_ matter: the bot will continue to search tweets and comments until it finds one to tweet.

You can check a wayward link and its forum by copying the link from `nohup.txt` into a fresh browser tab, and viewing the source. Then search `Disqus_` and it will take you the part where the forum is named -> look for `DATA-SHORTNAME='NPRED'` for example. The `shortname` is the name of the **forum**. You can then check this by pasting the URL into the Disqus Console described above, and putting that *shortname* into the *Forum* field and see if you get a pretty JSON output or not.

Another error I see in the `nohup.txt` is an `Exception  string indices must be integers`. I am not sure where this stems from, but the code still trundles on until it finds a comment it can tweet. Again, it is not a terrible error, practically speaking.

**Testing Image Output**
Before you test the Bot itself, you might like to get your comment image fixed up just how you like it. To do that you need `bot.conf` and `test_imageModule.py`. Once you have edited the `bot.conf` information with items relevant to testing the image module (including `[TextConfig]` and `[BackgroundConfig]`), you can run the test from the command line using: `python test_imageModle.py`. The image will be output into the same directory as a `.png`.

I recommend only editing the `bot.conf`. However, if you do make any edits to the `image_module` when testing your image output, make sure to reflect those changes in the `image_module` section in the `disqusAPI_Bot.py` code.

**nohup.txt Print Statements**
This one shows: Time, Disqus Comment API count, the Disqus comments found as JSON, the number of comments (here 100), and the tweet API count as `ntweets`. The tweets will count to 10 before it will even consider finding a comment to tweet. You can see the `forum` is `npr-news`.
```
-----
18:40:45
comment API: 1
[{u'isHighlighted': False, u'isFlagged': False, u'forum': u'npr-news', u'parent': 2638796769, u'author': {u'username': u'npr-fef29185ff9a494c545a35706b2a74ee', u'about':...
Number of comments:  100
ntweets: 1
```

Here is an example of one of those errors where the **forum** is incorrect. However, it still seems able to count the number of Disqus comments from the article.
```
-----
18:40:57
comment API: 2
Invalid argument, 'thread': Unable to find thread 'link:http://n.pr/1SGhfVj'
Number of comments:  76
ntweets: 2
```

Here is an example of the `Exception`.
```
18:44:04
comment API: 11
Invalid argument, 'thread': Unable to find thread 'link:http://n.pr/21b00M3'
Number of comments:  76
ntweets: 10
Exception  string indices must be integers
```

Here is an example of what happens when it tweets a comment.
- The Disqus Comment API count is 21 (limit is 1000 per hour).
- The Comments (I've only copied a small part on here).
- `Number of comments` found was 100 for that article.
- `ntweets` Tweet API hits is now 15.
- Then it `prints` a bunch of numbers. These are the Disqus `Author: reputation` scores for all the Authors who posted a `Parent:None` level (top level) comment. This might be useful when you're trying to assess what reputation score you want as a threshold for your bot to decide whether or not to consider tweeting their comment. You can see the range is large. The `bot.conf` is currently set to `2`. Once the comment/author has passed `parent` and `reputation`, the comment has to be at least 25 characters long to be passed to the text scoring. The number of surviving comments is printed on the line `num comments`. Here only 2 comments survived.
- The message on `BeautifulSoup` is worth noting. This only comes up the first time the bot finds a comment it wants to tweet.
- `top comment score: 0.5` is the result of the `TextStatistics.py` and `TextUtils.py`. The comment has to score over a certain threshold to be tweeted.
- Finally, the actual comment to be tweeted is printed.

```
18:45:59
comment API: 21
[{u'isHighlighted': False, u'isFlagged': False, u'forum': u'npr-news', u'parent': 2634617226, u'author': {u'username': u'npr-86f38ed29df93b4e255058cf574085b1', u'abou...
Number of comments:  100
ntweets: 15
1.232493
2.277839
/Users/jenniferstark/anaconda/envs/commentbot/lib/python2.7/site-packages/bs4/__init__.py:166: UserWarning: No parser was explicitly specified, so I'm using the best available HTML parser for this system ("html.parser"). This usually isn't a problem, but if you run this code on another system, or in a different virtual environment, it may use a different parser and behave differently.

To get rid of this warning, change this:

 BeautifulSoup([your markup])

to this:

 BeautifulSoup([your markup], "html.parser")

  markup_type=markup_type))
0.931214
1.22433
3.614409
1.232124
4.499422
1.344584
1.132474
-21.187916
1.186571
1.244168
-21.187916
1.490963
1.201514
4.696984
-21.187916
num comments: 2
top comment score: 0.5
[u'"Don\'t blame the brains blame the people who', u"ignore science, because it doesn't fit with their", u'preconceived notions of reality. \u201cThere is a cult', u'of ignora...
```

- If no comments survive `parent`, `reputation` and being at least 25 characters long, the `num comments` line will read `num comments: 0` and after that line you'll get an `Exception  list index out of range` because you're passing a list of 0 comments to the text processing code. It's ok, though, because the bot will continue to search for comments...

## Feedback
As always, please do contact me at starkja@umd.edu with any comments, suggestions or questions! You can also find me on Twitter [@_JAStark](https://twitter.com/_jastark)
