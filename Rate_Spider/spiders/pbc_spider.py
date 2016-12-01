# coding=utf-8

import time
import re
import json
from scrapy import Spider
from scrapy import log
from selenium import webdriver
from Rate_Spider.items import LinkItem, DetailItem

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class PbcSpider(Spider):

    name = 'pbc'
    allowed_domains = ['pbc.gov.cn']
    start_urls = ['http://www.pbc.gov.cn/zhengcehuobisi/125207/125217/125925/index.html']

    # 爬取所有的链接
    def get_links(self, browser, url):
        # 待返回的LinkItem列表
        item_list = []
        try:
            browser.get(url)
            time.sleep(2)
            # 找到所有的链接
            # 获得总的条目数
            total_num_info = browser.find_element_by_xpath("//td[@class='Normal']").text
            # 数据总条数
            total_num = int(total_num_info[5:8])
            # 每页显示的条数
            page_num = int(total_num_info[13:15])
            pages = total_num / page_num + 1
            # 获取第一页的链接
            links = browser.find_elements_by_xpath("//font[@class='newslist_style']/a")
            for link in links:
                item = LinkItem()
                item['title'] = link.text
                item['link'] = link.get_attribute('href')
                item_list.append(item)
            browser.find_element_by_xpath("//a[@class='pagingNormal'][1]").click()
            # 获取第2页——第31页的数据
            for i in range(1, pages):
                links = browser.find_elements_by_xpath("//font[@class='newslist_style']/a")
                for link_temp in links:
                    item = LinkItem()
                    item['title'] = link_temp.text
                    item['link'] = link_temp.get_attribute('href')
                    item_list.append(item)
                # 模拟点击“下一页”
                browser.find_element_by_xpath("//a[@class='pagingNormal'][3]").click()
                time.sleep(3)
        except Exception, e:
            print e
        return item_list

    # 获取给定链接页面中的汇率信息
    def get_data(self, browser, url):
        try:
            detail_item = DetailItem()
            browser.get(url)
            time.sleep(2)
            # 获取正文
            content = browser.find_element_by_xpath("//td[@class='content']/div").text
            content = content.encode('utf-8')
            # 获取日期
            pattern = re.compile(r'\d+年\d+月\d+日')
            date = pattern.search(content)
            if date:
                detail_item['Date'] = date.group()
            else:
                print 'none'

            content = content.replace(' ', '')
            content = content.replace('。', '，')
            for i in (',', ':', '：'):
                content = content.replace(i, '，')
            info_list = content.split('，')
            # 使用正则表达式匹配出所有的汇率
            pattern1 = re.compile('\S+对人民币\S+')
            pattern2 = re.compile('人民币1元对\S+')

            for info in info_list:
                # 对字符串进行一些预处理：最后增加一个'.'；删除前后的空格
                info += '.'
                info = info.strip()
                match = pattern1.search(info)
                if match:
                    begin = info.index('对人民币')
                    end = info.index('元.')
                    value = info[begin + 12: end]
                    name_temp = info[0:begin]
                    pattern5 = re.compile('\D+')
                    name = pattern5.search(name_temp)
                    true_name = self.map(name.group())
                    detail_item[true_name] = value
                elif pattern2.match(info):
                    info = info[16:]
                    # 分别匹配数字和非数字
                    pattern3 = re.compile('\d+.\d+')
                    value = pattern3.search(info)
                    if value:
                        value = value.group()
                        index = value.__len__()
                        name = info[index:-1]
                        true_name = self.map(name)
                        # 对value进行处理，转化为1单位外币对应***人民币
                        value = 1.0 / float(value)
                        detail_item[true_name] = value
                    else:
                        print 'value is none'
                else:
                    pass

        except Exception, e:
            print 'Exception!'
            print e
        return detail_item

    # 汉语名称和类属性的映射
    def map(self, key):
        dict_map = {'日期': 'Date', '美元': 'Dollar', '欧元': 'Euro','日元': 'Yen', '港元': 'HKD', '英镑':'Pound',
                    '澳大利亚元': 'AUD', '新西兰元': 'NZD', '新加坡元': 'SGD', '瑞士法郎': 'SF',  '加拿大元': 'CAD',
                    '林吉特': 'Ringgit', '俄罗斯卢布': 'RUB', '南非兰特': 'Rand', '韩元': 'KRW', '阿联酋迪拉姆': 'AED',
                    '沙特里亚尔': 'SR'};
        return dict_map.get(key)

    # 从links.txt中读取所有链接
    def get_stored_links(self):
        # 待返回的LinkItem列表
        item_list = []
        file_temp = open('links.txt')
        for line in file_temp.readlines():
            item = LinkItem()
            index = line.find(':')
            item['title'] = line[0:index - 1]
            item['link'] = line[index+1:-1]
            item_list.append(item)
        file_temp.close()
        return item_list

    def parse(self, response):
        browser = webdriver.Chrome()
        # 使用下面这行代码，可以通过模拟点击的方式，获取所有的链接
        # links = self.get_links(browser, self.start_urls[0])

        # 为节约时间，直接从links.txt文件中读取已保存的链接（共608个链接）
        links = self.get_stored_links()
        file_temp = open('rate.txt', 'w')
        # 写入rate.txt文件中
        for link in links:
            # 对每一个link 解析 获得数据
            detail_item = self.get_data(browser, link['link'])
            # 写入rate.txt文件中
            dict_temp = detail_item.__dict__
            file_temp.write(json.dumps(dict_temp) + '\n')
            yield detail_item
        browser.close()








