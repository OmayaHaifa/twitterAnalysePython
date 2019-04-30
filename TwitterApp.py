import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import matplotlib.pyplot as plt
import string
from geopy.geocoders import Nominatim
import folium


def clean_tweet(tweet) :
    '''
    Remove unncessary things from the tweet
    like mentions, hashtags, URL links, punctuations
    '''
    # remove old style retweet text "RT"
    tweet = re.sub(r'^RT[\s]+', '', tweet)

    # remove hyperlinks
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)

    # remove hashtags
    # only removing the hash # sign from the word
    tweet = re.sub(r'#', '', tweet)

    # remove mentions
    tweet = re.sub(r'@[A-Za-z0-9]+', '', tweet)

    # remove punctuations like quote, exclamation sign, etc.
    # we replace them with a space
    tweet = re.sub(r'[' + string.punctuation + ']+', ' ', tweet)

    return tweet


def get_tweet_sentiment(tweet) :
    '''
    Utility function to classify sentiment of passed tweet
    using textblob's sentiment method
    '''
    # create TextBlob object of passed tweet text
    analysis = TextBlob(clean_tweet(tweet))
    # set sentiment
    if analysis.sentiment.polarity > 0 :
        return 'positive'
    elif analysis.sentiment.polarity == 0 :
        return 'neutral'
    else :
        return 'negative'


def get_tweets(fetched_tweets) :
    '''
    Main function to fetch tweets and parse them.
    '''
    # empty list to store parsed tweets
    tweets = []

    try :
        # parsing tweets one by one
        for tweet in fetched_tweets :
            # empty dictionary to store required params of a tweet
            parsed_tweet = {}

            # saving text of tweet
            parsed_tweet['text'] = tweet.text
            # saving sentiment of tweet
            parsed_tweet['sentiment'] = get_tweet_sentiment(tweet.text)
            # saving location of the tweet
            parsed_tweet['location'] = tweet.author.location
            # saving the author name of the tweet
            parsed_tweet['authorName'] = tweet.author.name
            # appending parsed tweet to tweets list
            tweets.append(parsed_tweet)

        # return parsed tweets
        return tweets

    except tweepy.TweepError as e :
        # print error (if any)
        print("Error : " + str(e))


def main() :
    # keys and tokens from the Twitter Dev Console
    consumer_key = '************'
    consumer_secret = '**********************'
    access_token = '************************'
    access_token_secret = '*****************'

    # attempt authentication
    try :
        # create OAuthHandler object
        auth = OAuthHandler(consumer_key, consumer_secret)
        # set access token and secret
        auth.set_access_token(access_token, access_token_secret)
        # create tweepy API object to fetch tweets
        api = tweepy.API(auth)
    except :
        print("Error: Authentication Failed")

    # call twitter api to fetch tweets
    fetched_tweets = tweepy.Cursor(api.search, q='hard brexit').items(50)
    # calling function to get tweets with attributes like text and the sentiment and the author name
    tweets = get_tweets(fetched_tweets)

    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    positive = (100 * len(ptweets) / len(tweets))

    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    negative = (100 * len(ntweets) / len(tweets))

    # picking neutral tweets from tweets
    netweets = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
    # percentage of neutral tweets
    neutral = 100 - (100 * len(ptweets) / len(tweets)) + (100 * len(ntweets) / len(tweets))
    print(neutral)

    # printing first 5 positive tweets
    print("\n\nPositive tweets:")
    for tweet in ptweets[:10] :
        print("tweet :")
        print(tweet['text'])

    # printing first 5 negative tweets
    print("\n\nNegative tweets:")
    for tweet in ntweets[:10] :
        print("tweet :")
        print(tweet['text'])

    # print graphe
    labels = 'negative', 'positive', 'neutral'
    sizes = [negative, positive, neutral]
    colors = ['red', 'green', 'blue']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')
    plt.savefig('PieChart01.png')
    plt.show()

#print the map
    m = folium.Map()
    for tweet in tweets :
        try :
            geolocator = Nominatim()
            location = geolocator.geocode(tweet['location'])
            print(location.address)
            print((location.latitude, location.longitude))

            if (tweet['sentiment'] == 'positive') :
                folium.Marker(
                    location=[location.latitude, location.longitude],
                    popup='Timberline Lodge',
                    icon=folium.Icon(color='green')
                ).add_to(m)

            if (tweet['sentiment'] == 'negative') :
                folium.Marker(
                    location=[location.latitude, location.longitude],
                    popup='Timberline Lodge',
                    icon=folium.Icon(color='red')
                ).add_to(m)

            if (tweet['sentiment'] == 'neutral') :
                folium.Marker(
                    location=[location.latitude, location.longitude],
                    popup='Timberline Lodge',
                    icon=folium.Icon(color='blue')
                ).add_to(m)
        except :
            print("An exception occurred")
    m.save('index.html')


if __name__ == "__main__" :
    # calling main function
    main()
