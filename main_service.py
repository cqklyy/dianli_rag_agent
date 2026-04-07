from main_agent import main_agent
from data2sqlite import data2sqlite
from flask import Flask, jsonify,request
from flask_cors import CORS
import logging
import json
import time
from datetime import datetime
from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response as WerkzeugResponse

# 日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
# 关键配置：禁用所有缓存机制
app.config.update(
    JSON_AS_ASCII=False,  # 支持中文JSON响应
    TEMPLATES_AUTO_RELOAD=True,  # 模板自动重载
    SEND_FILE_MAX_AGE_DEFAULT=0,  # 静态文件立即过期
    SESSION_REFRESH_EACH_REQUEST=True  # 每次请求刷新会话
)
# 配置跨域支持
CORS(
    app,
    methods=['GET','POST','PUT'],
    allow_headers=['Content-Type', 'Authorization'],
    origins='*',
    supports_credentials=True
)


class SSEStreamResponse:
    """SSE流式响应封装类"""
    
    def __init__(self, generator, mimetype='text/event-stream'):
        self.generator = generator
        self.mimetype = mimetype
        self.headers = Headers()
        self._setup_headers()
    
    def _setup_headers(self):
        """设置SSE必要的响应头"""
        self.headers.add('Content-Type', 'text/event-stream; charset=utf-8')
        self.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.headers.add('Pragma', 'no-cache')
        self.headers.add('Expires', '0')
        self.headers.add('Connection', 'keep-alive')
        self.headers.add('X-Accel-Buffering', 'no')
        self.headers.add('Access-Control-Allow-Origin', '*')
        self.headers.add('Access-Control-Allow-Headers', '*')
        self.headers.add('Access-Control-Expose-Headers', '*')
        # Postman特定优化
        self.headers.add('Transfer-Encoding', 'chunked')
    
    def build_response(self):
        """构建Werkzeug Response对象"""
        return WerkzeugResponse(
            response=self.generator,
            status=200,
            headers=self.headers,
            direct_passthrough=True  # 启用直接传递，支持流式传输
        )

def format_sse_data(data, event_type=None, event_id=None):
    """格式化SSE数据格式
    
    SSE格式规范:
    data: {json_data}\n\n
    或带事件类型:
    event: message\ndata: {json_data}\n\n
    """
    lines = []
    
    if event_type:
        lines.append(f"event: {event_type}")
    
    if event_id:
        lines.append(f"id: {event_id}")

    
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, ensure_ascii=False)
    else:
        data_str = str(data)
    
    lines.append(f"data: {data_str}")

    sse_message = "\n".join(lines) + "\n\n"
    return sse_message.encode('utf-8')  # 关键修复：直接返回bytes

def stream_generator(question):
    """SSE流式数据生成器"""
    try:
        # 发送开始事件
        start_event = {
            'type': 'start', 
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'question': question
        }
        yield format_sse_data(start_event, event_type='start')
        
        # 流式处理问答
        response_text = ""
        
        for chunk in main_agent(question):
            if chunk:
                response_text += chunk
                
                # 发送内容块
                content_event = {
                    'type': 'content',
                    'content': chunk,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                yield format_sse_data(content_event, event_type='content')
        
        # 发送结束事件
        end_event = {
            'type': 'end',
            'complete_response': response_text,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        yield format_sse_data(end_event, event_type='end')
        
        logger.info(f"SSE流式回答完成，问题: {question}")
        
    except Exception as e:
        error_msg = f"流式输出错误: {str(e)}"
        logger.error(error_msg)
        error_event = {
            'type': 'error',
            'error': error_msg,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        yield format_sse_data(error_event, event_type='error')

# 根路径处理
@app.route('/', methods=['GET'])
def index():
    """根路径处理"""
    return jsonify({
        'message': '电力交易智能问答系统API服务',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'chat': '/api/chat',
            'chat_sse': '/api/chat/sse'  # 新增专门的SSE接口
        },
        'timestamp': datetime.now().isoformat()
    })

# 健康检查接口
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': '电力交易智能问答系统',
        'sse_support': True
    })

# 专门的SSE流式问答接口
@app.route('/api/chat/sse', methods=['POST'])
def chat_sse():
    """
    专门的SSE流式问答接口
    
    请求格式:
    {
        "question": "用户问题"
    }
    
    返回格式: text/event-stream
    """
    try:
        # 获取JSON请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体必须是JSON格式'}), 400
        
        # 提取参数
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        
        logger.info(f"SSE接口收到问题: {question}")
        
        # 创建SSE流生成器
        generator = stream_generator(question)
        
        # 使用Werkzeug封装SSE响应
        sse_response = SSEStreamResponse(generator)
        response = sse_response.build_response()
        
        return response
        
    except Exception as e:
        error_msg = f"SSE问答接口错误: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

# 兼容原有的问答接口（支持流式和非流式）
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    电力交易智能问答接口（兼容版本）
    
    请求格式:
    {
        "question": "用户问题",
        "stream": true   # 是否启用流式输出，默认为true
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体必须是JSON格式'}), 400
        
        question = data.get('question', '').strip()
        stream = data.get('stream', True)
        
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        
        logger.info(f"问答接口收到问题: {question}, 流式模式: {stream}")
        
        # 流式输出 - 使用新的SSE实现
        if stream:
            generator = stream_generator(question)
            sse_response = SSEStreamResponse(generator)
            return sse_response.build_response()
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

# 自动数据采集接口
@app.route('/api/data/collect', methods=['POST'])
def collect_data():
    """
    自动数据采集接口
    
    请求格式:
    {
        "response": "前端返回的响应"
    }
    
    返回格式:
    {
        "status": "success",
        "message": "数据采集完成",
        "timestamp": "2024-01-01 00:00:00"
    }
    """
    try:
        # 获取JSON请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体必须是JSON格式'}), 400
        
        # 提取参数
        response = data.get('response', '')
        
        logger.info(f"收到数据采集请求，前端响应: {response}")
        
        # 执行数据采集
        data2sqlite()
        
        result = {
            'status': 'success',
            'message': '数据采集完成',
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("数据采集任务执行完成")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"数据采集接口错误: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

# 获取知识库数据接口
@app.route('/api/data/get', methods=['GET'])
def get_knowledge_base_data():
    """
    获取知识库数据接口
    
    查询参数:
    - page: 页码，默认1
    - pageSize: 每页数量，默认10
    
    返回格式:
    {
        "data": [
            {
                "id": 1,
                "title": "标题",
                "content": "内容",
                "created_time": "2024-01-01 00:00:00"
            }
        ],
        "total": 100
    }
    """
    try:
        import sqlite3
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        pageSize = request.args.get('pageSize', 10, type=int)
        
        conn = sqlite3.connect('data/电力交易.db')
        conn.row_factory = sqlite3.Row  # 启用字典类型的行
        cursor = conn.cursor()
        
        # 查询总记录数
        cursor.execute('SELECT COUNT(*) FROM 电力交易数据')
        total = cursor.fetchone()[0]
        
        # 计算偏移量
        offset = (page - 1) * pageSize
        
        # 查询分页数据
        cursor.execute('SELECT id, title, content, created_time FROM 电力交易数据 ORDER BY created_time DESC LIMIT ? OFFSET ?', (pageSize, offset))
        rows = cursor.fetchall()
        
        # 转换为字典列表
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'title': row['title'],
                'content': row['content'],
                'created_time': row['created_time']
            })
        
        conn.close()
        
        # 返回分页数据
        result = {
            'data': data,
            'total': total
        }
        
        logger.info(f"获取知识库数据成功，第 {page} 页，每页 {pageSize} 条，共 {total} 条")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"获取知识库数据错误: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

# 添加知识库数据接口
@app.route('/api/data/add', methods=['POST'])
def add_knowledge_base_data():
    """
    添加知识库数据接口
    
    请求格式:
    {
        "title": "标题",
        "content": "内容"
    }
    
    返回格式:
    {
        "success": true,
        "data": {
            "id": 1,
            "title": "标题",
            "content": "内容"
        }
    }
    """
    try:
        import sqlite3
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体必须是JSON格式'}), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title:
            return jsonify({'error': '标题不能为空'}), 400
        
        conn = sqlite3.connect('data/电力交易.db')
        cursor = conn.cursor()
        
        # 插入数据
        cursor.execute(
            'INSERT OR IGNORE INTO 电力交易数据 (title, content) VALUES (?, ?)',
            (title, content)
        )
        
        # 获取插入的ID
        new_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        result = {
            'success': True,
            'data': {
                'id': new_id,
                'title': title,
                'content': content
            }
        }
        
        logger.info(f"添加知识库数据成功，ID: {new_id}, 标题: {title}")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"添加知识库数据错误: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

# 删除知识库数据接口
@app.route('/api/data/delete/<int:id>', methods=['DELETE'])
def delete_knowledge_base_data(id):
    """
    删除知识库数据接口
    
    返回格式:
    {
        "success": true
    }
    """
    try:
        import sqlite3
        
        conn = sqlite3.connect('data/电力交易.db')
        cursor = conn.cursor()
        
        # 删除数据
        cursor.execute('DELETE FROM 电力交易数据 WHERE id = ?', (id,))
        
        conn.commit()
        conn.close()
        
        result = {
            'success': True
        }
        
        logger.info(f"删除知识库数据成功，ID: {id}")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"删除知识库数据错误: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

# 更新知识库数据接口
@app.route('/api/data/update/<int:id>', methods=['PUT'])
def update_knowledge_base_data(id):
    """
    更新知识库数据接口
    
    请求格式:
    {
        "title": "标题",
        "content": "内容"
    }
    
    返回格式:
    {
        "success": true,
        "data": {
            "id": 1,
            "title": "标题",
            "content": "内容"
        }
    }
    """
    try:
        import sqlite3
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体必须是JSON格式'}), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title:
            return jsonify({'error': '标题不能为空'}), 400
        
        conn = sqlite3.connect('data/电力交易.db')
        cursor = conn.cursor()
        
        # 更新数据
        cursor.execute(
            'UPDATE 电力交易数据 SET title = ?, content = ? WHERE id = ?',
            (title, content, id)
        )
        
        conn.commit()
        conn.close()
        
        result = {
            'success': True,
            'data': {
                'id': id,
                'title': title,
                'content': content
            }
        }
        
        logger.info(f"更新知识库数据成功，ID: {id}, 标题: {title}")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"更新知识库数据错误: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': '请求方法不允许'}), 405

# 启动服务
if __name__ == '__main__':
    logger.info("电力交易智能问答系统服务启动...")
    logger.info("根路径: http://localhost:5000/")
    logger.info("健康检查接口: http://localhost:5000/health")
    logger.info("问答接口: http://localhost:5000/api/chat")
    logger.info("SSE问答接口: http://localhost:5000/api/chat/sse")
    logger.info("自动数据采集接口: http://localhost:5000/api/data/collect")
    
    # 生产环境建议设置debug=False
    app.run(host='0.0.0.0', port=5000, debug=True)