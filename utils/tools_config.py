from langchain_chroma import Chroma
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.tools import tool
from .config import Config



def get_tools(llm_embedding):
    """
    创建并返回工具列表。

    Args:
        llm_embedding: 嵌入模型实例，用于初始化向量存储。

    Returns:
        list: 工具列表。
    """
    # 创建Chroma向量存储实例
    vectorstore = Chroma(
        persist_directory=Config.CHROMADB_DIRECTORY,
        collection_name=Config.CHROMADB_COLLECTION_NAME,
        embedding_function=llm_embedding,
    )
    # 将向量存储转换为检索器
    retriever = vectorstore.as_retriever()
    # 创建iPhone 17知识库检索工具
    retriever_tool = create_retriever_tool(
        retriever,
        name="retrieve_iphone17",
        description="""iPhone 17电商知识库查询工具。
        搜索以下信息：产品参数、价格、配置、售后政策、退换货、维修保修、送货配送、选购建议。
        当用户询问iPhone 17相关问题时使用此工具。"""
    )

    # 返回工具列表
    return [retriever_tool]
