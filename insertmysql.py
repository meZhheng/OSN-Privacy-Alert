import pymysql
import configparser
from NER.regular import get_findAll_emails, get_findAll_mobiles

config = configparser.ConfigParser()
config.read('config.ini')


class Mysql:
    def __init__(self):
        # 连接到 MySQL 数据库
        self.mydb = pymysql.connect(
            host=config['database']['DB_HOST'],  # 数据库主机地址
            user=config['database']['DB_USER'],  # 用户名
            password=config['database']['DB_PASSWORD'],  # 密码
            database=config['database']['DB_DATABASE'])  # 数据库名称
        # 创建游标对象
        self.my_cursor = self.mydb.cursor()
        if self.mydb:
            print("Connection Successful")
        else:
            print("Connection Unsuccessful")

    def tweet_insert(self, item):
        # SQL 插入语句
        sql = "INSERT INTO tweets (tweet_id, time, text, image, replies, retweets, likes, views) " \
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        # 执行 SQL 插入语句
        self.my_cursor.executemany(sql, item)
        # 提交到数据库执行
        self.mydb.commit()
        # 输出插入的行数
        print(self.my_cursor.rowcount, "record inserted.")

    def blog_insert(self, item):
        """
        插入博客数据到数据库中

        :param item: 博客数据，包括bid, 正文, 日期, 位置, 工具, 话题, 评论数, 点赞数, 转发数, @用户
        :return: None
        """
        # SQL 插入语句
        sql = "INSERT IGNORE INTO blogs VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            # 执行 SQL 插入语句
            self.my_cursor.executemany(sql, item)
            # 提交到数据库执行
            self.mydb.commit()
        except Exception as e:
            print(e)
            self.mydb.rollback()
        # 输出插入的行数
        print(self.my_cursor.rowcount, "record inserted.")

    def privacy_insert(self, item):
        """
        插入用户隐私数据到数据库中

        :param item: 用户隐私数据，包括用户id、隐私分类、隐私值
        :return: None
        """
        sql = "INSERT IGNORE INTO privacy(userid, privacy_class, privacy_value) VALUES (%s, %s, %s) "
        try:
            # 执行 SQL 插入语句
            self.my_cursor.executemany(sql, item)
            # 提交到数据库执行
            self.mydb.commit()
        except Exception as e:
            print(e)
            self.mydb.rollback()
        # 输出插入的行数
        print(self.my_cursor.rowcount, "record inserted.")

    def privacy2weibo_insert(self, item):
        """
        在隐私博文关系表中插入用户隐私数据id与博文id的联系

        :param item: 用户隐私数据，包括用户id、隐私值
        :return: None
        """
        sql = "INSERT IGNORE INTO privacy2weibo VALUES (%s, %s)"
        try:
            # 执行 SQL 插入语句
            self.my_cursor.executemany(sql, item)
            # 提交到数据库执行
            self.mydb.commit()
        except Exception as e:
            print(e)
            self.mydb.rollback()
        # 输出插入的行数
        print(self.my_cursor.rowcount, "record inserted.")

    def regular_extract(self, tweetid, userid, text):
        """
        从推文中提取邮箱和电话号码，并将它们插入到隐私表和隐私-微博关系表

        :param tweetid: 推文id
        :param userid: 用户id
        :param text: 推文内容
        :return: None
        """
        # 从文本中获取所有的电子邮件和电话号码
        emails = get_findAll_emails(text)
        mobiles = get_findAll_mobiles(text)

        # 如果找到了电子邮件，则将其插入到名为“privacy”的表中，然后将其与tweetid相关联
        if emails:
            item = []
            for email in emails:
                print(email)
                row = [userid, '邮箱', email]
                item.append(row)
            self.privacy_insert(item)
            for email in emails:
                result = self.get_privacy_id(userid, '邮箱', email)
                privacy_id = result[0][0]
                row = [tweetid, privacy_id]
                self.privacy2weibo_insert([row])

        # 如果找到了电话号码，则将其插入到名为“privacy”的表中，然后将其与tweetid相关联
        if mobiles:
            item = []
            for mobile in mobiles:
                row = [userid, '电话', mobile]
                item.append(row)
            self.privacy_insert(item)
            for mobile in mobiles:
                result = self.get_privacy_id(userid, '电话', mobile)
                privacy_id = result[0][0]
                row = [tweetid, privacy_id]
                self.privacy2weibo_insert([row])

    def get_privacy_id(self, userid, privacy_class, privacy_value):
        """
        获取用户的隐私id

        :param userid: 用户id
        :param privacy_class: 隐私分类
        :param privacy_value: 隐私值
        :return: 隐私id
        """
        sql = "SELECT * FROM privacy " \
              "WHERE userid = %s AND privacy_class = %s AND privacy_value = %s"
        val = [userid, privacy_class, privacy_value]
        self.my_cursor.execute(sql, val)
        result = self.my_cursor.fetchall()
        return result

    def get_tweets(self, userid):
        """
        从名为weibo的表中获取user_id为给定userid的所有行。

        :param userid: 用户ID
        :return: tweets，它是一个包含所有行的列表。
        """
        sql = "SELECT * FROM weibo WHERE user_id = %s"
        val = [userid]
        self.my_cursor.execute(sql, val)
        tweets = self.my_cursor.fetchall()
        return tweets

    def close(self):
        """
        关闭数据库连接。
        """
        try:
            self.mydb.close()
            print("连接已释放")
        except Exception as error:
            print(error)
            print("连接释放失败")


if __name__ == "__main__":
    database = Mysql()
    item = {}
    database.blog_insert(item)
