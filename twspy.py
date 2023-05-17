import threading
import configparser
import time
from queue import Queue
from spider import Spider
from insert import Mysql
from selenium import webdriver

config = configparser.ConfigParser()
config.read('config.ini')


def create_driver(data):
  driverOptions = webdriver.ChromeOptions()
  driverOptions.add_argument(f"user-data-dir={data}")
  driverOptions.add_argument('--no-sandbox')
  driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"

  return webdriver.Chrome(executable_path=driver_path, options=driverOptions)


def processing():
  url_queue = Queue(maxsize=20)
  user_queue = Queue(maxsize=20)
  data_queue = Queue(maxsize=200)

  driver = create_driver(config['chromeData']['path'])
  driver.implicitly_wait(10)
  driver.get("https://twitter.com/")
  cookies = driver.get_cookies()
  driver.close()

  database = Mysql(url_queue, user_queue, data_queue, config)
  spider = Spider(url_queue, user_queue, data_queue, config, cookies)

  stop_event = threading.Event()
  user_crawl = threading.Thread(target=spider.getUser, args=(stop_event,))
  tweet_crawl = threading.Thread(target=spider.getTweets, args=(stop_event,))
  user_insert = threading.Thread(target=database.tweet_insert, args=(stop_event, 'users'))
  tweet_insert = threading.Thread(target=database.tweet_insert, args=(stop_event, 'tweets'))
  thread_pool = [user_crawl, tweet_crawl, user_insert, tweet_insert]

  for thread in thread_pool:
    thread.start()

  user = config['userList']['user']
  spider.running(user)

  stop_event.set()

  for thread in thread_pool:
    thread.join()


if __name__ == '__main__':
  processing()
