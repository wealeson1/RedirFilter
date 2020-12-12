# RedirFilter

## 运行环境
+ Python3.6.X及其以上版本
+ 第三方库: click, requests
+ 测试环境: Windows10

## 工具使用场景

在进行域名收集后发现很多域名都重定向到另一个或多个域名。
RedirFilter 还会检查域名的存活情况，2xx 和 3xx 不做标记，4xx 和 5xx 会在后面标注。

## 工具参数说明

```
Usage: RedirFilter.py [OPTIONS]

Options:
  -f, --file TEXT        URL地址或者文件路径
  -t, --target TEXT      需过滤的域名
  -T, --targetfile TEXT  批量过滤文件
  -o, --output TEXT      结果保存文件
  -h, --help             Show this message and exit.

```