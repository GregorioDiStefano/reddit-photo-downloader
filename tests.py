from imgurpython import ImgurClient
import praw
import RedditImger
import unittest
import random
import string
import os

class Utils(object):

    @staticmethod
    def random_fn():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))


class MyTests(unittest.TestCase):

    reddit_settings = {
        "user_agent": "Chrome",
        "limit_per_subreddit" : 50,
        "download_dir" : "pictures",
    }

    subreddit = ["ImagesOfEarth", "SeaPorn"]

    def setUp(self):
        pass

    def test_create_reddit_client(self):
        ri1 = RedditImger.RedditImger(self.reddit_settings,
                                     self.subreddit)

        self.assertIsInstance(ri1.reddit_client, praw.Reddit)

    def test_image_ext(self):
        sri = RedditImger.SRImages(None, "test")
        self.assertTrue(sri.image_ext("http://google.ca/file.jpg"))
        self.assertFalse(sri.image_ext("http://google.ca/file.jpg1"))
        self.assertFalse(sri.image_ext("a.jpg/a"))
        self.assertTrue(sri.image_ext("http://reddit.com/file.png"))
        self.assertFalse(sri.image_ext("http://google.ca/"))

    def test_cache_1(self):
        a = RedditImger.Cacher(Utils.random_fn())
        self.assertFalse(a.exists("a fake item"))
        a.set("a fake item")
        self.assertTrue(a.exists("a fake item"))

    def test_cache_2(self):
        random_fn = Utils.random_fn()
        a = RedditImger.Cacher(random_fn)
        self.assertFalse(a.exists("a fake item"))
        a.set("a fake item")
        self.assertTrue(a.exists("a fake item"))
        a.save_cache()

        b = RedditImger.Cacher(random_fn)
        self.assertTrue(b.exists("a fake item"))
        os.remove(random_fn + ".p")

    def test_cache_3(self):
        random_fn = Utils.random_fn()
        a = RedditImger.Cacher(random_fn)
        self.assertFalse(a.check_and_set("a"))
        self.assertTrue(a.check_and_set("a"))

    def test_reddit_client(self):
        ri1 = RedditImger.RedditImger(self.reddit_settings,
                                     self.subreddit)

        ri1.start()

if __name__ == '__main__':
    unittest.main()
