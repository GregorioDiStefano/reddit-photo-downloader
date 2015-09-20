from imgurpython import ImgurClient
import praw
import RedditImger
import unittest


class MyTests(unittest.TestCase):

    imgur_settings = {
        "imgur_client_id": "99d1b0a07a1f84b",
        "imgur_client_secret": "4c5a1c42c3681557addb6b92c05649fbbbd97a51",
    }

    reddit_settings = {
        "user_agent": "Chrome",
        "limit_per_subreddit" : 100,
    }

    subreddit = ["ImagesOfEarth", "SeaPorn"]

    def setUp(self):
        pass

    def test_create_imgur_client(self):
        ri0 = RedditImger.RedditImger(self.imgur_settings,
                                     self.reddit_settings,
                                     self.subreddit)

        self.assertIsInstance(ri0.imgur_client, ImgurClient)

    def test_create_reddit_client(self):
        ri1 = RedditImger.RedditImger(self.imgur_settings,
                                     self.reddit_settings,
                                     self.subreddit)

        self.assertIsInstance(ri1.reddit_client, praw.Reddit)

    def test_image_ext(self):
        sri = RedditImger.SRImages(None, "test")
        self.assertTrue(sri.image_ext("http://google.ca/file.jpg"))
        self.assertFalse(sri.image_ext("http://google.ca/file.jpg1"))
        self.assertFalse(sri.image_ext("a.jpg/a"))
        self.assertTrue(sri.image_ext("http://reddit.com/file.png"))
        self.assertFalse(sri.image_ext("http://google.ca/"))

if __name__ == '__main__':
    unittest.main()
