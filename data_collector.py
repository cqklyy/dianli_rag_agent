"""
数据收集模块
功能：
    1、通过Drissionpage实现20240101-至今相关的电力交易相关文本内容自动化数据收集
    2、开发每日数据更新的函数进行对当日时间电力交易相关文本内容自动化数据收集
"""

from DrissionPage import ChromiumPage
import logging
import warnings

warnings.filterwarnings('ignore')
# 配置日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DataCollector:
    def __init__(self):
        self.url='https://shoudian.bjx.com.cn/dljy/'
        self.page=ChromiumPage()
        self.selectors={
            # 新闻列表选择器
            'news_list': 'xpath=//div[@class="cc-list-content"]//li',
            # 新闻标题选择器
            'news_title': 'xpath=.//a//text()|.//a/text()',
            # 新闻链接选择器
            'news_link': 'xpath=.//a/@href',
            # 时间选择器
            'publish_time': 'xpath=.//span[contains(@class, "date")]/text()',
            # 新闻内容选择器
            'content': 'xpath=//div[@id="article_cont"]',
            # 新闻标题选择器
            'detail_title': 'xpath=//div[@class="box"]/h1',
            # 翻页选择器
            'next_page': 'xpath=//a[contains(text(),"下一页")]'
        }
