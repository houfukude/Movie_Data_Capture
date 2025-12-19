# -*- coding: utf-8 -*-

import re
import urllib.parse
from .parser import Parser


class Dlsite(Parser):
    source = 'dlsite'

    expr_title = '/html/head/title/text()'
    expr_actor = '//th[contains(text(),"声优")]/../td/a/text()'
    expr_studio = '//th[contains(text(),"商标名")]/../td/span[1]/a/text()'
    expr_studio2 = '//th[contains(text(),"社团名")]/../td/span[1]/a/text()'
    expr_runtime = '//strong[contains(text(),"時長")]/../span/text()'
    expr_runtime2 = '//strong[contains(text(),"時長")]/../span/a/text()'
    expr_outline = '//*[@class="work_parts_area"]/p/text()'
    expr_series = '//th[contains(text(),"系列名")]/../td/span[1]/a/text()'
    expr_series2 = '//th[contains(text(),"社团名")]/../td/span[1]/a/text()'
    expr_director = '//th[contains(text(),"剧情")]/../td/a/text()'
    expr_release = '//th[contains(text(),"贩卖日")]/../td/a/text()'
    expr_cover = '//*[@id="work_left"]/div/div/div[2]/div/div[1]/div[1]/ul/li[1]/picture/source/@srcset'
    expr_tags = '//th[contains(text(),"分类")]/../td/div/a/text()'
    expr_label = '//th[contains(text(),"系列名")]/../td/span[1]/a/text()'
    expr_label2 = '//th[contains(text(),"社团名")]/../td/span[1]/a/text()'
    expr_extrafanart = '//*[@id="work_left"]/div/div/div[1]/div/@data-src'

    keyword_strategies = [
        # 原始关键词
        lambda k: k,
        # 移除动画相关后缀
        lambda k: k.replace("THE ANIMATION", "").replace("he Animation", "").replace("t", "").replace("T", ""),
        # 波浪号转换
        lambda k: k.replace("～", "〜") if "～" in k else k.replace("〜", "～") if "〜" in k else k,
        # 移除卷标
        lambda k: k.replace('上巻', '').replace('下巻', '').replace('前編', '').replace('後編', ''),
    ]

    def extraInit(self):
        self.imagecut = 4
        self.allow_number_change = True
        # 设置反反爬虫头信息
        self.extraheader = {
            'Referer': 'https://www.dlsite.com/maniax/',
        }

    def search(self, number):
        self.cookies = {'locale': 'zh-cn'}
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
            # TODO 应该从页面内获取 number
            self.number = str(re.findall(r"\wJ\w+", self.detailurl)).strip(" [']")
            htmltree = self.getHtmlTree(self.detailurl)
        elif "RJ" in number or "VJ" in number:
            self.number = number.upper()
            self.detailurl = 'https://www.dlsite.com/maniax/work/=/product_id/{}.html/?locale=zh_CN'
            self.detailurl = self.detailurl.format(self.number)
            htmltree = self.getHtmlTree(self.detailurl)
        else:
            search_url = 'https://www.dlsite.com/maniax/fsr/=/language/jp/sex_category/male/keyword/{}/order/trend/work_type_category/movie'
            detail_xpath = '//*[@id="search_result_img_box"]/li[1]/dl/dd[2]/div[2]/a/@href'
            self.detailurl = None
            for i, strategy in enumerate(self.keyword_strategies):
                search_keyword = strategy(number)  # 修复：使用参数 number
                if not search_keyword.strip():  # 跳过空关键词
                    continue

                encoded_keyword = urllib.parse.quote(search_keyword.strip())
                # DLsite 搜索会将空格编码为 + 而不是 %20 ，这样可以避免 Cloudflare 的 403 拦截
                encoded_keyword = encoded_keyword.replace('%20', '+')
                strategied_url = search_url.format(encoded_keyword)
                # print(f"搜索策略 {i+1}: {strategied_url}")
                try:
                    search_tree = self.getHtmlTree(strategied_url)
                    search_result = self.getTreeAll(search_tree, detail_xpath)
                    # print(f"搜索结果: {search_tree} {search_result}")
                    if len(search_result) > 0:
                        self.detailurl = search_result[0]
                        # print(f"搜索策略 {i+1} 成功: {self.detailurl}")
                        break
                except Exception as e:
                    # print(f"搜索策略 {i+1} 失败: {e}")
                    continue

            if not self.detailurl:
                print(f"[-] [dlsite] 无法找到关键词 '{number}' 对应的作品，已尝试所有搜索策略")
                return ""  # 明确返回 None 而不是抛出异常

            htmltree = self.getHtmlTree(self.detailurl)
            self.number = str(re.findall(r"\wJ\w+", self.detailurl)).strip(" [']")

        result = self.dictformat(htmltree)
        return result

    def getNum(self, htmltree):
        return self.number

    def getTitle(self, htmltree):
        result = super().getTitle(htmltree)
        result = result[:result.rfind(' | DLsite')]
        result = result[:result.rfind(' [')]
        if 'OFF】' in result:
            result = result[result.find('】')+1:]
        result = result.replace('【HD版】', '')
        return result

    def getOutline(self, htmltree):
        total = []
        result = self.getTreeAll(htmltree, self.expr_outline)
        total = [x.strip() for x in result if x.strip()]
        return '\n'.join(total)

    def getRelease(self, htmltree):
        return super().getRelease(htmltree).replace('年', '-').replace('月', '-').replace('日', '')

    def getCover(self, htmltree):
        return 'https:' + super().getCover(htmltree).replace('.webp', '.jpg')

    def getExtrafanart(self, htmltree):
        try:
            result = []
            for i in self.getTreeAll(self.expr_extrafanart):
                result.append("https:" + i)
        except:
            result = ''
        return result

    def getTags(self, htmltree):
        tags = super().getTags(htmltree)
        tags.append("DLsite")
        return tags
