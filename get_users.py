# coding:utf-8
import re
import time
from typing import List, Dict
import crawlertool as tool
from selenium import webdriver
from selenium.webdriver.common.by import By


class SpiderTwitterAccountInfo(tool.abc.SingleSpider):
  """
    Twitter账号信息爬虫
    """

  def __init__(self, driver):
    self.driver = driver
    # 爬虫实例的变量

  @staticmethod
  def get_twitter_user_name(page_url: str) -> str:
    """提取Twitter的账号用户名称
        主要用于从Twitter任意账号页的Url中提取账号用户名称
        :param page_url: Twitter任意账号页的Url
        :return: Twitter账号用户名称
        """
    if pattern := re.search(r"(?<=twitter.com/)[^/]+", page_url):
      return pattern.group()

  def running(self, user_name: str) -> List[Dict]:
    """执行Twitter账号信息爬虫
        :param user_name: Twitter的账号用户名称（可以通过get_twitter_user_name获取）
        :return: Json格式的Twitter账号数据
        """
    self.user_name = user_name
    actual_url = "https://twitter.com/" + user_name

    self.console("开始抓取,实际请求的Url:" + actual_url)

    self.driver.get(actual_url)
    time.sleep(3)
    item = {}

    userID = self.driver.find_element(By.XPATH, "(//div[@data-testid='UserName']//div[@tabindex='-1']//span)").text
    item["userID"] = userID.replace('@', '')

    item["userName"] = self.driver.find_element(By.XPATH, "(//div[@data-testid='UserName']//span)[1]").text

    item["userDescription"] = self.driver.find_element(By.XPATH, "//div[@data-testid='UserDescription']").text

    item["userLocation"] = self.driver.find_element(By.XPATH, "//span[@data-testid='UserLocation']").text

    userUrl = self.driver.find_element(By.XPATH, "//a[@data-testid='UserUrl']")
    item["userUrl"] = userUrl.get_attribute("href")

    item["following"] = self.driver.find_element(By.XPATH, "(//a[@dir='ltr' and @role='link']/span/span)[1]").text
    item["followers"] = self.driver.find_element(By.XPATH, "(//a[@dir='ltr' and @role='link']/span/span)[3]").text

    return [item]


if __name__ == "__main__":
  # 初始化webdriver
  driverOptions = webdriver.ChromeOptions()

  # 导入缓存数据
  driverOptions.add_argument(r"user-data-dir=C:\Users\Ana997\AppData\Local\Google\Chrome\User Data")

  # 对应的chromedriver路径
  driver = webdriver.Chrome(options=driverOptions)

  print(SpiderTwitterAccountInfo(driver).running(
    SpiderTwitterAccountInfo.get_twitter_user_name("https://twitter.com/Doug_Bandow")))
  driver.quit()
