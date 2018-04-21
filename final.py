import requests
import json
import sqlite3
from bs4 import BeautifulSoup
from secret_data import*
import base64
import six
import six.moves.urllib.parse as urllibparse
import plotly.plotly as py
import plotly.graph_objs as go



class Song:

    def __init__(self, name, rank):
        self.name = name
        self.rank = rank

        info_diction = self.get_song_info_from_spotify(name)
        self.artist = info_diction['artist']
        self.artist_id = info_diction['artist_id']
        self.track_id = info_diction['track_id']
        self.url = info_diction['url']
        self.popularity = info_diction['popularity']

        feature_diction = self.get_audio_feature_from_spotify(self.track_id)
        self.tempo = feature_diction["tempo"]
        self.danceability = feature_diction["danceability"]
        self.loudness = feature_diction["loudness"]
        self.energy = feature_diction["energy"]
        self.acousticness = feature_diction["acousticness"]
        self.speechiness = feature_diction["speechiness"]


    def get_song_info_from_spotify(self, name):
        info_diction = {}
        baseurl = "https://api.spotify.com/v1/search?"
        params = {"q": name, "type":"track", "limit": 1}
        response_obj = make_request_using_cache_spotify_API_Search(baseurl, params)
        info_diction["artist"] = response_obj["tracks"]["items"][0]["artists"][0]["name"]
        info_diction["artist_id"] = response_obj["tracks"]["items"][0]["artists"][0]["id"]
        info_diction["track_id"] = response_obj["tracks"]["items"][0]["id"]
        info_diction["url"] = response_obj["tracks"]["items"][0]["external_urls"]["spotify"]
        info_diction["popularity"] = response_obj["tracks"]["items"][0]["popularity"]
        return info_diction 

    def get_audio_feature_from_spotify(self, track_id):
        feature_diction={}
        baseurl = "https://api.spotify.com/v1/audio-features/{}".format(track_id)
        response_obj = make_request_using_cache_spotify_API(baseurl)
        feature_diction["tempo"] = response_obj["tempo"]
        feature_diction["danceability"] = response_obj["danceability"]
        feature_diction["loudness"] = response_obj["loudness"]
        feature_diction["energy"] = response_obj["energy"]
        feature_diction["acousticness"] = response_obj["acousticness"]
        feature_diction["speechiness"] = response_obj["speechiness"]
        return feature_diction


class Artist:
    def __init__(self, name, artist_id):
        self.name = name
        self.artist_id = artist_id
        info_diction = self.get_artist_info_from_spotify(artist_id)
        self.popularity = info_diction["popularity"]
        self.followers = info_diction["followers"]

    def get_artist_info_from_spotify(self, artist_id):
        info_diction = {}
        baseurl = "https://api.spotify.com/v1/artists/{}".format(artist_id)
        response_obj = make_request_using_cache_spotify_API(baseurl)
        info_diction["popularity"] = response_obj["popularity"]
        info_diction["followers"] = response_obj["followers"]["total"]
        return info_diction


def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache_spotify_API_Search(baseurl, params):

    CACHE_FNAME_API = 'cache_API.json'

    try:
        cache_file_API = open(CACHE_FNAME_API, 'r')
        cache_contents_API = cache_file_API.read()
        CACHE_DICTION_API = json.loads(cache_contents_API)
        cache_file_API.close()

    except:
        CACHE_DICTION_API = {}        
        
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION_API:
        print("Getting cached data...")
        return CACHE_DICTION_API[unique_ident]
    else:
        print("Making a request for new data...")
        access_token = get_access_token()
        authorization_header = {"Authorization":"Bearer {}".format(access_token)}
        resp = requests.get(baseurl, headers=authorization_header, params=params)
        CACHE_DICTION_API[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION_API)
        fw = open(CACHE_FNAME_API,"w")
        fw.write(dumped_json_cache)
        fw.close() 
        return CACHE_DICTION_API[unique_ident]

def make_request_using_cache_spotify_API(baseurl):
    CACHE_FNAME_API = 'cache_API.json'

    try:
        cache_file_API = open(CACHE_FNAME_API, 'r')
        cache_contents_API = cache_file_API.read()
        CACHE_DICTION_API = json.loads(cache_contents_API)
        cache_file_API.close()

    except:
        CACHE_DICTION_API = {}        
        
    unique_ident = baseurl

    if unique_ident in CACHE_DICTION_API:
        print("Getting cached data...")
        return CACHE_DICTION_API[unique_ident]
    else:
        print("Making a request for new data...")
        access_token = get_access_token()
        authorization_header = {"Authorization":"Bearer {}".format(access_token)}
        resp = requests.get(baseurl, headers=authorization_header)
        CACHE_DICTION_API[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION_API)
        fw = open(CACHE_FNAME_API,"w")
        fw.write(dumped_json_cache)
        fw.close() 
        return CACHE_DICTION_API[unique_ident]


def get_access_token():
    token_url = "https://accounts.spotify.com/api/token"
    base64encoded = base64.b64encode(six.text_type(client_id + ':' + client_secret).encode('ascii'))
    headers = {'Authorization': 'Basic %s' % base64encoded.decode('ascii')}
    payload = { 'grant_type': 'client_credentials'}
    access_token = json.loads(requests.post(token_url, headers = headers, data = payload).text)["access_token"]
    return access_token


def get_hot100_songs_by_scraping():
    hot100_list=[]
    baseurl = 'https://www.billboard.com/charts/hot-100'
    page_text = make_request_using_cache_billboard(baseurl)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    container = page_soup.find_all(class_="chart-row__container")
    i = 1
    for content in container:
        song = content.find(class_="chart-row__song").text
        hot100_list.append(Song(song, i))
        i+=1 
    return hot100_list


def make_request_using_cache_billboard(url):

    CACHE_FNAME = 'cache.json'
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()

    except:
        CACHE_DICTION = {}
    
    unique_ident = url
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() 
        return CACHE_DICTION[unique_ident]



def init_db(db_name):  
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        print("success")

    except:
        print("Error:Connection fails")  

    statement = '''
                DROP TABLE IF EXISTS 'Songs';
                '''
    cur.execute(statement)

    statement = '''
                DROP TABLE IF EXISTS 'Artists';
                '''

    cur.execute(statement)

    statement = '''
                CREATE TABLE 'Artists' (
                'Id' INTEGER PRIMARY KEY,
                'Name' TEXT NOT NULL,
                'Popularity' INTEGER,
                'Followers' INTEGER
                );
                '''
    cur.execute(statement)

    statement = '''
                CREATE TABLE 'Songs' (
                'Id' INTEGER PRIMARY KEY,
                'Rank' INTEGER NOT NULL,
                'Name' TEXT NOT NULL,
                'Artist' TEXT NOT NULL,
                'ArtistId' INTEGER NOT NULL,
                'Popularity' INTEGER,
                'Tempo' REAL,
                'Danceability' REAL,
                'Loudness' REAL,
                'Energy' REAL,
                'Acousticness' REAL,
                'Speechiness' REAL,
                'URL' TEXT
                );
                '''
    cur.execute(statement)
    conn.commit()
    conn.close()


def insert_data(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        print("success")

    except:
        print("Error:Connection fails")  


    songs = get_hot100_songs_by_scraping()
    artists = []
    artists_name = []
    for song in songs:
        artist = Artist(song.artist, song.artist_id)
        if artist.name not in artists_name:
            artists_name.append(artist.name)
            artists.append(artist)

    for artist in artists:
        insertion = (artist.name, artist.popularity, artist.followers)
        statement = '''
                    INSERT INTO Artists (Name, Popularity, Followers)
                    VALUES (?,?,?)
                    '''
        cur.execute(statement, insertion)

    for song in songs:
        artistId = cur.execute('SELECT Id FROM Artists WHERE Name = ?', (song.artist,)).fetchone()[0]
        insertion = (song.rank, song.name, song.artist, artistId, song.popularity, song.tempo, song.danceability, song.loudness, song.energy, song.acousticness, song.speechiness, song.url)
        statement = '''
                    INSERT INTO Songs (Rank, Name, Artist, ArtistId, Popularity, Tempo, Danceability, Loudness, Energy, Acousticness, Speechiness, URL)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    '''
        cur.execute(statement, insertion)
    
    conn.commit()
    conn.close()


def plot_song_rank_vs_pop_top_10():
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        print("success")

    except:
        print("Error:Connection fails") 

    data = cur.execute("SELECT Name, Popularity FROM Songs ORDER BY Rank LIMIT 10").fetchall()
    name = []
    popularity = []
    for data in data:
        name.append(data[0])
        popularity.append(data[1])

    data = [go.Bar(
            x=name,
            y=popularity,
            text=popularity,
            textposition = 'auto',
            marker=dict(
                color='rgb(158,202,225)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            ),
            opacity=0.6
        )]

    layout = go.Layout(
        title= "Top 10 songs from billboard vs Song popularity from Spotify",
        xaxis=dict(
            title='Songs'
        ),
        yaxis=dict(
            title='Popularity'
        ),
        bargap=0.2,
        bargroupgap=0.1
        )
    
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='bar-direct-labels')

    conn.commit()
    conn.close()


def plot_artist_vs_song_top_10():
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        print("success")

    except:
        print("Error:Connection fails")

    data = cur.execute("SELECT Artist, COUNT(*) FROM Songs GROUP BY Artist ORDER BY COUNT(*) DESC LIMIT 10").fetchall()
    name = []
    number_of_songs = []
    for data in data:
        name.append(data[0])
        number_of_songs.append(data[1])

    data = [go.Bar(
            x=name,
            y=number_of_songs,
            text=number_of_songs,
            textposition = 'auto',
            marker=dict(
                color='rgb(158,202,225)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            ),
            opacity=0.6
        )]

    layout = go.Layout(
            title= "Top 10 artists vs Number of songs in Hot100",
            xaxis=dict(
            title='Artists'
            ),
            yaxis=dict(
            title='Number of songs'
            ),
            bargap=0.2,
            bargroupgap=0.1
            )
    
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='bar-direct-labels')

    conn.commit()
    conn.close()

def plot_artist_vs_followers_top_10():
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        print("success")

    except:
        print("Error:Connection fails")

    data = cur.execute("SELECT Name, Followers FROM Artists ORDER BY Followers DESC LIMIT 10").fetchall()
    name = []
    followers = []
    for data in data:
        name.append(data[0])
        followers.append(data[1])

    data = [go.Bar(
            x=name,
            y=followers,
            text=followers,
            textposition = 'auto',
            marker=dict(
                color='rgb(158,202,225)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            ),
            opacity=0.6
        )]

    layout = go.Layout(
            title= "Top 10 artists vs Number of followers from Spotify",
            xaxis=dict(
            title='Artists'
            ),
            yaxis=dict(
            title='Number of followers'
            ),
            bargap=0.2,
            bargroupgap=0.1
            )
    
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='bar-direct-labels')

    conn.commit()
    conn.close()


def plot_features_histogram(feature):
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        print("success")

    except:
        print("Error:Connection fails")

    statement = "SELECT " + feature + " FROM Songs"

    data = cur.execute(statement).fetchall()
    feature_list = []
    for data in data:
        feature_list.append(data[0])

    trace1 = go.Histogram(
            x=feature_list,
            opacity=0.75,
            name=feature
            )


    data = [trace1]

    layout = go.Layout(
    title= feature + " histogram",
    xaxis=dict(
        title='Value'
    ),
    yaxis=dict(
        title='Count'
    ),
    bargap=0.2,
    bargroupgap=0.1
    )

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='styled histogram')
    conn.commit()
    conn.close()


def list_songs():
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        print("success")

    except:
        print("Error:Connection fails")

    songs_list = cur.execute("SELECT Rank, Name FROM Songs ORDER BY Rank").fetchall()

    for song in songs_list:
        print(str(song[0]) + " " + song[1])


if __name__ == "__main__":
    db_name = "final.sqlite"    
    init_db(db_name)
    insert_data(db_name)

    while(True):
        answer = input('\nPlease enter "list", number 1 to 4, "help", or "exit":')
        help_text = '''
There are 7 options to type in:
1. "list" : it would show you all the hot100 songs. 
2. "1" : it would show you a bar chart on plot.ly with top 10 songs from hot100 of billborad vs their popularity from spotify. 
3. "2" : it would show you a bar chart on plot.ly with top 10 artists vs number of songs in the hot100 of billboard.
4. "3" : it would show you a bar chart on plot.ly with top 10 artists vs their number of followers from spotify.
5. "4" : it would prompt you which audio feature you would like to see: 1 for Tempo, 2 for Danceability, 3 for Loudness, 4 for Energy, 5 for Acousticness, 6 for Speechiness. After you entering a number, it would show you a histogram of the chosen audio feature. 
6. "help" : it would show you the instruction.
7. "exit" : exit the program. 
                    '''

        if answer == "list":
            list_songs()
        elif answer == "1":
            plot_song_rank_vs_pop_top_10()
        elif answer == "2":
            plot_artist_vs_song_top_10()
        elif answer == "3":
            plot_artist_vs_followers_top_10()
        elif answer == "4":
            option = input("\nPlease enter 1 for Tempo, 2 for Danceability, 3 for Loudness, 4 for Energy, 5 for Acousticness, 6 for Speechiness:\n")
            if option == "1":
                plot_features_histogram("Tempo")
            elif option == "2":
                plot_features_histogram("Danceability")
            elif option == "3":
                plot_features_histogram("Loudness")
            elif option == "4":
                plot_features_histogram("Energy")
            elif option == "5":
                plot_features_histogram("Acousticness")
            elif option == "6":
                plot_features_histogram("Speechiness")
            else:
                print("Input is invalid. Please input it again.")
        elif answer == "help": 
            print(help_text)
        elif answer == "exit":
            print("Bye!")
            break
        else:
            print("Input is invalid. Please input it again.")




















