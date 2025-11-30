"""
电力交易智能问答系统核心
"""
from data2sqlite import _sqlite
import sqlite3
from module_api import rerank_documents,chat_agent

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
    # print(f'获取到的知识文本:\n{title_text}')

    if title_text:
        titles=title_text.keys()
        # print(f'对应标题有:{titles}')
        reranked_texts=rerank_documents(query,list(titles),top_k=3)
        print(f'获取到的相关标题:{reranked_texts}')
        text_list=[]
        for i in reranked_texts:
            # print(i)
            title=i['document']
            text=title_text[title]
            text_list.append(text)
            # print(f'最终相关文本:{text_list}')
        return text_list if text_list else None
    else:
        return None

def main(query:str):
    try:
        reranked_texts=search_relax_text(query=query)
        # print(f'查询到的相关文本:\n{reranked_texts}')
        response=chat_agent(query,reranked_texts)
        for chunk in response:
            yield chunk
    except Exception as e:
        yield f'电力交易智能问答系统发生错误:{e}'

if __name__ == '__main__':
    print(f'正在为您回答问题...')
    response=main(query='福建省电力中长期市场交易方案怎么样')
    for chunk in response:
        print(chunk,end='',flush=True)
