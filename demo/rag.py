from typing import List
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel
import dashscope
from dashscope import Generation, TextEmbedding, rerank
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DASHSCOPE_API_KEY = "sk-ws-H.PDMHRXM.gn7P.MEUCICkp69SIzEw8QK6jBmgwhznhLcFBvIol2jzjiU6Bc-G9AiEAiLoHmWsOHXD1xjS3ycecisCdNJYx4wAXdWU0khZmwqg"
dashscope.api_key = DASHSCOPE_API_KEY
# RAG: Retrieval Augmented Generation, 检索增强生成
# indexing 文档预处理： pdf/word解析，文本切片，embedding向量化， BGE模型
# retrieval 检索：向量数据库chroma/milvus, chroma只适合测试，生产环境建议使用milvus；混合检索dense+bm25, reranking: 重排序
# generation 生成：大模型生成回答, 引用溯源/幻觉检测
# 框架选型： Llamaindex, dify/coze 低代码mvp
# 评估： RAGAs框架
# 知识库问答系统： pdf切片-向量化存chroma-检索,用户提问时先搜相似快-把快+问题给大模型
# 阶段1： pdf/文档 -> 切分 -> Embedding转向量 -> 写入向量库chroma
# 阶段2： 用户提问 -> Embedding转向量 -> chroma检索相似文档 -> 检索相似文档 -> 合并相似文档 -> 片段+问题 给大模型 -> 生成回答 -> 反馈评估

PDF_PATH = "./data/资产数据申请场景分析.pdf"
# 向量库持久化目录
CHROMA_DIR = "./chroma_db_local"


class AliEmbedding(Embeddings, BaseModel):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        resp = TextEmbedding.call(
            model=TextEmbedding.Models.text_embedding_v2,
            input=texts
        )
        if resp.status_code != 200:
            raise Exception(f"embedding接口异常 {resp.message}")
        return [item["embedding"] for item in resp.output["embeddings"]]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

def load_pdf_text(pdf_file_path: str) -> str:
    reader = PdfReader(pdf_file_path)
    # full_text = "\n".join([page.page_content for page in reader.pages])
    # return full_text
    full_textt=""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text.strip():
            full_textt += page_text + "\n"
    return full_textt
            
def build_knowledge_base(pdf_file_path: str) -> None:
    # 加载pdf-切片-写入向量库
    embedding = AliEmbedding()
    full_text = load_pdf_text(pdf_file_path)
    # 切割文本 优先按照换行，句号，逗号分隔
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n", "。", "，", " "]
    )
    chunks = text_splitter.split_text(full_text)
    print(f"切片完成，文本数量：{len(chunks)}")
    # 写入chroma向量库
    vector_db = Chroma.from_texts(
        chunks,
        embedding,
        persist_directory="./chroma_db_local"
    )
    print(f"向量库写入完成，文本数量：{len(chunks)}")
    return vector_db

def load_exist_knowledge_base() -> Chroma:
    embedding = AliEmbedding()
    vector_db = Chroma(
        embedding_function=embedding,
        persist_directory=CHROMA_DIR
    )
    return vector_db


# embedding = AliEmbedding()

# raw_docs = [
#     "RAG全称检索增强生成，解决大模型幻觉问题",
#     "RAG分为知识库构建阶段和在线问答阶段",
#     "向量数据库用来存储文本embedding向量，做语义检索",
#     "微调是修改模型权重，RAG不改动大模型本身参数"
# ]

# vector_db = Chroma.from_texts(
#     raw_docs,
#     embedding,
#     persist_directory="./chroma_db_local"
# )
# retriever = vector_db.as_retriever(search_kwargs={"k": 2})


def llm_call(prompt: str) -> str:
    resp = Generation.call(
        model=Generation.Models.qwen_turbo,
        messages=[{"role": "user", "content": prompt}],
        result_format="message"
    )
    if resp.status_code == 200:
        return resp.output.choices[0].message.content
    else:
        return f"调用大模型失败：{resp.message}"


def rag_query(vector_db,user_question):
    retriever = vector_db.as_retriever(search_kwargs={"k": 6})
    docs = retriever.invoke(user_question)
    # context = "\n".join([d.page_content for d in docs])
    if len(docs) == 0:
        return "没有相关资料"
    doc_texts = [d.page_content for d in docs]
    resp = dashscope.TextReRank.call(
        model="qwen3-rerank",
        query=user_question,
        documents=doc_texts,
        top_n=3
    )
    if resp.status_code != 200:
        selected_docs = docs[:3]
    else:
        selected_docs = [docs[item["index"]] for item in resp.output["results"]]
        print("===Reranker打分===")
        for item in resp.output["results"]:
            doc = docs[item["index"]]
            page = doc.metadata.get("page")
            print(f"score:{item['relevance_score']:.3f} page:{page} {doc.page_content[:80]}...")

    context_blocks = []
    for d in selected_docs:
        page_no = d.metadata.get("page")
        context_blocks.append(f"【来源页码：{page_no}】\n{d.page_content}")
    context = "\n\n".join(context_blocks)

    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""
参考下面资料回答问题，如果资料中没有答案，请直接回答不知道，禁止编造信息。
参考资料：
{context}

用户问题：{question}
回答：
"""
    )
    final_prompt = prompt_template.format(context=context, question=user_question)
    answer = llm_call(final_prompt)
    return answer


if __name__ == "__main__":
    db = load_exist_knowledge_base()
    print('知识库已加载，输入问题开始问答')
    # ==========后续直接加载已有向量库，不再解析PDF==========
    # db = load_exist_knowledge_base()
    while True:
        question = input("请输入问题：")
        if question.lower() == 'exit':
            break
        res = rag_query(db, question)
        print("=====RAG回答=====")
        print(res)
        

