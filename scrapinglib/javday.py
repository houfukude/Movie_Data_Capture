# -*- coding: utf-8 -*-

from lxml import etree
from .parser import Parser


class Javday(Parser):
    source = 'javday'

    expr_url = '/html/head/meta[@property="og:url"]/@content'
    expr_cover = '/html/head/meta[@property="og:image"]/@content'
    expr_tags = '/html/head/meta[@name="keywords"]/@content'
    expr_title = "/html/head/title/text()"
    expr_actor = "//span[@class='vod_actor']/a/text()"
    expr_studio = '//span[@class="producer"]/a/text()'
    expr_number = '//span[@class="jpnum"]/text()'

    def extraInit(self):
        self.imagecut = 4
        self.uncensored = True

    def search(self, number):
        self.number = number.strip().upper()
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
        else:
            self.detailurl = "https://javday.app/videos/" + self.number.replace("-", "") + "/"
        self.htmlcode = self.getHtml(self.detailurl)
        if self.htmlcode == 404:
            return 404
        htmltree = etree.fromstring(self.htmlcode, etree.HTMLParser())
        self.detailurl = self.getTreeElement(htmltree, self.expr_url)

        result = self.dictformat(htmltree)
        return result

    def getTitle(self, htmltree):
        title = super().getTitle(htmltree)
        # 删除番号和网站名。站名后缀实际是 "- JAVDAY"（原代码只处理了 "- JAVDAY.APP"），
        # 导致标题尾部残留 " - JAVDAY" 并带入命名
        result = title.replace(self.number, "")
        for suffix in ("- JAVDAY.APP", "- JAVDAY", "| JAVDAY"):
            result = result.replace(suffix, "")
        return result.strip()

    def getTags(self, htmltree) -> list:
        # keywords 形如 "SNOS-461,瀬戸環奈,,JAVDAY"，需要剔掉番号、演员、站名和空项。
        # 原来只过滤 'JAVDAY.APP'，实际站名是 'JAVDAY'，因此番号/演员/站名全部混进标签。
        tags = super().getTags(htmltree)
        actors = self.getTreeAll(htmltree, self.expr_actor)
        result = []
        for tag in tags:
            tag = tag.strip()
            if not tag:
                continue
            if 'JAVDAY' in tag.upper():
                continue
            if tag.upper() == self.number.upper():
                continue
            if tag in actors:
                continue
            result.append(tag)
        return result
