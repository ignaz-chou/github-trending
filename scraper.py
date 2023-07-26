# coding:utf-8

import datetime
import codecs
import requests
import os
import time
from pyquery import PyQuery as pq
import openai
import os
# 从环境变量获取你的OpenAI的API密钥

openai.api_key = os.getenv("OPENAI_KEY")

def translate_text(english_text):
    # 调用OpenAI API进行翻译
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "You are a translator"},
        {"role": "user", "content": f"translate to chinese:{english_text}"},
        ]
    )
    print("response",response)
    translation = response['choices'][0]['message'].content  # 从response中提取翻译结果
    print("translation",translation)
    return translation

def git_add_commit_push(date, filename):
    # 这个函数用于向 git 添加、提交和推送文件
    cmd_git_add = 'git add {filename}'.format(filename=filename)  # 生成 git add 命令
    cmd_git_commit = 'git commit -m "{date}"'.format(date=date)  # 生成 git commit 命令
    cmd_git_push = 'git push -u origin master'  # 生成 git push 命令

    os.system(cmd_git_add)  # 执行 git add 命令
    os.system(cmd_git_commit)  # 执行 git commit 命令
    os.system(cmd_git_push)  # 执行 git push 命令


def createMarkdown(date, filename):
    # 这个函数用于创建一个 markdown 文件，并写入日期
    with open(filename, 'w') as f:
        f.write("## " + date + "-cn\n")  # 写入日期


def scrape(language, filename):
    # 这个函数用于抓取指定语言的 GitHub Trending 页面
    # 定义请求头
    HEADERS = {
        'User-Agent'		: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }

    url = 'https://github.com/trending/{language}'.format(language=language)  # 生成 URL
    r = requests.get(url, headers=HEADERS)  # 发起请求
    assert r.status_code == 200  # 断言响应码为 200
    
    d = pq(r.content)  # 通过 pyquery 解析 HTML
    items = d('div.Box article.Box-row')  # 选取每一个 trending 项目

    # 使用 codecs 打开文件，用于解决 utf-8 编码问题，如中文
    with codecs.open(filename, "a", "utf-8") as f:
        f.write('\n#### {language}\n'.format(language=language))  # 写入语言

        for item in items:
            i = pq(item)
            title = i(".lh-condensed a").text()
            owner = i(".lh-condensed span.text-normal").text()
            description = i("p.col-9").text()  # 获取项目描述
            description_cn = translate_text(description)  # 翻译项目描述
            url = i(".lh-condensed a").attr("href")
            url = "https://github.com" + url
            f.write(u"* [{title}]({url}):{description}//{description_cn}\n".format(title=title, url=url, description=description,description_cn=description_cn))



def job():
    # 主工作流程
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')  # 获取当前日期
    filename = '{date}.md'.format(date=strdate)  # 生成文件名

    createMarkdown(strdate, filename)  # 创建 markdown 文件

    # 抓取不同语言的 GitHub Trending 信息
    scrape('python', filename)
    scrape('typescript', filename)

    # scrape('swift', filename)
    scrape('javascript', filename)
    # scrape('go', filename)

    # git add commit push
    # git_add_commit_push(strdate, filename)  # 将 markdown 文件添加、提交和推送到 git


if __name__ == '__main__':
    job()  # 如果直接运行这个脚本，就执行主工作流程
