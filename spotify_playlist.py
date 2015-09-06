import praw
import pprint
import sys
import spotipy
import spotipy.util as util
import requests
from bs4 import BeautifulSoup

def add_to_playlist(track_uri):
    if len(sys.argv) > 2:
        username = sys.argv[1]
        playlist_id = sys.argv[2]
    else:
    	print("Usage: %s username playlist_id track_id ..." % (sys.argv[0],))
    	sys.exit()
    track_ids = track_uri

    scope = 'playlist-modify-public'

    clientID = 'ac8c779500c5447b90e4eb7e804a9ddc'
    clientSecret = '2ea9588d7ac34e59abededa78bc191b0'
    redirect = 'http://localhost:8888/callback'

    token = util.prompt_for_user_token(username, scope, clientID, clientSecret, redirect)

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
        print(results)
    else:
        print("Can't get token for", username)

    
    

def add_by_artist():
	spotify = spotipy.Spotify()
	name = sys.argv[4]
	results = spotify.search(q='artist:' + name, type='artist')
	item = results['artists']['items']
	artist_uri = item[0]['uri']
	
	top_tracks = spotify.artist_top_tracks(artist_uri)
	track_array = []
	for track in top_tracks['tracks'][:10]:
		#print(track['preview_url'])
		new_uri = track['uri'].replace('spotify:track:', '')
		track_array.append(new_uri)
	add_to_playlist(track_array)


def add_by_reddit():
    r = praw.Reddit(user_agent='news_reader')
    spotify = spotipy.Spotify()
    submissions = r.get_subreddit('music').get_hot(limit=30)
    submission_form = "{}) {} : {} <{}>"
    count = 1
    print("Top 30 Posts from /r/music")
    print('-' * 25)
    track_array = []
    for sub in submissions:
        #print(submission_form.format(count, sub.ups, sub.title, sub.url))
        sub_form = submission_form.format(count, sub.ups, sub.title, sub.url)
        if(sub.url.find("youtube")!=-1):
        	split_on_dash = sub.title.split('-')
        	if(len(split_on_dash)==1):
        		continue
        	split_on_bracket = split_on_dash[1].split('[')
        	final_title = split_on_bracket[0].split('(')
        	print(final_title[0])
        	if(len(final_title[0])==0):
        		continue
        	results = spotify.search(q=final_title[0], type='track')
        	r = results['tracks']['items']
        	if(len(r)<1):
        		continue
        	print(r[0]['uri'])
        	track_array.append(r[0]['uri'])
        count += 1
    add_to_playlist(track_array)

def add_by_billboard():
    spotify = spotipy.Spotify()
    url = 'http://www.billboard.com/charts/hot-100'
    source = requests.get(url)
    plain_text = source.content
    soup = BeautifulSoup(plain_text, 'html.parser')
    data = soup.find_all("div", {"class": "row-title"})
    track_array = []	
    for datum in data:
        song_name = datum.contents[1].text
        results = spotify.search(q=song_name, type='track')
        r = results['tracks']['items']
        if(len(r)<1):
            continue
        track_array.append(r[0]['uri'])
    add_to_playlist(track_array)

if(sys.argv[3].lower()=='reddit'):
    add_by_reddit()
elif(sys.argv[3].lower()=='billboard'):
    add_by_billboard()
elif(sys.argv[3].lower()=='artist'):
    add_by_artist()
else:
    print('Error')
