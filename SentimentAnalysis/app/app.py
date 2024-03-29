import re
import tweepy
import googletrans
from googletrans import Translator
from tweepy import OAuthHandler
from textblob import TextBlob
translator = Translator()


class TwitterClient(object):
    def __init__(self):
        consumer_key = '3nPoEBxFd6Z6SH3xxwChlmDQb'
        consumer_secret = '9b0ecGsPCNCx5cEaiBTtF72C00pw11FHvQY9lGlVM3T8QKMlIO'
        access_token = '1201071936387735552-jrqfXu56Bgnh75Tok9yZoWaBfxGIjb'
        access_token_secret = 'Kb4V0CRKdkfI57YhmUUXSNbYtOX47KGo2xxFAAAyhISbo'
        try:
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(self.auth)
        except:
            print("Error:Authentication Failure")

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=10):
        tweets = []
        try:
            fetched_tweets = self.api.search(q=query, count=count)
            for tweet in fetched_tweets:
                langlist = googletrans.LANGUAGES
                tweetlang = translator.detect(tweet.text)
                if tweetlang.lang in langlist:
                    if tweetlang != "en":
                        transtweet = translator.translate(tweet.text, src=tweetlang.lang, dest='en')
                    else:
                        transtweet = tweet
                else:
                    transtweet = tweet

                parsed_tweet = {'text': tweet.text, 'trtweet': transtweet.text, 'sentiments': self.get_tweet_sentiment(transtweet.text)}

                # tweetid = tweet._json['id']
                # self.api.update_status(parsed_tweet['sentiments']+'@murli_wala', tweetid)
                # screenname = tweet._json['user']['screen_name']
                # self.api.update_status(status='@'+screenname+' '+parsed_tweet['sentiments'], in_reply_to_status=tweetid, auto_populate_reply_metadata=True)

                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
            for x in tweets:
                print("Tweet : ", x['text'])
                print("Translated_Tweet : ", x['trtweet'])
                print("Sentiment :", x['sentiments'])
            return tweets
        except tweepy.TweepError as e:
            print("Error : " + str(e))


def main():
    api = TwitterClient()
    tweets = api.get_tweets(query='murli_wala', count=20)
    ptweets = [tweet for tweet in tweets if tweet['sentiments'] == 'positive']
    print("Positive tweets percentage: {} %".format(100 * len(ptweets) / len(tweets)))
    ntweets = [tweet for tweet in tweets if tweet['sentiments'] == 'negative']
    print("Negative tweets percentage: {} %".format(100 * len(ntweets) / len(tweets)))
    print("Neutral tweets percentage: {} % ".format(100 * (len(tweets) - len(ntweets + ptweets)) / len(tweets)))

    print("\n\nPositive tweets:")
    for tweet in ptweets[:10]:
        print(tweet['text'])

    print("\n\nNegative tweets:")
    for tweet in ntweets[:10]:
        print(tweet['text'])


if __name__ == "__main__":
    main()
