import tweepy


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


if __name__ == '__main__':
    from requests import get

    twitter = TwitterParser()
    twitter.authorize()

    tweets = twitter.get_user_tweets("AlJazeera")
