"""
主接口服务
"""
from main_agent import main_agent
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import logging
import json
import time
from datetime import datetime

# 日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
# 配置跨域支持
CORS(
    app,
    methods=['GET','POST','PUT'],
    allow_headers=['Content-Type', 'Authorization'],
    origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
    supports_credentials=True
)

# 全局配置
app.config['JSON_AS_ASCII'] = False  # 支持中文JSON响应

# 健康检查接口
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': '电力交易智能问答系统'
    })


# 问答接口 - 支持JSON格式参数和流式输出
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    电力交易智能问答接口
    
    请求格式:
    {
        "question": "用户问题",
        "response": "",  # 可选，用于存储流式输出的数据流
        "stream": true   # 可选，是否启用流式输出，默认为true
    }
    
    返回格式:
    流式输出: text/event-stream
    非流式: JSON
    """
    try:
        # 获取JSON请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体必须是JSON格式'}), 400
        
        # 提取参数
        question = data.get('question', '').strip()
        stream = data.get('stream', True)
        
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        
        logger.info(f"收到问题: {question}")
        
        # 流式输出
        if stream:
            def generate():
                """生成器函数，用于流式输出"""
                try:
                    # 开始标记
                    yield f"data: {json.dumps({'type': 'start', 'timestamp': time.time()}, ensure_ascii=False)}\n\n"
                    
                    # 流式输出回答内容
                    response_text = ""
                    for chunk in main_agent(question):
                        response_text += chunk
                        # 发送内容块
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"
                    
                    # 结束标记
                    yield f"data: {json.dumps({'type': 'end', 'complete_response': response_text, 'timestamp': time.time()}, ensure_ascii=False)}\n\n"
                    
                    logger.info(f"流式回答完成，问题: {question}")
                    
                except Exception as e:
                    error_msg = f"流式输出错误: {str(e)}"
                    logger.error(error_msg)
                    yield f"data: {json.dumps({'type': 'error', 'error': error_msg}, ensure_ascii=False)}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
        
        else:
            # 非流式输出
            response_text = ""
            for chunk in main_agent(question):
                response_text += chunk
            
            result = {
                'question': question,
                'response': response_text,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            logger.info(f"非流式回答完成，问题: {question}")
            return jsonify(result)
    
    except Exception as e:
        error_msg = f"问答接口错误: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '接口不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

# 启动服务
if __name__ == '__main__':
    logger.info("电力交易智能问答系统服务启动...")
    logger.info("健康检查接口: http://localhost:5000/health")
    logger.info("问答接口: http://localhost:5000/api/chat")
    
    app.run(host='0.0.0.0', port=5000, debug=True)


