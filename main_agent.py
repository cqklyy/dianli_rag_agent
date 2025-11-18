"""
电力交易智能问答系统核心
"""
from data2sqlite import _sqlite
import sqlite3
from module_api import reranked_text,chat_agent

def get_data():
    _sqlite()
    title_text={}
    with sqlite3.connect('./data/电力交易.db') as conn:
        cursor = conn.cursor()
        sql_select='select * from 电力交易数据'
        cursor.execute(sql_select)
        db_data=cursor.fetchall()
        for data in db_data:
            title=data[1]
            text=data[2]
            title_text[title]=text
    if title_text:
        return title_text
    else:
        return None

def search_relax_text(query:str):
    title_text=get_data()
    if title_text:
        titles=title_text.keys()
        print(titles)
        reranked_texts=reranked_text(query,titles)
        return reranked_texts if reranked_texts else None
    else:
        return None

def main(query:str):
    try:
        reranked_texts=search_relax_text(query='11')
        response=chat_agent(query,reranked_texts)
        for chunk in response:
            yield chunk
    except Exception as e:
        yield f'电力交易智能问答系统发生错误:{e}'

if __name__ == '__main__':
    main()