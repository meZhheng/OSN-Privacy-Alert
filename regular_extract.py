from insertmysql import Mysql


def regular_extract(userid):
    database = Mysql()
    tweets = database.get_tweets(userid)
    for tweet in tweets:
        database.regular_extract(tweet[0], tweet[2], tweet[4])
    database.close()


if __name__ == "__main__":
    # 示例
    user_id = 1108613250
    regular_extract(user_id)
