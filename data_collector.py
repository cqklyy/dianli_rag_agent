"""
数据收集模块
功能：
    1、通过Drissionpage实现相关的电力交易相关文本内容自动化数据收集
    2、开发每日数据更新的函数进行对当日时间电力交易相关文本内容自动化数据收集
"""
import traceback
import time
from DrissionPage import Chromium,ChromiumOptions
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
        self.result={}
        self.selectors={
            # 新闻列表选择器
            'news_list': 'xpath=//div[@class="cc-list-content"]/ul',
            # 新闻标题选择器
            'news_title': 'xpath=.//a//text()|.//a/text()',
            # 时间选择器
            'publish_time': 'xpath=.//span[contains(@class, "date")]/text()',
            # 新闻内容选择器
            'content': 'xpath=//div[@id="article_cont"]'
        }

    def _init_browser(self):
        logger.info('正在初始化浏览器...')
        co=ChromiumOptions()
        co.headless(True)   # 无头模式，不跳转界面
        self.browser=Chromium(addr_or_opts=co)
        return self.browser

    def data_collect_since(self,pages=5):
        """
        实现截止目前到pages页之间的电力交易报道的数据采集
        :param pages: 需要采集的页数
        :return:
            self.result:储存结果的json数据
        """
        browser=self._init_browser()
        logger.info('正在访问电力交易网...')
        tab=browser.latest_tab
        global url
        for page in range(1,pages+1):
            url=self.url+str(page)
            print(f'目前在访问第{page}页,地址为{url}')
            tab.get(url)
            print(tab.url)
            # 监听tag=ag=shoudian_detail_c_1的数据包
            tab.listen.start(targets='ag=shoudian_detail_c_1',method='GET')
            # 获取新闻列表
            news_titles=tab.ele(self.selectors['news_list'],timeout=10)
            if news_titles:
                # 拿到当页的报道列表
                news_list=news_titles.children()
                for news in news_list:
                    try:
                        news_title=news.ele('xpath=./a').text
                        news_time=news.ele('tag:span').text # 获取报道的时间
                        print(f'报道:{news_title}  日期:{news_time}')
                        logger.info(f'数据采集中...')
                        news.click()
                        news_id=tab.tab_id

                        # 等待指定元素出现在DOM中
                        tab=browser.latest_tab
                        tab.wait.ele_displayed(loc_or_ele=self.selectors['content'],timeout=5,raise_err=False)
                        # time.sleep(2)
                        article=tab.ele(self.selectors['content'],timeout=5).text

                        self.result[f'{news_title}']=article.strip()
                        # print(self.result['news_title'])

                        logger.info(f'报道《{news_title}》数据采集完成')
                        # 关闭当前页
                        tab.close()
                        # 回到进入链接的页面
                        tab=browser.get_tab(news_id)
                        time.sleep(1)

                    except Exception as e:
                        logger.error(f'报道《{news_title}》数据采集出错:{e}')
                        print(f'详细信息:{traceback.format_exc()}')
                        break

            else:
                logger.error('未获取报道列表元素，请检查')
                print(traceback.format_exc())
        if tab:
            tab.listen.stop()
        return self.result



if __name__=='__main__':
    collector=DataCollector()
    result=collector.data_collect_since(2)
    for tite,text in result.items():
        print(f'标题:{tite}\n内容:\n{text}')
