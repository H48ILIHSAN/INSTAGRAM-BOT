import codecs
import os
from pprint import pprint
import subprocess
import urllib.request
import tweepy
import time

from pathlib import Path
from instagram_private_api import Client
from collections import namedtuple
from xml.dom.minidom import parseString
from urllib.parse import urlparse

INSTA_USERNAME = 'jkt48.zee'
INSTA_ID       = '9144760144'

def absPath(path):
    return str(Path(__file__).resolve().parent.joinpath(path))

def fetchStory():
    with open(absPath('config/instaAPI.txt')) as instaData:
        kuki = codecs.decode(instaData.read().encode(), 'base64')
    instaAPI = Client(INSTA_USERNAME,'', cookie=kuki)
    return instaAPI.user_story_feed(INSTA_ID)

def parseStory(userInfo):
    if userInfo['reel'] is None: return[0]
    Data = namedtuple('Story', ['type','taken_at','media_url','audio_url'])
    mediaURL = []
    for media in userInfo['reel']['items']:
        takenTS = int(media.get('taken_at'))
        if 'video_version' in media:
            videoManifest = parseString(media['video_dash_manifest'])
            videoPeriod   = videoManifest.documentElement.getElementsByTagName('Period')
            Representation= videoPeriod[0].getElementsByTagName('Representation')
            videoURL      = Representation[0].getElementsByTagName('BaseURL')[0].childNodes[0].nodeValue
            audioElement  = Representation.pop()
            if audioElement.getAttribute("mimeType") == "audio/mp4":
                audioURL  = audioElement.getElementsByTagName('Base URL')[0].childNodes[0].nodeValue
                mediaURL.append(Data('video', takenTS, videoURL, audioURL))
            else:
                mediaURL.append(Data('video', takenTS, videoURL, None))
        else:
            mediaURL.append(Data('picture', takenTS, media['image_versions2']['candidates'][-1]['url'], None))
    return mediaURL

def getStory(storyGET):
    with open(absPath('config/instaAPI.txt')) as instaData:
        kuki = codecs.decode(instaData.read().encode(), 'base64')
    storyGET = Client(INSTA_USERNAME,'', cookie=kuki)
    storyData = storyGET.user_reel_media(INSTA_ID)
    counter = 0
    if storyData['items'] is not None:
        counter = storyData['media_count']
        for i in storyData['items']:
            if i["media_type"] == 1:
                url = i['image_versions2']['candidates'][0]['url']
                end = absPath('assets/story.mp4')
                urllib.request.urlretrieve(url, end)
            elif i["media_type"] == 2:
                url = i['video_versions'][0]['url']
                end = absPath('assets/story.mp4')
                urllib.request.urlretrieve(url, end)

def getTwitAPI():
    with open(absPath('config/twitterAPI.txt')) as twitData:
        ckey, csecret, tkey, tsecret = twitData.read().split('\n')
    twitAuth = tweepy.OAuthHandler(ckey, csecret)
    twitAuth.set_access_token(tkey, tsecret)
    return tweepy.API(twitAuth)

def twitMedia(filePath):
    filePath = absPath('assets/story.mp4')
    TwitAPI = getTwitAPI()
    print('UPLOADING {}...'.format(filePath))
    try:
        Twit = TwitAPI.update_status_with_media(filename=filePath, status='story baru dari ayang @A_ZeeJKT48\nID:' + str(story.taken_at))
        if hasattr(Twit, 'processing_info') and Twit.processing_info['state'] == 'pending':
            print('Pending...')
            time.sleep(15)
        print('TWEETING!')
    except tweepy.TwitterServerError as err:
            print('ERROR:', err)
            print('SUCCESS!')

def ReadLastTweet():
    if not os.path.exists(absPath('temp.txt')):
        return 0
    with open(absPath('temp.txt')) as file:
        read = file.read()
        timestamp = int(read)
    return timestamp

def deleteTweet():
    print('CHECKING OLD TWEETS...')
    TwitApi = getTwitAPI()
    timeline = TwitApi.user_timeline(count=200)
    for tweet in timeline:
        if time.time() - tweet.created_at.timestamp() > 60 * 60 * 24 * 5:
            print('DELETING TWEET {}'.format(tweet.id_str))
            TwitApi.destroy_status(tweet.id_str)
    return

def SaveLastTweet(story):
    with open('temp.txt','w') as file:
        write = str(story.taken_at)
        file.write(write)

while True:
    if __name__ == '__main__':
        userInfo = fetchStory()
        stories  = parseStory(userInfo)
        lastStory = ReadLastTweet()
        for story in stories:
            if lastStory >= story.taken_at:
                print()
                print('TWEET FOR STORY {} ALREADY SENT'.format(story.taken_at))
                time.sleep(300)
                continue
            fileName = getStory(story)
            twitMedia(fileName)
            SaveLastTweet(story)
            break
                