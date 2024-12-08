# -*- coding: utf-8 -*-

import re
import json
from urllib.parse import quote
from lxml import etree
from scrapinglib import httprequest
from .parser import Parser


class Getchu(Parser):
    source = 'getchu'

    expr_title = '//*[@id="soft-title"]/text()'
    # expr_cover = '//head/meta[@property="og:image"]/@content'
    expr_director = "//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"
    expr_studio = "//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"
    expr_actor = "//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"
    expr_label = "//td[contains(text(),'ジャンル：')]/following-sibling::td/text()"
    expr_release = "//td[contains(text(),'発売日：')]/following-sibling::td/a/text()"
    expr_tags = "//td[contains(text(),'カテゴリ')]/following-sibling::td/a/text()"
    expr_outline = "//div[contains(text(),'ストーリー')]/following-sibling::div/text()"
    expr_extrafanart = "//div[contains(text(),'サンプル画像')]/following-sibling::div/a/@href"
    expr_series = "//td[contains(text(),'ジャンル：')]/following-sibling::td/text()"

    def extraInit(self):
        self.imagecut = 0
        self.allow_number_change = True

        self.cookies = {
            'getchu_adalt_flag': 'getchu.com',
            "adult_check_flag": "1"
        }
        self.extraheader = {
            'host': "www.getchu.com",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            'referer': "http://www.getchu.com/php/search_top.phtml?em=1",
        }
        self.GETCHU_WWW_SEARCH_URL = 'http://www.getchu.com/php/search.phtml?genre=anime_dvd&search_keyword={keyword}&check_key_dtl=1&submit='
        self.GETCHU_COVER_URL = 'http://www.getchu.com/brandnew/{id}/rc{id}package.jpg'
        self.GETCHU_DETAIL_URL = 'http://www.getchu.com/soft.phtml?id={id}'

    def queryNumberUrl(self, number):
        if "item" in number or 'GETCHU' in number.upper():
            self.number = re.findall(r'\d+', number)[0]
        else:
            queryUrl = self.GETCHU_WWW_SEARCH_URL.format(keyword=quote(number, encoding="euc_jp"))
            htmlTree = self.getHtmlTree(queryUrl)
            queryUrl = self.getTreeElement(htmlTree, '//a[@class="blueb"]/@href')
            self.number = re.findall(r'\d+', queryUrl)[0]
        return self.GETCHU_DETAIL_URL.format(id=self.number)

    def getHtml(self, url, type=None):
        """ 通过 scraper 的方式访问网页(指定EUC-JP)
        """
        resp = self.get_by_scraper(url,  encoding='euc_jis_2004',  type=type)
        return resp

    def getNum(self, htmltree):
        return 'GETCHU-' + re.findall(r'\d+', self.number)[0]

    def getActors(self, htmltree):
        return super().getDirector(htmltree)

    def getOutline(self, htmltree):
        outline = ''
        _list = self.getTreeAll(htmltree, self.expr_outline)
        for i in _list:
            outline = outline + i.strip()
        return outline

    def getCover(self, htmltree):
        cover = self.GETCHU_COVER_URL.format(id=self.number)
        return cover

    def getExtrafanart(self, htmltree):
        arts = super().getExtrafanart(htmltree)
        extrafanart = []
        for i in arts:
            i = "http://www.getchu.com" + i.replace("./", '/')
            if 'jpg' in i:
                extrafanart.append(i)
        return extrafanart

    def extradict(self, dic: dict):
        """ 额外新增的  headers
        """
        dic['headers'] = {'referer': self.detailurl}
        return dic

    def getTags(self, htmltree):
        tags = super().getTags(htmltree)
        tags.append("Getchu")
        tags.append("Animation")
        return tags
