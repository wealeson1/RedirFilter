# coding=UTF-8

import requests
import click
import sys
import os
from urllib.parse import urlparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import ConnectionError, ConnectTimeout, TooManyRedirects
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

_https = 'https://'
_http = 'http://'
object_443 = {}
object_80 = {}


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-f', '--file', help="URL地址或者文件路径")
@click.option('-t', '--target', help='需过滤的域名')
@click.option('-T', '--targetfile', help='批量过滤文件')
@click.option('-o', '--output', help='结果保存文件')
def main(file, target, targetfile, output):
    run(file, target, targetfile, output)


def run(file, target, targetfile, output):
    """入口函数"""
    domain_list = []
    try:
        with open(file, 'r', encoding='utf8') as f:
            for url in f.readlines():
                domain_list.append(url.strip('\n'))
    except FileNotFoundError:
        click.secho("[ERROR] {file} 文件不存在，请检查文件".format(file=file), fg='red')
    except Exception as e:
        click.secho("[ERROR]" + str(e), fg='red')
    get_443(domain_list)
    get_80(domain_list)
    ProcessingRequestObjects(requests_objects=object_443, output=output, target=target, targetfile=targetfile)
    ProcessingRequestObjects(requests_objects=object_80, output=output, target=target, targetfile=targetfile)
    click.secho("[+] 结果已经保存在 {file}".format(file=output), fg='green')


def get_443(list):
    """ 获取https请求，结果存放在 object_443 """
    for url in list:
        url = _https + url
        try:
            _req = requests.get(url=url, verify=False, timeout=3)
            object_443[url] = _req  # 添加字典，key是url，value是url的requests.get()对象
            click.secho("[+] {url}   ===>   {req_url}".format(url=url, req_url=_req.url), fg='green')
        except KeyboardInterrupt:
            sys.exit()
        except ConnectionError:
            click.secho("[ERROR] {url} 请求失败，请检查域名是否可用".format(url=url), fg='red')
        except ConnectTimeout:
            click.secho("[ERROR] 连接超时，请检查网络是否可用", fg='red')
        except TooManyRedirects:
            click.secho("[ERROR] {url} 无限重定向".format(url=url), fg='red')
        except Exception as e:
            click.secho("[ERROR] " + str(e), fg='red')


def get_80(list):
    """获取http请求，结果存放在 object_80 """
    for url in list:
        url = _http + url
        try:
            _req = requests.get(url=url, verify=False, timeout=3)
            object_80[url] = _req
            click.secho("[+] {url}  ===>  {req_url}".format(url=url, req_url=_req.url), fg='green')
        except KeyboardInterrupt:
            sys.exit()
        except ConnectionError:
            click.secho("[ERROR] {url} 请求失败，请检查域名是否可用".format(url=url), fg='red')
        except ConnectTimeout:
            click.secho("[ERROR] 连接超时，请检查网络是否可用", fg='red')
        except TooManyRedirects:
            click.secho("[ERROR] {url} 无限重定向".format(url=url), fg='red')
        except Exception as e:
            click.secho("[ERROR] " + str(e), fg='red')


class ProcessingRequestObjects:
    """ 处理 http和https的 request 对象 """
    def __init__(self, requests_objects, output, target=None, targetfile=None):
        self._req_objects = requests_objects
        self.tem_param = None  # 作为临时中间存储变量或对象
        self.status_2xx = {}
        self.status_3xx = {}
        self.status_others = {}
        self.target = target
        self.targetfile = targetfile
        self.output = output
        self.filter_mathod = None
        self.check_status_code()
        self.check_target()
        self.select_method()
        self.output_file()

    def check_status_code(self):
        """ 检查 requests 对象的状态码并分配到相应的字典中 """
        _keys = self._req_objects.keys()
        for key in list(_keys):
            self.tem_param = self._req_objects[key]
            if self.tem_param.history:
                # print(self.tem_param.history[0].url)
                self.status_3xx[key] = self.tem_param
                self._req_objects.pop(key)
            elif self.tem_param.status_code == 200:
                # print(self.tem_param.url)
                self.status_2xx[key] = self.tem_param
                self._req_objects.pop(key)
            else:
                self.status_others[key] = self.tem_param

    def check_file(self, file):
        """检查文件是否存在"""
        if os.path.exists(file):
            return True
        else:
            click.secho("[ERROR] {file}文件不存在!".format(file=self.targetfile), fg='red')
            sys.exit()

    def check_target(self):
        """检查是否为批量过滤"""
        if self.target is not None and self.targetfile is not None:
            click.secho("[ERROR] -t 和 -T 只能选择一个", fg='red')
            sys.exit()
        elif self.target is not None:
            self.filter_mathod = 'target'
        elif self.targetfile is not None:
            self.filter_mathod = 'targetfile'
        else:
            self.filter_mathod = None

    def select_method(self):
        """选择过滤的方法"""
        if self.filter_mathod == 'target':
            self.target_mathod()
        elif self.filter_mathod == 'targetfile':
            self.targetfile_mathod()
        else:
            click.secho("[+] 只展示，不过滤", fg='green')
            sys.exit()

    def target_mathod(self):
        """单目标过滤"""
        for key in list(self.status_3xx.keys()):
            if self.target == urlparse(self.status_3xx[key].url).netloc:
                click.secho("[+] {url} ==> {redir_url} 已经删除".format(url=key, redir_url=self.status_3xx[key].url), fg='yellow')
                self.status_3xx.pop(key)

    def output_file(self):
        """输出结果到文件"""
        with open(self.output, mode='a+', encoding='utf8') as f:
            with open(self.output, mode='r', encoding='utf8') as f1:
                _result = []
                for x in f1.readlines():
                    _result.append(x.strip('\n'))
                for key in list(self.status_3xx.keys()):
                    url_parser = urlparse(key)
                    _netloc = url_parser.netloc
                    if url_parser.netloc not in _result:
                        f.write(_netloc + '\n')
                for key in list(self.status_2xx.keys()):
                    url_parser = urlparse(key)
                    if url_parser.netloc not in _result:
                        f.write(url_parser.netloc + '\n')
                for key in list(self.status_others.keys()):
                    url_parser = urlparse(key)
                    if url_parser.netloc + "   ===>   " + str(self.status_others[key].status_code) not in _result:
                        f.write(url_parser.netloc + "   ===>   " + str(self.status_others[key].status_code) + '\n')

    def targetfile_mathod(self):
        """批量过滤"""
        self.check_file(self.targetfile)
        with open(file=self.targetfile, mode='r', encoding='utf8') as f:
            for target in f.readlines():
                if ' ' not in target and '\t' not in target:  # 防止文件中含有回车换行
                    target = target.strip('\n')
                    self.target = target
                    self.target_mathod()


if __name__ == '__main__':
    main()
