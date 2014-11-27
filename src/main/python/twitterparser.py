import tweepy
import requests
from database import *
from twitter import *
import re


class TwitterParser:
    '''
    Twitter Parser that uses Tweepy API to parser tweets.
    Need to instialize the instance of TwitterParser, then authorize the API.
    E.g.
    #connect to database
    people = ["DaliaHatuqa"] #handlers
    data = Database(host=host, dbName=dbName)
    data.connect(username="admin", password="admin")
    twitter = TwitterParser(data=data)
    twitter.authorize()
    twitter.run(people)
    '''

    consumer_key = "FEmg7RKtzQVs1xw9WKIWPBSKC"
    consumer_secret = "TUwJZm3YjzFniTO5YKq0q60HMchdmm8GTGruiUXeFcXCDtuXeo"
    access_token = "220720911-rQip850ZUb28PwkCa9Zkw3MqJVPzHocp1aVvpY6n"
    access_token_secret = "LwkBILLYzqEn2h3FbjoMxpGcuna8RTYIomF3WnDsBHYuS"
    auth = None
    api = None
    data = None
    retweet_regex = re.compile("(RT @.*?: )(.*)")
    handlers = []
    log = 'beta.log'
    logger = None

    def __init__ (self, consumer_key=None, consumer_secret=None, log=None,
                                                                     data=None, logger=None):
        if logger:
            self.logger = logger
        if consumer_key and consumer_secret:
            self.consumer_key = consumer_key
            self.consumer_secret = consumer_secret
        if log:
            self.log = log
        if not data:
            raise Exception('No Connection To Database, \
                                       need to pass in the database connection')
        self.data = data
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)

    def authorize(self, access_token=None, access_token_secret=None):
        '''Authorize the Parser with the twitter API'''
        if access_token and access_token_secret:
            self.access_token = access_token
            self.access_token_secret = access_token_secret
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)
        if self.logger:
            self.logger.info('Authorized with Twitter')

    def search_tweets(self, q, rpp=100):
        '''Return a list of query results from the parameter, q'''
        return self.api.search(q, rpp=rpp)

    def get_user_tweets(self, user, pages=10):
        '''Return first 200 tweets by the specified user'''
        user_object = self.get_user(user)
        if not user_object:
            return []
        tweets = []
        for page in range(1, pages+1):
            try:
                results = user_object.timeline(page=page)
            except tweepy.TweepError:
                #limit exeeded
                results = []
            tweets += [r for r in results]
        return list(set(tweets))

    def get_real_url(self, url):
        '''Reveal the real url of a short urls'''
        r = requests.get(url)
        return r.url

    def get_tweet_urls(self, tweet):
        '''Return all tweets contained inside a tweet'''
        urls = []
        if tweet.entities["urls"]:
            urls += [ url["url"] for url in tweet.entities["urls"]]
        return urls

    def get_user(self, user):
        '''Return the twitter account user'''
        try:
            return self.api.get_user(user)
        except tweepy.TweepError:
            if self.logger:
                self.logger.warn('User not found, user: {0}'.format(user))
            return None

    def get_user_mentions(self, tweets, target_mentions):
        '''Return tweets that mention the target people'''
        target_mentions = [x.lower() for x in target_mentions]
        match_tweets = []
        for tweet in tweets:
            mentions = tweet.entities["user_mentions"]
            if not mentions:
                continue
            for each_mention in mentions:
                if each_mention["screen_name"].lower() in target_mentions:
                    match_tweets.append(tweet)
        return match_tweets

    def count_mentions(self, user):
        '''Return the number of mentions for a user, in a dictionary'''
        ta = TwitterAccount.objects(screen_name=user).first()
        if not ta:
            return {}
        tweets = ta.tweets
        count_mentions = {}
        for tweet in tweets:
            mentions = tweet.entities["user_mentions"]
            if not mentions:
                continue
            for each_mention in mentions:
                name = each_mention["screen_name"]
                if name == user:
                    continue
                if count_mentions.has_key(name):
                    count_mentions[name] += 1
                else:
                    count_mentions[name] = 1
        return count_mentions


    def add_user_tweets(self, user):
        '''Recursively add all tweets of a given User'''
        #save the original author
        user = self.get_user(user)
        if not user:
            return None
        name = user.name
        screen_name = user.screen_name
        twitteraccount_meta = {"user": user, "name": name,
                                                     "screen_name": screen_name}

        ta = self.data.add_twitteraccount(twitteraccount_meta)
        tweets = self.get_user_tweets(screen_name)

        retweeted = False
        for tweet in tweets:
            #check if its a reply tweet, then skip
            if tweet.in_reply_to_screen_name:
                continue
            if self.retweet_regex.match(tweet.text):
                try:
                    tweet.retweeted_status
                    retweet_verified = True
                except AttributeError:
                    if self.logger:
                        self.logger.warn( \
                            'Re-tweet is not an actual retweet, {0}'\
                                            .format(tweet.text.encode('utf-8')))
                    retweet_verified = False
            if self.retweet_regex.match(tweet.text) and retweet_verified:
                #save the founded author
                try:
                    user = tweet.retweeted_status.author
                except AttributeError:
                    if self.logger:
                        self.logger.warn('Re-tweet is not an actual retweet, ')
                name = user.name
                screen_name = user.screen_name
                twitteraccount_meta = {"name": name, "screen_name": screen_name}

                rt_ta = self.data.add_twitteraccount(twitteraccount_meta)

                author = rt_ta
                text = tweet.retweeted_status.text
                entities = tweet.retweeted_status.entities
                created_at = tweet.created_at

                tweet_meta = {"text": text, "entities": entities,
                                 "author": author, "created_at": created_at}
                tw = self.data.add_tweet(tweet_meta)

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
            tweet_meta = {"text": text, "author": author, "entities": entities,
                          "created_at": created_at, "retweeted": retweeted,
                          "retweet": retweet, "retweet_author": retweet_author}
            tw = self.data.add_tweet(tweet_meta)

            retweeted = False

    def count_ref(self, source, target):
        '''
        Count the relation between two USERS, e.g. how many times the source
        has referenced the target USER
        '''
        s_user = TwitterAccount.objects(screen_name=source).first()
        if not s_user:
            if self.logger:
                self.logger.info( \
                    'TwitterAccount does not exists, source: {0}'\
                                                                .format(source))
            return 0
        s_tweets = s_user.tweets
        total = 0
        for each in s_tweets:
            user_mentions = each.entities["user_mentions"]
            if each.retweeted and each.retweet_author.screen_name == target:
                total += 1

            elif user_mentions:
                for each_mention in user_mentions:
                    if each_mention["screen_name"] == target:
                        total += 1

        return total

    def count_tweets_day(self, user):
        count_map = {}
        ta = TwitterAccount.objects(screen_name=user).first()
        if not ta:
            return {}
        tweets = ta.tweets
        for each in tweets:
            if not count_map.get(each.created_at.date()):
                count_map[each.created_at.date()] = 1
                continue
            count_map[each.created_at.date()] += 1

        print count_map
        return count_map


    def run(self, handlers):
        '''Run the twitter_parser'''
        if self.logger:
            self.logger.info('Started Twitter Crawler')
        self.handlers = handlers
        for each in self.handlers:
            self.add_user_tweets(each)
        if self.logger:
            self.logger.info('Done Twitter Crawler')
        return True


if __name__ == '__main__':
    host = "ds053380.mongolab.com:53380"
    dbName = "twitterparser"
    # people = ["DaliaHatuqa", "DanielSeidemann", "galberger"]

    data = Database(host=host, dbName=dbName)
    data.connect(username="admin", password="admin")

    twitter = TwitterParser(data=data)
    twitter.authorize()
    # twitter.run(people)
    print twitter.count_tweets_day('DaliaHatuqa')



