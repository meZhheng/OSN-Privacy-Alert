# coding:utf-8
import datetime as dt
import re
import time
from urllib import parse
from tenacity import *
import crawlertool as tool
from selenium import webdriver
from selenium.webdriver.common.by import By


class SpiderTwitterAccountPost(tool.abc.SingleSpider):

  def __init__(self, driver):
    self.driver = driver

  def get_twitter_user_name(self, page_url: str):
    """
    从URL提取用户名称
    :param page_url: Twitter任意账号页的Url
    :return: Twitter账号用户名称
    """
    if pattern := re.search(r"(?<=twitter.com/)[^/]+", page_url):
      self.user_name = pattern.group()

  @retry(stop=stop_after_attempt(5), wait=wait_random(min=3, max=5))
  def get_url(self, actual_url):
    self.driver.get(actual_url)
    time.sleep(5)
    # 判断是否该账号在指定时间范围内没有发文
    if self.driver.find_elements(By.XPATH, "//div[@data-testid='empty_state_header_text']"):
      raise TryAgain

  def running(self, since_date=None, until_date=None):
    """执行 Twitter 账号推文爬虫
    :param since_date: 抓取时间范围的右侧边界（最早日期）
    :param until_date: 抓取时间范围的左侧边界（最晚日期）
    :return: 推文信息-list
    """
    item_list = []

    query_sentence = ["from:%s" % self.user_name, "-filter:retweets"]
    if since_date is not None:
      query_sentence.append("since:%s" % str(since_date))  # 设置开始时间
    if until_date is not None:
      query_sentence.append("until:%s" % str(until_date))  # 设置结束时间
    query = " ".join(query_sentence)  # 计算q(query)参数的值
    params = {
      "q": query,
      "f": "live"
    }
    actual_url = "https://twitter.com/search?" + parse.urlencode(params)
    self.console("实际请求Url:" + actual_url)

    try:
      self.get_url(actual_url)
    except Exception as err:
      print(err)
      return '没有找到结果'

    # 循环遍历外层标签
    tweet_id_set = set()
    while True:
      last_label_tweet = None
      for tweet in self.driver.find_elements(By.XPATH, "//article"):
        item = []
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
        text = tweet.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text

        # 解析图片链接
        for img in tweet.find_elements(By.XPATH, ".//img[@draggable='true' and string-length(@alt) > 0]")[1:]:
          print(img.get_attribute("src"))

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
        if len(views_t := label.find_elements(By.XPATH, ".//span[@data-testid='app-text-transition-container']")) == 4:
          views = views_t[3].text
        item.extend([tweet_id, datetime, replies, retweets, likes, views, text])
        item_list.append(item)

      # 向下滚动到最下面的一条推文
      if last_label_tweet is not None:
        self.driver.execute_script("arguments[0].scrollIntoView();", last_label_tweet)  # 滑动到推文标签
        time.sleep(3)
      else:
        break

    return len(item_list)


if __name__ == "__main__":
  # 初始化webdriver
  driverOptions = webdriver.ChromeOptions()

  # 导入浏览器缓存，实现登录状态
  driverOptions.add_argument(r"user-data-dir=C:\Users\Ana997\AppData\Local\Google\Chrome\User Data")
  # driverOptions.add_argument("blink-settings=imagesEnabled=false") 不加载图片，加快爬取速度

  # webdriver路径
  driver = webdriver.Chrome(options=driverOptions)

  spider = SpiderTwitterAccountPost(driver)
  spider.get_twitter_user_name("https://twitter.com/nasa")

  print(spider.running(
    since_date=dt.date(2021, 3, 19),
    until_date=dt.date(2021, 3, 20)
  ))
  driver.quit()
