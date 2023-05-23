# coding:utf-8
import re
import time
import datetime as dt
from urllib import parse
from tenacity import *
import crawlertool as tool
import logging
from queue import Queue
from selenium.webdriver.common.by import By
from selenium import webdriver


class Spider(tool.abc.SingleSpider):

  def __init__(self, url_queue, user_queue, data_queue, config, cookies):
    self.url_queue = url_queue
    self.trans_queue = Queue(maxsize=50)
    self.user_queue = user_queue
    self.data_queue = data_queue
    self.config = config
    self.cookies = cookies

  @retry(stop=stop_after_attempt(5), wait=wait_random(min=3, max=5))
  def get_url(self, driver, actual_url):
    driver.get(actual_url)
    time.sleep(5)
    # 判断是否该账号在指定时间范围内没有发文
    if driver.find_elements(By.XPATH, "//div[@data-testid='empty_state_header_text']"):
      raise TryAgain

  def running(self, user):
    logger = logging.getLogger('getting user list')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('./logs/userList.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.get('https://twitter.com/')
    for cookie in self.cookies:
      driver.add_cookie(cookie)
    actual_url = "https://twitter.com/{}/followers".format(user)
    driver.get(actual_url)
    self.console("从以下url获取用户列表:" + actual_url)

    logger.info('Starting getting user list')
    user_id_set = set()
    while True:
      last_user = None
      for user in driver.find_elements(By.XPATH, "//div[@data-testid='cellInnerDiv']//a[@tabindex='-1']"):
        user_id = user.get_attribute("href")
        if user_id in user_id_set:
          continue
        user_id_set.add(user_id)
        self.url_queue.put(user_id)
        logger.info(f'getting user: {user_id}')
        last_user = user

      # 向下滚动到最下面的一个用户
      if last_user is not None:
        driver.execute_script("arguments[0].scrollIntoView();", last_user)  # 滑动到推文标签
        time.sleep(1)
      else:
        break
    logger.info('Finished')
    self.user_queue.join()
    driver.close()

  def getUser(self, stop_event):
    """执行Twitter账号信息爬虫
    """
    logger = logging.getLogger('getting user info')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('./logs/userInfo.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.get('https://twitter.com/')
    for cookie in self.cookies:
      driver.add_cookie(cookie)

    logger.info('Starting getting user info')
    while not (stop_event.is_set() and self.url_queue.empty()):
      actual_url = self.url_queue.get()

      driver.get(actual_url)

      if driver.find_elements(By.XPATH, "//div[@data-testid='emptyState']"):
        continue

      userID = actual_url.replace('https://twitter.com/', '')

      userName = driver.find_element(By.XPATH, "(//div[@data-testid='UserName']//span)[1]").text

      userDescription = 'unknown'
      if description := driver.find_elements(By.XPATH, "//div[@data-testid='UserDescription']"):
        userDescription = description[0].text

      userLocation = 'unknown'
      if location := driver.find_elements(By.XPATH, "//span[@data-testid='UserLocation']"):
        userLocation = location[0].text

      userUrl = 'unknown'
      if url := driver.find_elements(By.XPATH, "//a[@data-testid='UserUrl']"):
        userUrl = url[0].get_attribute("href")

      following = driver.find_element(By.XPATH, "((//div[@dir='ltr' and @role='button'] | "
                                                "//a[@dir='ltr' and @role='link'])/span/span)[1]").text
      followers = driver.find_element(By.XPATH, "((//div[@dir='ltr' and @role='button'] | "
                                                "//a[@dir='ltr' and @role='link'])/span/span)[3]").text

      self.user_queue.put([userID, userName, userDescription, userLocation, userUrl, following, followers])
      self.trans_queue.put(userID)
      self.url_queue.task_done()
      logger.info(f'getting user: {userID}')

    logger.info('Finished')
    self.user_queue.join()
    self.trans_queue.join()
    driver.close()

  def getTweets(self, stop_event, since_date=dt.date(2019, 1, 1)):
    """执行 Twitter 账号推文爬虫
    :param stop_event: 结束事件
    :param since_date: 抓取时间范围的右侧边界（最早日期）
    """
    logger = logging.getLogger('getting tweets')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('./logs/tweets.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.get("https://twitter.com/")
    for cookie in self.cookies:
      driver.add_cookie(cookie)

    logger.info('Starting getting tweets')
    while not (stop_event.is_set() and self.trans_queue.empty()):
      user_name = self.trans_queue.get()
      query_sentence = ["from:%s" % user_name, "-filter:retweets"]
      if since_date is not None:
        query_sentence.append("since:%s" % str(since_date))  # 设置开始时间
      query = " ".join(query_sentence)  # 计算q(query)参数的值
      params = {
        "q": query,
        "f": "live"
      }
      actual_url = "https://twitter.com/search?" + parse.urlencode(params)
      self.console("实际请求Url:" + actual_url)

      try:
        self.get_url(driver, actual_url)
      except Exception as err:
        print(err)
        return '没有找到结果'

      # 循环遍历外层标签
      tweet_id_set = set()
      while True:
        last_label_tweet = None
        for tweet in driver.find_elements(By.XPATH, "//article"):
          tweet_id = tweet.find_element(By.XPATH, ".//div[@data-testid='User-Name']//a[@dir='ltr']")
          tweet_id = re.search("[0-9]+$", tweet_id.get_attribute("href")).group()
          # 判断推文是否已被抓取(若未被抓取则解析推文)
          if tweet_id in tweet_id_set:
            continue
          tweet_id_set.add(tweet_id)
          last_label_tweet = tweet

          # 解析推文发布时间
          datetime = tweet.find_element(By.XPATH, ".//time").get_attribute("datetime")
          datetime = datetime.replace("T", " ").replace(".000Z", "")

          # 解析推文内容
          text = 'unknown'
          if t := tweet.find_elements(By.XPATH, ".//div[@data-testid='tweetText']"):
            text = t[0].text
          # 解析图片链接
          imgs = []
          for img in tweet.find_elements(By.XPATH, ".//img[@draggable='true' and string-length(@alt) > 0]")[1:]:
            img = img.get_attribute("src")
            imgs.append(img)
          imgs = '|^|'.join(imgs)

          # 定位到推文反馈数据标签
          label = tweet.find_element(By.XPATH, ".//div[@role='group']")
          analytics = label.get_attribute("aria-label")
          # 解析推文反馈数据
          replies, retweets, likes, views = 0, 0, 0, 0
          for feedback_item in analytics.split(","):
            if "replies" in feedback_item:
              replies = int(re.search("[0-9]+", feedback_item).group())
            if "Retweets" in feedback_item:
              retweets = int(re.search("[0-9]+", feedback_item).group())
            if "likes" in feedback_item:
              likes = int(re.search("[0-9]+", feedback_item).group())
          if len(views_t :=
                 label.find_elements(By.XPATH, ".//span[@data-testid='app-text-transition-container']")) == 4:
            views = views_t[3].text

          self.data_queue.put([tweet_id, datetime, replies, retweets, likes, views, text, imgs, user_name])
          logger.info(f'getting tweets: {tweet_id}')

        # 向下滚动到最下面的一条推文
        if last_label_tweet is not None:
          driver.execute_script("arguments[0].scrollIntoView();", last_label_tweet)  # 滑动到推文标签
          time.sleep(1)
        else:
          break
      self.trans_queue.task_done()
    logger.info('finished')
    self.data_queue.join()
    driver.close()


if __name__ == "__main__":
  from queue import Queue

  # 初始化webdriver
  driverOptions = webdriver.ChromeOptions()

  # 导入浏览器缓存，实现登录状态
  driverOptions.add_argument(r"user-data-dir=C:\Users\Ana997\AppData\Local\Google\Chrome\User Data")
  # driverOptions.add_argument("blink-settings=imagesEnabled=false") 不加载图片，加快爬取速度

  # webdriver路径
  driver = webdriver.Chrome(options=driverOptions)
  user_queue = Queue()
  data_queue = Queue()
  spider = Spider(driver, user_queue, data_queue)
  spider.get_twitter_user_name("https://twitter.com/nasa")

  print(spider.running(
    since_date=dt.date(2021, 3, 18),
  ))
  driver.quit()
