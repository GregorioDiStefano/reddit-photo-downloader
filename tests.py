from imgurpython import ImgurClient
import praw
import RedditImger
import unittest
import random
import string
import os
import shutil
from Queue import Queue

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
        cacher = RedditImger.Cacher(Utils.random_fn())
        self.assertFalse(cacher.exists("a fake item"))
        cacher.set("a fake item")
        self.assertTrue(cacher.exists("a fake item"))

    def test_cache_2(self):
        random_fn = Utils.random_fn()
        cacher = RedditImger.Cacher(random_fn)
        self.assertFalse(cacher.exists("a fake item"))
        cacher.set("a fake item")
        self.assertTrue(cacher.exists("a fake item"))
        cacher.save_cache()

        cacher2 = RedditImger.Cacher(random_fn)
        self.assertTrue(cacher2.exists("a fake item"))
        os.remove(cacher.fn)

    def test_cache_3(self):
        random_fn = Utils.random_fn()
        cacher = RedditImger.Cacher(random_fn)
        self.assertFalse(cacher.check_and_set("a"))
        self.assertTrue(cacher.check_and_set("a"))

    def test_threaded_downloader(self):
        urls = [("test_1", "http://i.imgur.com/8YFMclo.jpg"),
                ("test_1", "http://i.imgur.com/E3iGZaQ.jpg"),
                ("test_2", "http://i.imgur.com/cBYCFwF.png"),
                ("test_3", "http://i.imgur.com/ZF6Fu1K.jpg")]

        expected_files = [ "pictures/test_1/623602eb1852451c496a4ce1d9ac2d62",
                           "pictures/test_1/188f63f667644fa173c3914dd048a104",
                           "pictures/test_2/9277225dc44320fd62e9b78644ef3314",
                           "pictures/test_3/276d5838aee4044213e73e089ec88810"]

        reddit_settings = {
            "user_agent": "Chrome",
            "limit_per_subreddit" : 1,
            "number_of_threads" : 2,
            "download_dir" : "test_pictures",
        }

        downloader = RedditImger.ThreadedDownloader(reddit_settings["download_dir"], reddit_settings["number_of_threads"])
        queue = Queue()

        for sr, url in urls:
            queue.put({"subreddit": sr, "url": url})

        downloader.set_queue(queue)
        downloader.start()

        for file in expected_files:
            try:
                open(file)
            except Exception:
                self.fail("Expected files not downloaded :(")

        try:
            shutil.rmtree(reddit_settings["download_dir"])
        except Exception, e:
            print "Error while trying to delete test downloads: ", e
            pass

    def test_main(self):
        ri1 = RedditImger.RedditImger(self.reddit_settings,
                                     self.subreddit)
        ri1.start()

if __name__ == '__main__':
    unittest.main()
