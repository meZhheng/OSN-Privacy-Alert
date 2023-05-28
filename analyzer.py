from Mysql import Mysql
from edit import getData

database = Mysql()
id = 6410832904
tweets = database.get_valid_tweets(id)
textlist = []
for tweet in tweets[15:20]:
    textlist.append(tweet[4])
print(textlist)
results = getData(textlist)
answers = []
for result in results:
    result = result.split(":")[1]
    for char in ['[', ']']:
        result = result.replace(char, "")
    answers.append(result)

