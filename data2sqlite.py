"""
数据存储模块
"""
from data_collector import DataCollector
import sqlite3
import logging
import warnings

warnings.filterwarnings('ignore')
# 配置日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def data2sqlite():
    data_collector = DataCollector()
    _sqlite()
    original_data = data_collector.data_collect_since(pages=1)
    # 打印
    # for tite, text in original_data.items():
    #     print(f'标题:{tite}\n内容:\n{text}')
    for title,text in original_data.items():
        # with open(f'./data/{title}.md','w',encoding='utf-8') as f:
        #     f.write(text)
        #     print(f'成功存储{title}数据')
        with sqlite3.connect(f'data/电力交易.db') as conn:
            cursor = conn.cursor()
            # 使用问号占位符的写法
            cursor.execute(
                'INSERT OR IGNORE INTO 电力交易数据 (title, content) VALUES (?, ?)',
                (title, text)
            )

            logger.info(f'《{title}》数据成功入库')


def _sqlite():
    """初始化sqlite数据库"""
    logger.info(f'正在初始化sqlite数据库...')
    conn = sqlite3.connect('data/电力交易.db')
    cursor = conn.cursor()

    # 创建表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS 电力交易数据 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            content TEXT,
            created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    logger.info(f'完成sqlite数据库初始化')


if __name__ == "__main__":
    data2sqlite()
    # _sqlite()

