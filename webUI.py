# iPhone 17 智能客服 - 简单版
import gradio as gr
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8012/v1/chat/completions"

def chat(message, history):
    """处理用户消息并返回回复"""
    if not message.strip():
        return ""
    
    try:
        data = {
            "messages": [{"role": "user", "content": message}],
            "stream": False,
            "userId": "user1",
            "conversationId": "conv1"
        }
        
        logger.info(f"发送请求: {message}")
        resp = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
            timeout=120
        )
        
        logger.info(f"响应状态: {resp.status_code}")
        result = resp.json()
        answer = result['choices'][0]['message']['content']
        logger.info(f"收到回复: {answer[:100]}...")
        return answer
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"⚠️ 连接失败: {str(e)}"

# Gradio ChatInterface
demo = gr.ChatInterface(
    fn=chat,
    title="🍎 iPhone 17 智能客服",
    description="有什么可以帮您？询问产品信息、价格、售后、配送等问题。",
    examples=[
        "iPhone 17 Pro Max 多少钱？",
        "退货政策是什么？",
        "什么时候发货？",
        "有哪些颜色可选？"
    ],
    theme="soft"
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7861)
