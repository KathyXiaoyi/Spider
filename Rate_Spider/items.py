# -*- coding: utf-8 -*-

from scrapy.item import Item, Field
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class LinkItem(Item):
    title = Field()
    link = Field()


class DetailItem(Item):
    # 日期
    Date = Field()
    # 美元
    Dollar = Field()
    # 欧元
    Euro = Field()
    # 日元
    Yen = Field()
    # 港元
    HKD = Field()
    # 英镑
    Pound = Field()
    # 澳大利亚元
    AUD = Field()
    # 新西兰元
    NZD = Field()
    # 新加坡元
    SGD = Field()
    # 瑞士法郎
    SF = Field()
    # 加拿大元
    CAD = Field()
    # 林吉特
    Ringgit = Field()
    # 俄罗斯卢布
    RUB = Field()
    # 南非兰特
    Rand = Field()
    # 韩元
    KRW = Field()
    # 阿联酋迪拉姆
    AED = Field()
    # 沙特里亚尔
    SR = Field()

