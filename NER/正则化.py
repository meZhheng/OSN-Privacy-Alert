# encoding: utf-8
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
    """
    mobiles = re.findall(r"1[2759]{2,2}\d{8}", text)
    return mobiles


if __name__ == '__main__':
    content = "Please 17965785598 42.121.252.58:443 contact 127.0.0.1  086-1598845173 us 068-1720071239 https://blog.csdn.net/u013421629/ at https://www.yiibai.com/ contact@qq.com for further information 1973536419@qq.com You can  also give feedbacl at FEedback@yiibai.com feng_hao_yang@sjtu.edu.cn"
    emails = get_findAll_emails(text=content)
    print(emails)
    moblies = get_findAll_mobiles(text=content)
    print(moblies)
