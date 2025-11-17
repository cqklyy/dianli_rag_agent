"""
模型调用模块
"""
import traceback
from openai import OpenAI
import requests
from typing import List, Dict, Any

agent_config={
    'api_key':'sk-ikuwkmunggtqrigwxbzlmampmetjrzxdyrhvrfswowswhmsm',
    'base_url':"https://api.siliconflow.cn/v1",
    'lang_module':'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B',
    'rerank_module':'Qwen/Qwen3-Reranker-8B'
}

def rerank_documents(query: str, documents: List[str], top_k: int = 3) -> List[Dict]:
    """
    基于重排序模型Qwen/Qwen3-Reranker-8B对新闻题目进行相关性排序

    Args:
        query: 查询问题
        documents: 题目列表
        top_k: 返回最相似的前k个文本

    Returns:
        排序后的题目列表，包含题目内容和相似度分数
    """
    # 硅基流动的重排序API端点
    url = f"{agent_config['base_url']}/rerank"

    headers = {
        "Authorization": f"Bearer {agent_config['api_key']}",
        "Content-Type": "application/json"
    }

    # 构建请求数据
    payload = {
        "model": agent_config['rerank_module'],  # 重排序模型
        "query": query,
        "documents": documents,
        "top_n": top_k  # 返回前top_k个结果
    }

    try:
        # 发送API请求
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        result = response.json()
        print(result)

        # 处理返回结果
        ranked_documents = []
        for item in result["results"]:
            doc_index = item["index"]
            relevance_score = item["relevance_score"]

            ranked_documents.append({
                "document": documents[doc_index],
                "relevance_score": relevance_score,
                "rank": len(ranked_documents) + 1
            })

        # 按相似度分数降序排列
        ranked_documents.sort(key=lambda x: x["relevance_score"], reverse=True)

        return ranked_documents[:top_k]

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e}")
        print(f'详细信息:{traceback.format_exc()}')
        return []
    except KeyError as e:
        print(f"响应解析错误: {e}")
        print(f'详细信息:{traceback.format_exc()}')
        return []



if __name__ == "__main__":
    documents=['宁夏2025年迎峰度冬有序用电（负荷管理）实施方案：有序用电方案规模应不低于本地区历史最高负荷的30%', '报价低于成本价！2026年电力零售市场“卷价格”的风险与应对', '广西新能源市场化电量达526.88亿千瓦时', '全国统一电力市场初步建成 97万家市场经营主体在全球最大“电力卖场”交易', '广西电力市场是真蓝海还是新内卷？关键要点解析', '国网能源院专家：以规则制度赋能全国统一电力市场建设', '河南电力现货市场近期试运行分析']
    query='广西电力市场'
    reranked_text=rerank_documents(query, documents)
    print(reranked_text)



