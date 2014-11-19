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

    def __init__ (self, consumer_key=None, consumer_secret=None):
        if consumer_key and consumer_secret:
            self.consumer_key = consumer_key
            self.consumer_secret = consumer_secret
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)

    def authorize(self, access_token=None, access_token_secret=None):
        '''Authorize the Parser with the twitter API'''
        if access_token and access_token_secret:
            self.access_token = access_token
            self.access_token_secret = access_token_secret
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)

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

    def count_mentions(self, tweets):
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


if __name__ == '__main__':
    m = re.compile("(RT @.*?: )(.*)")

    host = "ds053380.mongolab.com:53380"
    dbName = "twitterparser"
    data = Database(host=host, dbName=dbName)
    data.connect(username="admin", password="admin")
    twitter = TwitterParser()
    twitter.authorize()

    #save the original author
    user = twitter.get_user("DaliaHatuqa")
    name = user.name
    screen_name = user.screen_name
    ta = TwitterAccount(name=name, screen_name=screen_name)
    ta.save()

    print "Done"

    tweets = twitter.get_user_tweets("DaliaHatuqa")
    retweeted = False
    for tweet in tweets:
        if m.match(tweet.text):
            #save the founded author
            user = tweet.retweeted_status.author
            name = user.name
            screen_name = user.screen_name
            
            rt_ta = TwitterAccount.objects(screen_name=screen_name).first()
            if not rt_ta:
                rt_ta = TwitterAccount(name=name, screen_name=screen_name)
                rt_ta.save()

            print "Saved rt_ta"

            author = rt_ta
            text = tweet.retweeted_status.text
            entities = tweet.retweeted_status.entities
            tw = Tweet(text=text, entities=entities, author=author)
            tw.save()

            print "Saved rt_tw"

            rt_ta.tweets.append(tw)
            rt_ta.save()

            print "Saved rt_ta.append"

            retweeted = True
        
        text = tweet.text
        author = ta      
        entities = tweet.entities
        if retweeted:
            retweeted_author = rt_ta
            retweet = tw
        else:
            retweeted_author = None
            retweet = None

        tw = Tweet(text=text, entities=entities, author=author,
                   retweeted=retweeted, retweeted_author=retweeted_author, 
                   retweet=retweet)
        tw.save()

        ta.tweets.append(tw)
        ta.save()

        retweeted = False
    

