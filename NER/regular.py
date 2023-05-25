import re

# 自定义获取文本电子邮件的函数
def get_findAll_emails(text):
    """
    :param text: 文本
    :return: 返回电子邮件列表
    """
    emails = re.findall(r"[A-Za-z0-9\.\-+_]+@[A-Za-z0-9\.\-+_]+\.[a-z]+", text)
    return emails

# 自定义获取文本手机号函数
def get_findAll_mobiles(text):
    """
    :param text: 文本
    :return: 返回手机号列表
    中国手机号: 1(3-9选一个)+9位随机
    美国手机号: 匹配格式包括
    1 555-555-5555
    555-555-5555
    (555) 555 5555
    即1是可有可无的,其他10位必须有,其中的前三位区号,带不带括号均可。中间的两个分隔符用空格代替,这里我们让第一个位置的空格/分隔符可有可无,第二个位置必须有
    (如果第二个位置也需要改成可有可无，在\d{4}前加?即可,不过一般是有分隔的
    """
    Chinese_mobiles = re.findall(r"1[3-9]\d{9}", text)
    American_mobiles = re.findall(r"(?:(?:1\s?)?(?:\(\d{3}\)|\d{3}))(?:\s|-)?\d{3}(?:\s|-)\d{4}", text)
    return list(set(Chinese_mobiles+American_mobiles))

if __name__ == '__main__':
    
    content = "Please 42.121.252.58:443 contact 127.0.0.1  086-18459851737 us 1 (555)555-5555 https://blog.csdn.net/u013421629/ at https://www.yiibai.com/ contact@qq.com for further information 1973536419@qq.com You can  also give feedbacl at FEedback@yiibai.com feng_hao_yang@sjtu.edu.cn"
    emails=get_findAll_emails(text=content)
    print(emails)
    moblies=get_findAll_mobiles(text=content)
    print(moblies)