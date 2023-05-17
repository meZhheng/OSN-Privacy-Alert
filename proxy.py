import requests
import configparser
import base64
import json
import socket
import ssl

config = configparser.ConfigParser()
config.read('config.ini')


def download_subscription():
  proxies = {
    "http": None,
    "https": None,
  }
  response = requests.get(config['proxy']['SUBSCRIPTION'], proxies=proxies)

  if response.status_code == 200:
    decoded_text = base64.b64decode(response.text + '=' * (-len(response.text) % 4)).decode('utf8').split('vmess')
    decoded_text = list(filter(None, decoded_text))
    subscription = [base64.b64decode(text[3:-2] + '=' * (-len(text[3:-2]) % 4)).decode('utf8') for text in decoded_text]
    return subscription
  else:
    print('获取代理服务器失败')


def parse_subscription_content():
  try:
    # 解析订阅内容，提取代理服务器配置信息
    proxy_config = [json.loads(subscription) for subscription in download_subscription()]
    return proxy_config
  except Exception as e:
    # 处理解析失败的情况
    print('错误：{}'.format(e))
    print('解析代理服务器失败')
    return None


def configure_proxies(proxy_config):
  proxies = []
  for proxy in proxy_config:
    # 解析每个代理服务器的配置信息，并存储到代理列表中
    proxy_info = "https://{}:{}".format(proxy["add"], proxy["port"])
    proxy = {
      "http": proxy_info,
      "https": proxy_info
    }
    proxies.append(proxy)
  return proxies


def ping(address):
  try:
    response = requests.get('https://' + address, timeout=3)
    response.elapsed.total_seconds()
    return True
  except Exception as e:
    print('错误：{}'.format(e))
    return False


def get_valid_proxy(proxy_pool):
  while True:
    # 从代理池中取出一个代理IP
    proxy = proxy_pool.pop(0)

    # 检查代理IP的可用性
    try:
      response = requests.get("https://www.google.com", proxies=proxy, timeout=5)
      if response.status_code == 200:
        # 如果代理IP可用，则返回该代理IP
        print('代理服务器连接成功：{}'.format(proxy))
        return proxy
    except Exception as e:
      print('代理服务器 {} 错误：{}'.format(proxy, e))

    # 如果代理IP不可用，则将该代理IP从代理池中删除
    if proxy in proxy_pool:
      proxy_pool.remove(proxy)

    # 如果代理池中没有可用的代理IP，则等待一段时间
    # if len(proxy_pool) == 0:
    #   time.sleep(10)
    #   # 重新从代理提供商那里获取代理IP地址
    #   new_proxies = get_proxies_from_provider()
    #   proxy_pool.extend(new_proxies)


def connect_to_proxy(proxy_info):
  proxy_address = proxy_info['address']
  proxy_port = proxy_info['port']
  proxy_protocol = proxy_info['protocol']
  proxy_encryption = proxy_info['encryption']

  # 创建代理服务器的连接
  proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  proxy_socket.connect((proxy_address, proxy_port))

  print('socket connect successfully')
  # 发送连接请求到代理服务器
  request = f"CONNECT www.google.com:443 HTTP/1.1\r\nHost: www.google.com:443\r\n\r\n"
  proxy_socket.sendall(request.encode())

  # 接收代理服务器的响应
  response = proxy_socket.recv(4096)
  response = response.decode()
  print("Proxy Server Response:\n", response)

  # 如果响应状态码为 200，则连接成功
  if "200 Connection established" in response:
    # 创建与代理服务器的加密连接（如果需要）
    if proxy_encryption == "ssl":
      # 创建加密连接
      proxy_socket = ssl.wrap_socket(proxy_socket)

    # 发送实际请求到目标服务器
    proxy_socket.sendall(b"GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n")

    # 接收目标服务器的响应
    response = proxy_socket.recv(4096)
    response = response.decode()
    print("Server Response:\n", response)

    # 关闭连接
    proxy_socket.close()
  else:
    print("Failed to connect to proxy server.")


if __name__ == '__main__':
  # proxy_config = parse_subscription_content()
  # proxy_pool = configure_proxies(proxy_config)
  # get_valid_proxy(proxy_pool)
  proxy_info = {
    'address': 'cm1.qqcdnxb.com',
    'port': 17000,
    'protocol': 'tcp',
    'encryption': 'auto'
  }

  # 连接到代理服务器并发送请求
  connect_to_proxy(proxy_info)
