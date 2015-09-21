from imgurpython import ImgurClient
import praw
import re
from Queue import Queue
from threading import Thread, Lock
import os
import hashlib
import urllib3
import cPickle

"""
    Prevent useless HTTP req. and API uses if a certain item has been seen
    before.
"""
class Cacher(object):
    data = []
    realm = ""
    fn = ""

    def __init__(self, realm):
        try:
            self.realm = realm
            self.fn = self.realm + ".p"
            f = open(self.fn)
        except Exception, e:
            self.data = []
        else:
            self.data = cPickle.load(open(self.fn, "rb"))

    def set(self, url=""):
        self.data.append(url)

    def exists(self, url=""):
        return url in self.data

    def check_and_set(self, url=""):
        if not self.exists(url):
            self.set(url)
            return False
        return True

    def save_cache(self):
        print self.data
        cPickle.dump(self.data, file(self.realm + ".p", "wb"))

class ThreadedDownloader(object):
    num_fetch_threads = 10
    queue = Queue()
    mutex = Lock()
    sr_dirs_created = []
    download_dir = ""

    def __init__(self, dl_dir="images"):
        self.download_dir = dl_dir
        if not os.path.exists(dl_dir):
            os.mkdir(dl_dir)

    def setup_dir(self, sr):
        if sr not in self.sr_dirs_created:
            download_dir_sr = self.download_dir + "/" + sr
            if not os.path.exists(download_dir_sr):
                os.mkdir(download_dir_sr)
                self.sr_dirs_created.append(sr)

    def set_queue(self, queue):
        self.queue = queue

    def start(self):
        # Set up some threads to fetch the enclosures
        for i in range(self.num_fetch_threads):
            worker = Thread(target=self.work, args=())
            worker.setDaemon(True)
            worker.start()
        self.queue.join()
        print "Done!"

    def work(self):
        print "Starting thread!", self.queue.qsize()

        while self.queue.qsize():

            print "Size: ", self.queue.qsize()

            self.mutex.acquire()
            dl = self.queue.get()
            self.mutex.release()

            url = dl.values()[0]
            sr = dl.values()[1]

            self.setup_dir(sr)

            http = urllib3.PoolManager()
            img_data = http.request("GET", url).data
            image_hash = hashlib.md5(img_data).hexdigest()

            filename = self.download_dir + "/" + sr + "/" + image_hash

            img_file = open(filename, 'wb')
            img_file.write(img_data)
            img_file.close()

            self.queue.task_done()

class SRImages(object):
    limit = 0
    subreddit = None
    image_urls = []
    reddit_client = None
    downloader = None
    enclosure_queue = Queue()

    def __init__(self, rc, subreddit="", limit=100):
        self.subreddit = subreddit
        self.limit = limit
        self.reddit_client = rc
        self.image_urls = []

    def image_ext(self, url):
        return re.match("([^\s]+(\.(?i)(jpg|png))$)", url)

    def get_image_urls(self):
        submissions = self.reddit_client.get_subreddit(self.subreddit).get_hot(limit=self.limit)
        for s in submissions:
            if self.image_ext(s.url) and s.url not in self.image_urls:
                self.image_urls.append(s.url)

    def __str__(self):
        return "<%s, images: %d>" % (self.subreddit, len(self.image_urls))

class RedditImger(object):
    reddit_client = None

    cacher = Cacher("reddit_url")
    SRImgsObjs = []

    reddit_settings = {}
    downloader = None
    enclosure_queue = Queue()

    def __init__(self, imgur_settings={}, reddit_settings={}, subreddits=[]):

        try:
            self.reddit_settings = reddit_settings
            self.reddit_client = praw.Reddit(user_agent=reddit_settings["user_agent"])
            self.downloader = ThreadedDownloader(reddit_settings["download_dir"])
            self.subreddits = subreddits
        except KeyError:
            raise KeyError("Did you set the reddit_settings correctly?")

    def start(self):
        # Process every subreddit, get the images, and add the object to a list
        for subreddit in self.subreddits:
            sri = SRImages(self.reddit_client, subreddit, limit = self.reddit_settings["limit_per_subreddit"])
            sri.get_image_urls()
            self.SRImgsObjs.append(sri)

        # Add the images to a mapping
        for sri in self.SRImgsObjs:
            sr = sri.subreddit

            for img_url in sri.image_urls:
                if not self.cacher.check_and_set(img_url):
                    pair = {"subreddit": sr, "url": img_url}
                    self.enclosure_queue.put(pair)

        self.downloader.set_queue(self.enclosure_queue)
        self.downloader.start()
        self.cacher.save_cache()


