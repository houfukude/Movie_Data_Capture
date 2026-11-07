# -*- coding: utf-8 -*-

import json
import re
from urllib.parse import quote, urljoin

from lxml import etree

from .parser import Parser


class Airav(Parser):
    """airav.io（原 airav.wiki）

    NOTE: 站点已从 JSON API（/api/video/barcode/...）改为服务端渲染的 HTML 页面：
      * 搜索:   https://airav.io/search_result?kw=<番号>
      * 详情:   https://airav.io/video?hid=<id>
    旧实现依赖的 JSON 接口在新站返回 404，故改为解析 HTML。
    """

    source = 'airav'

    expr_title = '//h1/text()'
    expr_cover = '//meta[@property="og:image"]/@content'
    expr_outline = '//div[@class="video-info"]/p[@class="my-3"]/text()'

    BASE = 'https://airav.io'

    def extraInit(self):
        self.imagecut = 1
        self.htmlcode = ''

    # ------------------------------------------------------------------ 工具
    def _field(self, htmltree, key):
        """读取 <li class="my-2">番號： ADN-187</li> 这类键值行"""
        for li in htmltree.xpath('//li[contains(@class,"my-2")]'):
            text = ''.join(li.xpath('.//text()')).strip()
            if text.startswith(key):
                return text[len(key):].strip()
        return ''

    def _field_links(self, htmltree, key):
        """读取键值行里的 <a> 文本列表"""
        for li in htmltree.xpath('//li[contains(@class,"my-2")]'):
            text = ''.join(li.xpath('.//text()')).strip()
            if text.startswith(key):
                return [(a.text or '').strip() for a in li.xpath('.//a') if (a.text or '').strip()]
        return []

    def _jsonld(self):
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', self.htmlcode or '', re.S)
        if not m:
            return {}
        try:
            return json.loads(m.group(1))
        except Exception:
            return {}

    # ------------------------------------------------------------------ 搜索
    def search(self, number):
        self.number = number.strip().upper()
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
        else:
            search_code = self.getHtml(self.BASE + '/search_result?kw=' + quote(self.number))
            if not isinstance(search_code, str) or not search_code:
                return 404
            search_tree = etree.HTML(search_code)
            picked, fallback = None, None
            for a in search_tree.xpath('//a[contains(@href,"/video?hid=")]'):
                href = a.get('href')
                if not fallback:
                    fallback = href
                text = ' '.join(a.xpath('.//text()')).strip().upper()
                if self.number in text:
                    picked = href
                    break
            target = picked or fallback
            if not target:
                return 404
            self.detailurl = urljoin(self.BASE + '/', target)

        htmlcode = self.getHtml(self.detailurl)
        if not isinstance(htmlcode, str) or not htmlcode:
            return 404
        self.htmlcode = htmlcode
        htmltree = etree.HTML(htmlcode)

        # 番号校验，避免拿到搜索页第一个不相关的结果
        head = ''.join(htmltree.xpath(self.expr_title)).upper()
        if self.number not in head and self.number.replace('-', '') not in head.replace('-', ''):
            return 404
        return self.dictformat(htmltree)

    # ------------------------------------------------------------------ 字段
    def getNum(self, htmltree):
        num = self._field(htmltree, '番號：')
        if not num:
            head = ''.join(htmltree.xpath(self.expr_title)).strip()
            matched = re.match(r'^([A-Za-z0-9]+-[A-Za-z0-9]+)', head)
            num = matched.group(1) if matched else self.number
        self.number = num.upper()
        return self.number

    def getTitle(self, htmltree):
        head = ''.join(htmltree.xpath(self.expr_title)).strip()
        return head.replace(self.number, '', 1).strip()

    def getCover(self, htmltree):
        cover = self.getTreeElement(htmltree, self.expr_cover)
        if cover and not cover.startswith('http'):
            cover = 'https:' + cover
        return cover

    def getOutline(self, htmltree):
        return self.getTreeElement(htmltree, self.expr_outline).replace('\n', '').strip()

    def getActors(self, htmltree):
        return self._field_links(htmltree, '女優：')

    def getTags(self, htmltree):
        return self._field_links(htmltree, '標籤：')

    def getStudio(self, htmltree):
        links = self._field_links(htmltree, '廠商：')
        return links[0] if links else ''

    def getLabel(self, htmltree):
        links = self._field_links(htmltree, '廠商：')
        return links[0] if links else ''

    def getSeries(self, htmltree):
        return ''

    def getDirector(self, htmltree):
        return ''

    def getRelease(self, htmltree):
        # 页面只有 uploadDate（上传时间），不是发行日期，宁可留空
        return ''

    def getYear(self, htmltree):
        return ''

    def getRuntime(self, htmltree):
        # JSON-LD 的 duration 是预告片时长，不是正片时长，不使用
        return ''

    def getExtrafanart(self, htmltree):
        return []
