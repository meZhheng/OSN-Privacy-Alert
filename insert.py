import mysql.connector
from queue import Queue


class Mysql:
  def __init__(self, url_queue, user_queue, data_queue, config):
    # 连接到 MySQL 数据库
    self.url_queue = url_queue
    self.user_queue = user_queue
    self.data_queue = data_queue
    self.mydb = mysql.connector.connect(
      host=config['database']['DB_HOST'],  # 数据库主机地址
      user=config['database']['DB_USER'],  # 用户名
      password=config['database']['DB_PASSWORD'],  # 密码
      database=config['database']['DB_DATABASE'])  # 数据库名称
    # 创建游标对象
    self.my_cursor = self.mydb.cursor()
    print("Connection Successfully") if self.mydb else print("Connection Unsuccessfully")

  def tweet_insert(self, stop_event, table: str):

    if table == 'users':
      sql = "INSERT IGNORE INTO users VALUES (%s, %s, %s, %s, %s, %s, %s)"
      users = []
      while not (stop_event.is_set() and self.user_queue.empty()):
        user = self.user_queue.get()
        users.append(user)
        self.user_queue.task_done()
        if len(users) == 10:
          self.my_cursor.executemany(sql, users)
          self.mydb.commit()
          users = []
      if users:
        self.my_cursor.executemany(sql, users)
        self.mydb.commit()

    elif table == 'tweets':
      sql = "INSERT IGNORE INTO tweets VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
      tweets = []
      while not (stop_event.is_set() and self.data_queue.empty()):
        tweet = self.data_queue.get()
        tweets.append(tweet)
        self.data_queue.task_done()
        print(len(tweets))
        if len(tweets) == 100:
          print(tweets)
          self.my_cursor.executemany(sql, tweets)
          self.mydb.commit()
          tweets = []
      if tweets:
        self.my_cursor.executemany(sql, tweets)
        self.mydb.commit()


if __name__ == "__main__":
  user_queue = Queue()
  data_queue = Queue()
  database = Mysql(user_queue, data_queue)
  item = [["9299999999999999190", "2023.05.12", 10, 9, 8, 7, "这是一个多条插入测试2", "图片url"],
          ["9999599999999199291", "2023.05.12", 10, 9, 8, 7, "这是一个多条插入测试3", "图片url"]]
  database.tweet_insert('tweets')
