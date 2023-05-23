import mysql.connector


class Mysql:
    def __init__(self):
        # 连接到 MySQL 数据库
        self.mydb = mysql.connector.connect(
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
        val = [["9999999999999999989", "2023.05.12", "插入测试", "图片url", 10, 9, 8, 7]]
        # 执行 SQL 插入语句
        self.my_cursor.executemany(sql, val)
        # 提交到数据库执行
        self.mydb.commit()
        # 输出插入的行数
        print(self.my_cursor.rowcount, "record inserted.")


if __name__ == "__main__":
    database = Mysql()
    item = {}
    database.tweet_insert(item)
