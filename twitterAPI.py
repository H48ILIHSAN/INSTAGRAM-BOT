import argparse
import tweepy

from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--consumer_key', dest='consumer_key', type=str, required=True)
parser.add_argument('-s', '--consumer_secret', dest='consumer_secret', type=str, required=True)
args = parser.parse_args()

auth = tweepy.OAuthHandler(args.consumer_key, args.consumer_secret)
redirect_url = auth.get_authorization_url()
print(redirect_url)
print('Access Token:')
auth.get_access_token(input())
with open(Path(__file__).resolve().parent.joinpath('config/twitterAPI.txt'), 'w') as outfile:
    outfile.write('\n'.join([args.consumer_key,args.consumer_secret,auth.access_token,auth.access_token_secret]))
print('TWITTER HAS CONNECTED')