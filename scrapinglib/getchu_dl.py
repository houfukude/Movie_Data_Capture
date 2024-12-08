# -*- coding: utf-8 -*-

import re
import json
from urllib.parse import quote
from lxml import etree
from scrapinglib import httprequest
from .parser import Parser


class Getchu_dl(Parser):
    """ 二者基本一致
    headers extrafanart 略有区别
    現在この作品は販売停止中です。
    """
    expr_title = "//div[contains(@style,'color: #333333;')]/text()"
    expr_director = "//td[contains(text(),'原案')]/following-sibling::td/text()"
    expr_studio = "//td[contains(text(),'ジャンル')]/following-sibling::td/a/text()"
    expr_label = "//td[contains(text(),'ブランド')]/following-sibling::td/a/text()"
    expr_release = "//td[contains(text(),'登録日')]/following-sibling::td/text()"
    expr_tags = "//td[contains(text(),'カテゴリ')]/following-sibling::td/a/text()"

    expr_actor = "//table[@summary='情報2']//tr[3]/td[2]/a/text()"
    expr_outline = "//table[@summary='あらすじ']//tr[2]/td/p[2]/text()"
    expr_extrafanart = "//table[@summary='サンプル']//tr[2]/td/a/@href"

    def extraInit(self):
        self.imagecut = 4
        self.allow_number_change = True

        self.small_cover = ""

        self.cookies = {"adult_check_flag": "1"}
        self.extraheader = {"Referer": "https://dl.getchu.com/"}

        self.GETCHU_DL_SEARCH_URL = 'https://dl.getchu.com/search/search_list.php?search_category_id=&search_keyword=_WORD_&btnWordSearch=%B8%A1%BA%F7&action=search&set_category_flag=1'
        self.GETCHU_DL_URL = 'https://dl.getchu.com/i/item_WORD_'

    def queryNumberUrl(self, number):
        if "item" in number or 'GETCHU' in number.upper():
            self.number = re.findall(r'\d+', number)[0]
        else:
            queryUrl = self.GETCHU_DL_SEARCH_URL.replace("_WORD_", quote(number, encoding="euc_jp"))
            queryTree = self.getHtmlTree(queryUrl)
            detailurl = self.getTreeElement(queryTree, '//img[@class="goods_pic_sample"]/@src')
            self.cover_small = "http://dl.getchu.com" + detailurl  # .replace('../', '')
            if detailurl == "":
                return None

            self.number = re.findall(r'\d+', detailurl)[1]
        return self.GETCHU_DL_URL.replace("_WORD_", self.number)

    def getHtml(self, url, type=None):
        """ 通过 scraper 的方式访问网页(指定EUC-JP)
        """
        resp = self.get_by_scraper(url,  encoding='euc_jis_2004',  type=type)
        return resp

    def getNum(self, htmltree):
        return 'GETCHU-' + re.findall(r'\d+', self.number)[0]

    def getTitle(self, htmltree):
        title = super().getTitle(htmltree=htmltree)
        title = title.replace('【通常版】', '')
        title = title.replace('【HD版】', '')
        return title

    def getCover(self, htmltree):
        return self.cover_small.replace('small', 'top')

    def getRelease(self, htmltree):
        return super().getRelease(htmltree).replace('年', '-').replace('月', '-').replace('日', '')

    def getSmallCover(self, htmltree):
        return self.cover_small

    def extradict(self, dic: dict):
        return dic

    def getExtrafanart(self, htmltree):
        arts = self.getTreeAll(htmltree, self.expr_extrafanart)
        extrafanart = []
        for i in arts:
            i = "https://dl.getchu.com" + i
            extrafanart.append(i)
        return extrafanart

    def getTags(self, htmltree):
        tags = super().getTags(htmltree)
        tags.append("Getchu")
        tags.append("Animation")
        return tags
