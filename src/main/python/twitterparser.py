import tweepy
from database import *
from twitter import *
import re


class TwitterParser:

    consumer_key = "FEmg7RKtzQVs1xw9WKIWPBSKC"
    consumer_secret = "TUwJZm3YjzFniTO5YKq0q60HMchdmm8GTGruiUXeFcXCDtuXeo"
    access_token = "220720911-rQip850ZUb28PwkCa9Zkw3MqJVPzHocp1aVvpY6n"
    access_token_secret = "LwkBILLYzqEn2h3FbjoMxpGcuna8RTYIomF3WnDsBHYuS"
    auth = None
    api = None
    m = re.compile("(RT @.*?: )(.*)")
    handlers = []
    log = 'beta.log'

    def __init__ (self, consumer_key=None, consumer_secret=None, log=None):
        if consumer_key and consumer_secret:
            self.consumer_key = consumer_key
            self.consumer_secret = consumer_secret
        if log:
            self.log = log
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)

        #create a logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # create a file handler
        handler = logging.FileHandler(self.log)
        handler.setLevel(logging.INFO)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(handler)

    def authorize(self, access_token=None, access_token_secret=None):
        '''Authorize the Parser with the twitter API'''
        if access_token and access_token_secret:
            self.access_token = access_token
            self.access_token_secret = access_token_secret
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)
        self.logger.info('Authorized with Twitter')

    def search_tweets(self, q, rpp=100):
        '''Return a list of query results from the parameter, q'''
        return self.api.search(q, rpp=rpp)

    def get_user_tweets(self, user, pages=10):
        '''Return first 200 tweets by the specified user'''
        user_object = self.get_user(user)
        tweets = []
        for page in range(1, pages+1):
            results = user_object.timeline(page=page)
            tweets += [r for r in results]
        return list(set(tweets))

    def get_real_url(self, url):
        r = requests.get(url)
        return r.url

    def get_tweet_urls(self, tweet):
        urls = []
        if tweet.entities["urls"]:
            urls += [ url["url"] for url in tweet.entities["urls"]]
        return urls

    def get_user(self, user):
        '''Return the twitter account user'''
        return self.api.get_user(user)

    def get_user_mentions(self, tweets, target_mentions):
        '''Return tweets that mention the target people'''
        target_mentions = [x.lower() for x in target_mentions]
        match_tweets = []
        for tweet in tweets:
            mentions = tweet.entities["user_mentions"]
            if mentions:
                for each_mention in mentions:
                    if each_mention["screen_name"].lower() in target_mentions:
                        match_tweets.append(tweet)
        return match_tweets

    def count_mentions(self, user):
        tweets = self.get_user_tweets(user)
        count_mentions = {}
        for tweet in tweets:
            mentions = tweet.entities["user_mentions"]
            if mentions:
                for each_mention in mentions:
                    name = each_mention["screen_name"]
                    if count_mentions.has_key(name):
                        count_mentions[name] += 1
                    else:
                        count_mentions[name] = 1
        return count_mentions


    def add_user_tweets(self, user):
        #save the original author
        user = self.get_user(user)
        name = user.name
        screen_name = user.screen_name
        ta = TwitterAccount.objects(screen_name=screen_name).first()
        if not ta:
            ta = TwitterAccount(name=name, screen_name=screen_name)
            ta.save()

        tweets = self.get_user_tweets(screen_name)
        retweeted = False
        for tweet in tweets:
            #check if its a reply tweet, then skip
            if tweet.in_reply_to_screen_name:
                continue
            if self.m.match(tweet.text):
                try:
                    tweet.retweeted_status
                    retweet_verified = True
                except AttributeError:
                    self.logger.warn('Re-tweet is not an actual retweet, {0}'.format(tweet.text))
                    retweet_verified = False
            if self.m.match(tweet.text) and retweet_verified:
                #save the founded author
                try:
                    user = tweet.retweeted_status.author
                except AttributeError:
                    self.logger.warn('Re-tweet is not an actual retweet, ')
                name = user.name
                screen_name = user.screen_name

                rt_ta = TwitterAccount.objects(screen_name=screen_name).first()
                if not rt_ta:
                    rt_ta = TwitterAccount(name=name, screen_name=screen_name)
                    rt_ta.save()

                author = rt_ta
                text = tweet.retweeted_status.text
                entities = tweet.retweeted_status.entities
                created_at = tweet.created_at
                tw = Tweet.objects(text=text, author=author).first()
                if not tw:
                    tw = Tweet(text=text, entities=entities, author=author, created_at=created_at)
                    tw.save()

                    rt_ta.tweets.append(tw)
                    rt_ta.save()

                retweeted = True

            text = tweet.text
            author = ta
            entities = tweet.entities
            created_at = tweet.created_at
            if retweeted:
                retweet_author = rt_ta
                retweet = tw
            else:
                retweet_author = None
                retweet = None

            tw = Tweet.objects(text=text, author=author).first()
            if not tw:
                tw = Tweet(text=text, entities=entities, author=author,
                           retweeted=retweeted, retweet_author=retweet_author,
                           retweet=retweet, created_at=created_at)
                tw.save()
                # print text, author.name

                ta.tweets.append(tw)
                ta.save()

            retweeted = False

    def count_ref(self, source, target):
        s_user = TwitterAccount.objects(screen_name=source).first()
        s_tweets = s_user.tweets
        total = 0
        for each in s_tweets:
            user_mentions = each.entities["user_mentions"]
            if each.retweeted and each.retweet_author.screen_name == target:
                total += 1
                print each.text

            elif user_mentions:
                for each_mention in user_mentions:
                    if each_mention["screen_name"] == target:
                        total += 1
                        print each.text

        return total

    def run(self, handlers):
        self.logger.info('Started Twitter Crawler')
        print "Running Twitter Crawler"
        self.handlers = handlers
        for each in self.handlers:
            self.add_user_tweets(each)
        self.logger.info('Done Twitter Crawler')
        return True


if __name__ == '__main__':
    host = "ds053380.mongolab.com:53380"
    dbName = "twitterparser"
    people = ["DaliaHatuqa", "DanielSeidemann", "galberger"]

    data = Database(host=host, dbName=dbName)
    data.connect(username="admin", password="admin")

    twitter = TwitterParser()
    twitter.authorize()
    twitter.run(people)



