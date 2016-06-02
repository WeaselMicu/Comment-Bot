**More Troubleshooting**
*Invalid argument, 'thread': Unable to find thread*
When running the App and watching the `nohup.txt` output when testing, you may see a line :
`Invalid argument, 'thread': Unable to find thread 'link:http://www.npr.org/2016/04/22/475261626/we-know-nothing-about-jon-snow-as-game-of-thrones-returns'`
This likely means your forum doesn't quite match with the URLs passed. This happens with NPR (and perhaps other news sites) because it is difficult to filter the forum based on the URL alone. When a URL passes the URL filter (in `bot.conf [CommentConfig] news_org_url_1 news_org_url_2`), it then tries to access the named Disqus forum associated with the article URL. If the forum name in the HTML source code doesn't match the one specified in your code, it will print this error. Practically, this does not _really_ matter: the bot will continue to search tweets and comments until it finds one to tweet.

You can check a wayward link and its forum by copying the link from `nohup.txt` into a fresh browser tab, and viewing the source. If you search for `Disqus_` in the source, it will take you the part where the forum is named -> look for `DATA-SHORTNAME='NPRED'` for example. The `shortname` is the name of the **forum**. You can then check this by pasting the URL into the Disqus Console described in the main README.md (https://disqus.com/api/console/#!/), and putting that *shortname* into the *Forum* field and see if you get a pretty JSON output or not.

*Exception  string indices must be integers*
Another error I see in the `nohup.txt` is an `Exception  string indices must be integers`. I am not sure where this stems from, but the code still trundles on until it finds a comment it can tweet. Again, it is not a terrible error, practically speaking.


**nohup.txt Print Statements**
Below, the `filter_object` matched on `npr` so the code continued to collect the url in the tweet. However, the URL does not match `news_org_url_1` or `news_org_url_2`.
```
-----
https://npr.codes/profile-phil-shannon-support-engineer-327900211168
Not url 1 or 2
-----
```

Below is an example of one of those errors where the **forum** is incorrect. It prints the URL, prints which comments API it is using (Disqus), Time, Comment API count (1), the attempt to gather comments (but prints the `Invalid argument` instead), and the number of comments found (76). Even though the forum is incorrect, it can still count the number of Disqus comments from the article.  You can see the `forum` is `npr-news`.
```
-----
http://n.pr/1RXV21k
API = Disqus, done requests.get
12:29:49
comment API: 1
{u'code': 2, u'response': u"Invalid argument, 'thread': Unable to find thread 'link:http://n.pr/1RXV21k'"}
Number of comments found: 76
```

Below is an example of when the forum did not match, but the number of comments _was_ over the `min_comments_found` threshold.
```
-----
http://www.npr.org/2016/06/02/479636188/songs-we-love-field-mouse-the-mirror
API = Disqus, done requests.get
17:55:30
comment API: 19
{u'code': 2, u'response': u"Invalid argument, 'thread': Unable to find thread 'link:http://www.npr.org/2016/06/02/479636188/songs-we-love-field-mouse-the-mirror'"}
Number of comments found: 133
ntweets: 1
Exception  string indices must be integers
-----
```

Below is an example of when everything is right (forum name etc) but the article is so new it has no comments yet:
```
http://www.npr.org/2016/06/02/480487252/top-u-s-diplomat-outlines-complicated-issues-facing-u-s-china
API = Disqus, done requests.get
17:56:44
comment API: 28
{u'cursor': {u'prev': None, u'hasNext': False, u'next': u'0:0:0', u'hasPrev': False, u'total': None, u'id': u'0:0:0', u'more': False}, u'code': 0, u'response': []}
Number of comments found: 0
-----
```

Below is an example of what happens when it tweets a comment.
- The Disqus Comment API count is 17 (limit is 1000 per hour).
- The Comments (I've only copied a small part on here).
- `Number of comments` found was 100 for that article.
- `ntweets` Tweet API hits is now 2.
- Then it `prints` a bunch of numbers. These are the Disqus `Author: reputation` scores for all the Authors who posted a `Parent:None` level (top level) comment. This might be useful when you're trying to assess what reputation score you want as a threshold for your bot to decide whether or not to consider tweeting their comment. You can see the range is large. The `bot.conf` is currently set to `2`. Once the comment/author has passed `parent` and `reputation`, the comment has to be at least 25 characters long to be passed to the text scoring. The number of surviving comments is printed on the line `num comments`. Here only 3 comments survived.
- The message on `BeautifulSoup` is worth noting. This only comes up the first time the bot finds a comment it wants to tweet.
- `top comment score: 0.5` is the result of the `TextStatistics.py` and `TextUtils.py`. The comment has to score over a certain threshold to be tweeted.
- Finally, the actual comment to be tweeted is printed.

```
http://www.npr.org/2016/05/31/480073262/u-s-mexico-border-sees-resurgence-of-central-americans-seeking-asylum
API = Disqus, done requests.get
12:33:44
comment API: 17
{u'cursor': {u'prev': None, u'hasNext': True, u'next': u'1464706666693067:0:0', u'hasPrev': False, u'total': None, u'id': u'1464706666693067:0:0', u'more': True}, u'code': 0, u'res...
Number of comments found: 100
ntweets: 2
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
num comments: 3
top comment score: 0.5
[u'"Don\'t blame the brains blame the people who', u"ignore science, because it doesn't fit with their", u'preconceived notions of reality. \u201cThere is a cult', u'of ignora...
```

- If no comments survive `parent`, `reputation` and being at least 25 characters long, the `num comments` line will read `num comments: 0` and after that it should return to continue listening to the twittershere. If it does _not_ return for whatever reason, you will get a line that reads `Exception  list index out of range` because it passed a list of 0 comments to the text processing code. It's ok, though, because the bot will continue to search for comments...
