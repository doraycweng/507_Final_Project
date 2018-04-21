import unittest
from final import *

db_name = "final.sqlite"   

class TestSong(unittest.TestCase):
	
	def testConstructor(self):
		song = Song("God's Plan", 1)
		self.assertEqual(song.name, "God's Plan")
		self.assertEqual(song.rank, 1)
		self.assertEqual(song.artist, "Drake")
		self.assertEqual(song.popularity, 98)
		self.assertEqual(song.tempo, 77.17)


class TestArtist(unittest.TestCase):
	
	def testConstructor(self):
		artist = Artist("Drake" , "3TVXtAsR1Inumwj472S9r4")
		self.assertEqual(artist.popularity, 100)
		self.assertEqual(artist.followers, 19027612)


class TestScrape(unittest.TestCase):

	def testScrape(self):
		hot100_list = get_hot100_songs_by_scraping()
		self.assertEqual(len(hot100_list), 100)

class TestDatabase(unittest.TestCase):

	def test_song_table(self):
		conn = sqlite3.connect(db_name)
		cur = conn.cursor()
		song_list = cur.execute("SELECT Name FROM Songs").fetchall()
		self.assertEqual(len(song_list), 100)
		self.assertIn(("God's Plan",), song_list)

	def test_artist_table(self):
		conn = sqlite3.connect(db_name)
		cur = conn.cursor()
		artist_list = cur.execute("SELECT Name FROM Artists").fetchall()
		self.assertLessEqual(len(artist_list),100)
		self.assertIn(("Drake",), artist_list)

	def test_table_join(self):
		conn = sqlite3.connect(db_name)
		cur = conn.cursor()
		join_list = cur.execute("SELECT Followers FROM Songs JOIN Artists ON Songs.ArtistId = Artists.Id").fetchall()
		self.assertEqual(len(join_list),100)
		join_1 = cur.execute("SELECT Followers FROM Songs JOIN Artists ON Songs.ArtistId = Artists.Id WHERE Artists.Name='Drake'").fetchone()
		self.assertEqual(join_1, (19027612,))
		join_2 = cur.execute("SELECT Tempo FROM Songs JOIN Artists ON Songs.ArtistId = Artists.Id WHERE Songs.Name='Psycho'").fetchone()
		self.assertEqual(join_2, (140.057,))




unittest.main()