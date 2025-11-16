"""
电力交易智能问答系统核心
"""
from data2sqlite import _sqlite
import openai
import sqlite3

def get_data():
    _sqlite()
    with sqlite3.connect('./data/电力交易.db') as conn:
        cursor = conn.cursor()
        sql_select='select * from 电力交易数据'
        cursor.execute(sql_select)
        db_data=cursor.fetchall()