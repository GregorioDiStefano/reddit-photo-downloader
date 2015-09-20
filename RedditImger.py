from imgurpython import ImgurClient
import praw
import re
from Queue import Queue
from threading import Thread, Lock
import time
import pprint



"""
    Prevent useless HTTP req. and API uses if a certain item has been seen
    before.
"""
class Cacher(object):
    def __init__(self, realm):
        pass

    def set(self, url=""):
        pass

    def is_new(self, url=""):
        pass

class ThreadedDownloader(object):
    num_fetch_threads = 10
    queue = Queue()
    mutex = Lock()

    def set_queue(self, queue):
        self.queue = queue

    def start(self):
        # Set up some threads to fetch the enclosures
        for i in range(self.num_fetch_threads):
            worker = Thread(target=self.work, args=())
            worker.setDaemon(True)
            worker.start()
        self.queue.join()

    def work(self):
        print "Starting thread!", self.queue.qsize()
        while True:

            self.mutex.acquire()
            dl = self.queue.get()
            self.mutex.release()

            time.sleep(1)

            self.queue.task_done()

class SRImages(object):
    limit = 0
    subreddit = None
    image_urls = []
    reddit_client = None
    downloader = ThreadedDownloader()
    enclosure_queue = Queue()

    def __init__(self, rc, subreddit="", limit=100):
        self.subreddit = subreddit
        self.limit = limit
        self.reddit_client = rc

    def image_ext(self, url):
        return re.match("([^\s]+(\.(?i)(jpg|png))$)", url)

    def get_image_urls(self):
        submissions = self.reddit_client.get_subreddit(self.subreddit).get_hot(limit=100)
        for s in submissions:
            if self.image_ext(s.url) and s.url not in self.image_urls:
                self.image_urls.append(s.url)

    def __str__(self):
        return "<%s, images: %d>" % (self.subreddit, len(self.image_urls))

class RedditImger(object):
    imgur_client = None
    reddit_client = None

    cacher = Cacher("reddit_url")
    SRImgsObjs = []
    subreddit_images = {}

    downloader = ThreadedDownloader()
    enclosure_queue = Queue()

    def __init__(self, imgur_settings={}, reddit_settings = {}, subreddits=[]):

        try:
            self.imgur_client_id = imgur_settings["imgur_client_id"]
            self.imgur_client_secret = imgur_settings["imgur_client_secret"]
        except KeyError:
            raise KeyError("Did you set the imgur_settings correctly?")

        try:
            self.imgur_client = ImgurClient(self.imgur_client_id, self.imgur_client_secret)
            self.reddit_client = praw.Reddit(user_agent=reddit_settings["user_agent"])
        except KeyError:
            raise KeyError("Did you set the reddit_settings correctly?")

        # Process every subreddit, get the images, and add the object to a list
        for subreddit in subreddits:
            sri = SRImages(self.reddit_client, subreddit, limit = reddit_settings["limit_per_subreddit"])
            sri.get_image_urls()
            self.SRImgsObjs.append(sri)


        # Add the images to a mapping
        for sri in self.SRImgsObjs:
            sr = sri.subreddit

            self.subreddit_images[sr] = sri.image_urls
            for img_url in sri.image_urls:
                pair = {"subreddit": sr, "url" : img_url}
                self.enclosure_queue.put({"subreddit" : sr, "url" : img_url})

        self.downloader.set_queue(self.enclosure_queue)
        self.downloader.start()


