import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
import logging


# 设置日志模版
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 模型配置字典
MODEL_CONFIGS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "api_key": os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key"),
        "chat_model": "deepseek-chat",
        "embedding_model": "nomic-embed-text",
        "use_ollama_embedding": True
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "chat_model": "qwen2.5:7b",
        "embedding_model": "nomic-embed-text",
        "use_ollama_embedding": True
    },
    "openai": {
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "api_key": os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
        "chat_model": "gpt-4o-mini",
        "embedding_model": "text-embedding-3-small",
        "use_ollama_embedding": False
    }
}


DEFAULT_LLM_TYPE = "openai"
DEFAULT_TEMPERATURE = 0.7


class LLMInitializationError(Exception):
    """自定义异常类用于LLM初始化错误"""
    pass


def initialize_llm(llm_type: str = DEFAULT_LLM_TYPE):
    """初始化LLM实例"""
    try:
        if llm_type not in MODEL_CONFIGS:
            raise ValueError(f"不支持的LLM类型: {llm_type}. 可用的类型: {list(MODEL_CONFIGS.keys())}")

        config = MODEL_CONFIGS[llm_type]

        if llm_type == "ollama":
            os.environ["OPENAI_API_KEY"] = "NA"

        # 创建Chat LLM实例
        llm_chat = ChatOpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"],
            model=config["chat_model"],
            temperature=DEFAULT_TEMPERATURE,
            timeout=60,
            max_retries=2
        )

        # 创建Embedding实例
        if config.get("use_ollama_embedding", False):
            # 使用 OllamaEmbeddings（专门为Ollama设计）
            llm_embedding = OllamaEmbeddings(
                model=config["embedding_model"],
                base_url="http://localhost:11434"
            )
        else:
            # 使用 OpenAI Embeddings
            llm_embedding = OpenAIEmbeddings(
                base_url=config["base_url"],
                api_key=config["api_key"],
                model=config["embedding_model"]
            )

        logger.info(f"成功初始化 {llm_type} LLM")
        return llm_chat, llm_embedding

    except ValueError as ve:
        logger.error(f"LLM配置错误: {str(ve)}")
        raise LLMInitializationError(f"LLM配置错误: {str(ve)}")
    except Exception as e:
        logger.error(f"初始化LLM失败: {str(e)}")
        raise LLMInitializationError(f"初始化LLM失败: {str(e)}")


def get_llm(llm_type: str = DEFAULT_LLM_TYPE):
    """获取LLM实例"""
    try:
        return initialize_llm(llm_type)
    except LLMInitializationError as e:
        logger.warning(f"使用默认配置重试: {str(e)}")
        if llm_type != DEFAULT_LLM_TYPE:
            return initialize_llm(DEFAULT_LLM_TYPE)
        raise
