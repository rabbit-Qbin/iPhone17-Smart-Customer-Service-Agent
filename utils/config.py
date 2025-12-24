# config.py
import os

# 获取项目根目录（iPhone17系列产品_RagAgent目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """统一的配置类，集中管理所有常量"""
    # prompt文件路径（使用绝对路径）
    PROMPT_TEMPLATE_TXT_AGENT = os.path.join(BASE_DIR, "prompts/prompt_template_agent.txt")
    PROMPT_TEMPLATE_TXT_GRADE = os.path.join(BASE_DIR, "prompts/prompt_template_grade.txt")
    PROMPT_TEMPLATE_TXT_REWRITE = os.path.join(BASE_DIR, "prompts/prompt_template_rewrite.txt")
    PROMPT_TEMPLATE_TXT_GENERATE = os.path.join(BASE_DIR, "prompts/prompt_template_generate.txt")

    # Chroma 数据库配置（使用绝对路径）
    CHROMADB_DIRECTORY = os.path.join(BASE_DIR, "chromaDB")
    CHROMADB_COLLECTION_NAME = "iphone17_knowledge"

    # 日志持久化存储（使用绝对路径）
    LOG_FILE = os.path.join(BASE_DIR, "output/app.log")
    MAX_BYTES = 5*1024*1024
    BACKUP_COUNT = 3

    # 数据库 URI
    DB_URI = os.getenv("DB_URI", "postgresql://postgres:postgres@localhost:5432/postgres?sslmode=disable")

    # LLM类型: deepseek, openai, ollama
    LLM_TYPE = "deepseek"

    # API服务地址和端口
    HOST = "0.0.0.0"
    PORT = 8012
