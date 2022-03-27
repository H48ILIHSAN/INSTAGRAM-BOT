import codecs
import os
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
    with open(absPath('../app/config/instaAPI.txt')) as instaData:
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

def getStory(story):
    _, storyExt = os.path.splitext(urlparse(story.media_url).path)
    storyName = absPath('../app/assets/story' + storyExt)
    urllib.request.urlretrieve(story.media_url, storyName)
    if story.audio_url is not None:
        _, audioExt = os.path.splitext(urlparse(story.audio_url).path)
        audioName = absPath('../app/assets/audio' + audioExt)
        urllib.request.urlretrieve(story.audio_url, audioName)
    else:
        audioName = storyName
    
def getTwitAPI():
    with open(absPath('../app/config/twitterAPI.txt')) as twitData:
        ckey, csecret, tkey, tsecret = twitData.read().split('\n')
    twitAuth = tweepy.OAuthHandler(ckey, csecret)
    twitAuth.set_access_token(tkey, tsecret)
    return tweepy.API(twitAuth)

def twitMedia(filePath):
    _, Ext = os.path.splitext(urlparse(story.media_url).path)
    filePath = absPath('../app/assets/story' + Ext)
    TwitAPI = getTwitAPI()
    print('UPLOADING {}...'.format(filePath))
    try:
        Twit = TwitAPI.update_status_with_media(filename=filePath, status='ayang jkt48.zee habis bikin story')
        if hasattr(Twit, 'processing_info') and Twit.processing_info['state'] == 'pending':
            print('Pending...')
            time.sleep(15)
        print('TWEETING!')
    except tweepy.TwitterServerError as err:
        print('ERROR:', err)
    print('SUCCESS!')

def ReadLastTweet():
    if not os.path.exists(absPath('../app/temp.txt')):
        return 0
    with open(absPath('../app/temp.txt')) as file:
        read = file.read()
        timestamp = int()
    return timestamp

def SaveLastTweet(story):
    with open('../app/temp.txt','w') as file:
        write = str(story.taken_at)
        file.write(write)

def deleteTweet():
    print('CHECKING OLD TWEETS...')
    TwitApi = getTwitAPI()
    timeline = TwitApi.user_timeline(count=200)
    for tweet in timeline:
        if time.time() - tweet.created_at.timestamp() > 60 * 60 * 24 * 5:
            print('DELETING TWEET {}'.format(tweet.id_str))
            TwitApi.destroy_status(tweet.id_str)
    return

while True:
    if __name__ == '__main__':
        userInfo = fetchStory()
        stories  = parseStory(userInfo)
        print('{:d} STORIES FOUND!'.format(len(stories)))
        lastStory = ReadLastTweet()
        for story in stories:
            if lastStory >= story.taken_at:
                print('TWEET FOR STORY {} ALREADY SENT'.format(story.taken_at))
                continue
            fileName = getStory(story)
            twitMedia(fileName)
            SaveLastTweet(story)
            break
    time.sleep(6000)