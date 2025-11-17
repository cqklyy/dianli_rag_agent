"""
电力交易智能问答系统核心
"""
from data2sqlite import _sqlite
from openai import OpenAI
import sqlite3

agent_config={
    'api_key':'sk-iuhzfmlhdkoohzupkbuvrisosbmibokygjfdvugjxszuwrrd',
    'base_url':"https://api.siliconflow.cn/v1",
    'lang_module':'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B',
    'rerank_module':'Qwen/Qwen3-Reranker-8B'
}


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
    else:
        return None

def rerank(query:str,chunk_list:list):
    title_text=get_data()

def main():
    search_relax_text(query='11')

if __name__ == '__main__':
    main()