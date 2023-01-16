

from datetime import datetime
from random import random
from bs4 import BeautifulSoup

import requests
import base64
import argparse

BASE_URLS = [
    "http://jandan.net/pic",
    "http://jandan.net/treehole",
    "http://jandan.net/qa",
]

emojilist = ["😻", "🐸", "👽", "⚕️", "❤️", "👑"]

HELP_TEXT = """
me_in_jiandan v1.1 \033[0;34m注：\033[0m
无聊图总页数约为180，树洞约为80，问答约为10
若命令行支持，可以“ctrl+点击”打开url"""


class Configure:
    def __init__(self, userName: str, maxPages: int, isVerbose: bool) -> None:
        self.userName = userName
        self.maxPages = maxPages
        self.isVerbose = isVerbose

    def __repr__(self) -> str:
        return f"""
[当前配置]
userName:   {self.userName}
maxPages:   {self.maxPages}
isVerbose:  {self.isVerbose}
        """


class Crawler:
    def __init__(self, base_url, configure: Configure) -> None:
        self.configure = configure
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"
        }
        self.results = list()
        self.curpage = 0

    def get_max_pages(self, raw: BeautifulSoup) -> int:
        try:
            return int(
                str(raw.find_all(class_="current-comment-page")[0])
                .split("[")[-1]
                .split("]")[0]
            )
        except Exception as e:
            print(e if self.configure.isVerbose else "出错了")

    def find_post_in_page(self, url: str, page: BeautifulSoup) -> list:
        result_map = []
        result = []
        for comment in [
            x
            for x in page.select(".commentlist>li")
            if self.configure.userName in str(x.select(".author>strong"))
        ]:
            try:
                result_map.append(
                    {
                        "type": url.split("jandan.net/")[1].split("/")[0],
                        "url": "http://jandan.net/t/"
                        + comment.select(".righttext>a")[0].text,
                        "oo": comment.select(".tucao-like-container")[0]
                        .select("span")[0]
                        .text,
                        "xx": comment.select(".tucao-unlike-container")[0]
                        .select("span")[0]
                        .text,
                        "tucao": comment.select(".tucao-btn")[0].text,
                    }
                )
            except IndexError as e:
                if self.configure.isVerbose:
                    print(e)
                continue
        for jsonitem in result_map:
            result.append(
                f"{jsonitem['url']}\too {jsonitem['oo']}\t xx {jsonitem['xx']}\t{jsonitem['tucao']}"
            )
        if self.configure.isVerbose:
            print(f"Page {self.curpage} Found {len(result)} item(s).")
        else:
            if len(result) != 0:
                emoji = emojilist[int((random() * 100)) % len(emojilist)]
                # emoji = emojilist[len(result)]
                print(f"Page {self.curpage}: {len(result)} " + emoji)
        return result

    def craw(self) -> list:
        bs = BeautifulSoup(
            requests.get(self.base_url, headers=self.headers).text, "html.parser"
        )
        self.max_pages = self.get_max_pages(bs)

        crawpagecount = self.configure.maxPages
        if self.configure.isVerbose:
            print("⚡crawpagecount:" + str(crawpagecount))

        for i in range(self.max_pages, self.max_pages - crawpagecount, -1):
            if i < 1:
                break
            url = (
                self.base_url
                + "/"
                + base64.urlsafe_b64encode(
                    (
                        datetime.now().strftime("%Y%m%d").__str__() + "-" + str(i)
                    ).encode()
                ).decode()
            )
            self.curpage = i
            try:
                resp = requests.get(url, headers=self.headers)
            except Exception as e:
                print(
                    "Something went wrong!" + e
                    if self.configure.isVerbose
                    else "Something went wrong!"
                )
            if not resp.ok:
                print("Oops! Something went wrong!")
                continue
            # if pic or treehole
            self.results += self.find_post_in_page(
                url, BeautifulSoup(resp.text, "html.parser")
            )
        return self.results


def process_arguments():
    parser = argparse.ArgumentParser(description=HELP_TEXT)
    parser.add_argument(
        "--username",  # 用户名设置，必填，推荐使用全名，因为是模糊匹配的。
        "-u",
        metavar="Username",
        type=str,
        action="store",
        required=True,
        help="目标用户名",
        dest="userName",
    )
    parser.add_argument(
        "--max-pages",  # 爬取的最大页数，越多越卡，因为没开多线程
        "-m",
        metavar="N",
        default=30,  # default 30 不然网友发的太多根本爬不到自己发的都顶掉了
        type=int,
        action="store",
        required=False,
        help="最大爬取页面",
        dest="maxPages",
    )
    parser.add_argument(
        "--verbose",  # 是否显示详细信息（废话模式）
        "-v",
        default=False,
        action="store_true",
        help="废话模式",
        dest="isVerbose",
    )
    args = parser.parse_args()
    return Configure(args.userName, args.maxPages, args.isVerbose)


def main():
    arguments = process_arguments()
    print(arguments)

    print("🐢爬行中…")
    for url in BASE_URLS:
        print(f"\033[0;33m{url}\033[0m")
        linklist = Crawler(url, arguments).craw()
        if len(linklist) > 0:
            print("\033[0;32m" + str(len(linklist)) + " result(s) found" + "\033[0m")
            for link in linklist:
                print(link)
        else:
            print("\033[0;31mno result found\033[0m")
        print("")
    print("🐢爬完啦~")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("出错了！")
        print(e)
    except KeyboardInterrupt:
        print("取消！")
