import os


PROXY = 'http://127.0.0.1:7897'

def setup_proxy(proxy_url):
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url
