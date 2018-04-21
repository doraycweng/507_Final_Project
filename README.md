
Data source:
1. Scraping the hot100 songs from https://www.billboard.com/charts/hot-100 . 
2. Using Spotify API to get the artist, songs' popularity, songs' features(tempo, danceability, loudness, energy, acousticness and speechiness) and the artists' number of followers for the hot100 songs  


Requirement: 
1. Spotify API authorization 
Client_id and client_secret are required to run the program. They can be created by registering an application on https://beta.developer.spotify.com/dashboard/login . More information can be found here: https://beta.developer.spotify.com/documentation/general/guides/app-settings/#register-your-app . After the client_id and client_secret are created, insert them into the secret_data.py file. 

2. Plotly 
Create an plotly account and follow the steps on https://plot.ly/python/getting-started/ to install the package and set your credentials. 


Code Structure:

There are two classes in the program: Song and Artist. The song class contains two methods, "get_song_info_from_spotify" and "get_audio_feature_from_spotify", which are used to get the song's attributes from spotify. The artist class contains one method, "get_artist_info_from_spotify", which is used to get the artist's attributes from spotify. 

Other major functions include: "get_access_token", which is used to get access token from spotify, "get_hot100_songs_by_scraping", which is to scrape the hot100 songs from billboard website, and four plot functions: "plot_song_rank_vs_pop_top_10", "plot_artist_vs_song_top_10", "plot_artist_vs_followers_top_10" and "plot_features_histogram". 


Interaction:

After you run the program, it would prompt you "Please enter "list", number 1 to 4, "help", or "exit":".
There are 7 options to type in:
1. "list" : it would show you all the hot100 songs. 
2. "1" : it would show you a bar chart on plot.ly with top 10 songs from hot100 of billborad vs their popularity from spotify. 
3. "2" : it would show you a bar chart on plot.ly with top 10 artists vs number of songs in the hot100 of billboard.
4. "3" : it would show you a bar chart on plot.ly with top 10 artists vs their number of followers from spotify.
5. "4" : it would prompt you which audio feature you would like to see: 1 for Tempo, 2 for Danceability, 3 for Loudness, 4 for Energy, 5 for Acousticness, 6 for Speechiness. After you entering a number, it would show you a histogram of the chosen audio feature. 
6. "help" : it would show you the instruction.
7. "exit" : exit the program. 


Note: 

If you rerun the program to get new data from spotify, the final_test.py file might fail becuase the test case is written based on the cache data. 




