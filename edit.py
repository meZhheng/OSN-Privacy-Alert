import openai


def getData(tweets):
  prompt = "请你帮我分析一下推文中暴露的以下四类信息：个人基本信息：真实姓名；位置信息：家庭地址、个人所在地；工作信息：从业公司、从事行业。以下是我发布的推文："

  tweet = '/n'.join(tweets)

  output = "输出格式:\n真实姓名：[]\n家庭地址：[]\n个人所在地：[]\n从业公司：[]\n从事行业：[]\n 请你在接下来的所有对话中都根据这个输出格式输出，并在[]符内填写你推断出的信息，没有就填无。 "

  instruction = prompt + '\n' + tweet + '\n' + output

  message = [
    {"role": "user", "content": instruction}]

  openai.api_key = "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"

  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=message
  ).choices[0].message['content']

  print(response)


if __name__ == "__main__":
  tweets = [
    '好久不见，华表奖！#中国电影华表奖# ',
    '#华表奖阵容官宣# 百舸争流，奋楫者先！阔别重逢，共襄盛举，我们与中国电影共振同频。5月23日#华表奖颁奖典礼#，相约共赴，不见不散！#中国电影华表奖# ',
    '#奔跑吧之舌尖上的贵州#来贵阳不仅要吃美食看美景，游戏得赢祝福也得送，瞄准，用力，发射，NiceZ视介满月，我来送上一份六六祝福 ',
    'big power king Kong leg� 郑恺的微博视频 ',
    '#奔跑吧我为青春唱首歌# 一日奔跑，终身兄弟！奔跑吧的微博视频 '
    '#奔跑吧一起运动吧#队友靠谱讲究的就是一个省心省力，#奔跑吧#录制进行中，大家觉得我这个参赛姿势能不能一举夺冠？能不能拿下今天的冠军勋章，还要靠你来助我一臂之力！快来为我们加油打call吧，我们不想分开！ ',
  ]

  getData(tweets)
