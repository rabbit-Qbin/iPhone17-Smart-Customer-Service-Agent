# 功能：将iPhone 17知识库txt文件向量化并存入ChromaDB
import logging
import os
import uuid
import chromadb
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ 配置区域 ============
# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 知识库txt文件目录（项目内的知识库）
KNOWLEDGE_BASE_DIR = os.path.join(SCRIPT_DIR, "knowledge_base")

# ChromaDB存储位置和集合名称（使用绝对路径）
CHROMADB_DIRECTORY = os.path.join(SCRIPT_DIR, "chromaDB")
CHROMADB_COLLECTION_NAME = "iphone17_knowledge"

# Ollama配置
OLLAMA_BASE_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text:latest"
# ============ 配置结束 ============


class OllamaEmbeddings:
    """Ollama Embedding 封装类"""
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批量计算文档向量，带进度显示"""
        embeddings = []
        total = len(texts)
        for i, text in enumerate(texts):
            logger.info(f"  计算向量 {i+1}/{total}...")
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> list[float]:
        """计算单个查询向量"""
        return self._get_embedding(text)
    
    def _get_embedding(self, text: str) -> list[float]:
        """调用Ollama API获取向量，带重试"""
        # 清洗并截断文本
        text = clean_text(text)
        if len(text) > 500:  # 更保守的截断
            text = text[:500]
        
        # 最多重试3次
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=120
                )
                if response.status_code == 500:
                    logger.warning(f"  Ollama 500错误，文本长度: {len(text)}，尝试截断...")
                    text = text[:len(text)//2]  # 截断一半再试
                    continue
                response.raise_for_status()
                return response.json()["embedding"]
            except Exception as e:
                if attempt < 2:
                    logger.warning(f"  重试 {attempt + 1}/3: {e}")
                    import time
                    time.sleep(2)
                else:
                    logger.error(f"  最终失败，返回零向量。文本: {text[:50]}...")
                    return [0.0] * 768  # 返回零向量避免整体失败


def get_embedding_function():
    """获取embedding函数"""
    return OllamaEmbeddings(
        base_url=OLLAMA_BASE_URL,
        model=EMBEDDING_MODEL
    )


def load_txt_files(directory: str) -> list[dict]:
    """
    递归加载目录下所有txt文件
    
    Returns:
        list[dict]: [{"content": "文件内容", "source": "文件路径", "category": "分类"}]
    """
    documents = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                # 获取分类（父文件夹名）
                category = os.path.basename(root)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            documents.append({
                                "content": content,
                                "source": file,
                                "category": category
                            })
                            logger.info(f"已加载: {category}/{file}")
                except Exception as e:
                    logger.error(f"读取文件失败 {file_path}: {e}")
    
    return documents


def clean_text(text: str) -> str:
    """
    清洗文本，移除可能导致embedding失败的特殊字符
    """
    import re
    # 移除零宽字符和其他不可见字符
    text = re.sub(r'[\u200b-\u200f\u2028-\u202f\u205f-\u206f\ufeff]', '', text)
    # 将中文标点统一处理
    text = text.replace('「', '"').replace('」', '"')
    text = text.replace('『', '"').replace('』', '"')
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_document(doc: dict, chunk_size: int = 300, overlap: int = 50) -> list[dict]:
    """
    将长文档切分成小块
    
    Args:
        doc: 文档字典
        chunk_size: 每块最大字符数（改小到300）
        overlap: 块之间重叠字符数
    
    Returns:
        list[dict]: 切分后的文档块列表
    """
    content = clean_text(doc["content"])
    chunks = []
    
    # 如果文档较短，不切分
    if len(content) <= chunk_size:
        return [{
            "content": content,
            "source": doc["source"],
            "category": doc["category"]
        }]
    
    # 按换行切分（单个\n也切）
    paragraphs = content.split('\n')
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += para + " "
        else:
            if current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "source": doc["source"],
                    "category": doc["category"]
                })
            # 如果单个段落就超过chunk_size，强制切分
            if len(para) > chunk_size:
                for i in range(0, len(para), chunk_size - overlap):
                    chunk_text = para[i:i + chunk_size]
                    if chunk_text.strip():
                        chunks.append({
                            "content": chunk_text.strip(),
                            "source": doc["source"],
                            "category": doc["category"]
                        })
                current_chunk = ""
            else:
                current_chunk = para + " "
    
    # 添加最后一块
    if current_chunk.strip():
        chunks.append({
            "content": current_chunk.strip(),
            "source": doc["source"],
            "category": doc["category"]
        })
    
    return chunks


def vectorstore_save():
    """主函数：加载知识库并存入向量数据库"""
    
    # 1. 加载所有txt文件
    logger.info(f"正在从 {KNOWLEDGE_BASE_DIR} 加载知识库...")
    documents = load_txt_files(KNOWLEDGE_BASE_DIR)
    logger.info(f"共加载 {len(documents)} 个文件")
    
    if not documents:
        logger.error("未找到任何txt文件！")
        return
    
    # 2. 切分文档
    all_chunks = []
    for doc in documents:
        chunks = split_document(doc)
        all_chunks.extend(chunks)
    logger.info(f"切分后共 {len(all_chunks)} 个文档块")
    
    # 3. 初始化embedding
    logger.info("正在初始化Embedding模型...")
    embedding = get_embedding_function()
    
    # 4. 计算向量
    logger.info("正在计算向量...")
    texts = [chunk["content"] for chunk in all_chunks]
    metadatas = [{"source": chunk["source"], "category": chunk["category"]} for chunk in all_chunks]
    
    try:
        embeddings = embedding.embed_documents(texts)
        logger.info(f"向量计算完成，维度: {len(embeddings[0])}")
    except Exception as e:
        logger.error(f"向量计算失败: {e}")
        return
    
    # 5. 存入ChromaDB
    logger.info(f"正在存入ChromaDB: {CHROMADB_DIRECTORY}/{CHROMADB_COLLECTION_NAME}")
    
    chroma_client = chromadb.PersistentClient(path=CHROMADB_DIRECTORY)
    
    # 删除旧集合（如果存在）
    try:
        chroma_client.delete_collection(CHROMADB_COLLECTION_NAME)
        logger.info("已删除旧集合")
    except:
        pass
    
    # 创建新集合
    collection = chroma_client.create_collection(name=CHROMADB_COLLECTION_NAME)
    
    # 添加文档
    collection.add(
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
        ids=[str(uuid.uuid4()) for _ in range(len(texts))]
    )
    
    logger.info(f"✅ 知识库灌库完成！共 {len(texts)} 条记录")
    
    # 6. 测试检索
    logger.info("\n--- 测试检索 ---")
    test_queries = [
        "iPhone 17 Pro Max多少钱",
        "退货政策是什么",
        "什么时候发货"
    ]
    
    for query in test_queries:
        query_embedding = embedding.embed_query(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=2)
        logger.info(f"\n查询: {query}")
        for i, doc in enumerate(results['documents'][0]):
            logger.info(f"  结果{i+1}: {doc[:100]}...")


if __name__ == "__main__":
    vectorstore_save()
