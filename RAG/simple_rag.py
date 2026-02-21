import os
import glob
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import SystemMessage, HumanMessage, convert_to_messages
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings

import gradio as gr

MODEL = "stepfun/step-3.5-flash:free"
EMBEDDING_MODEL = "all-MiniLM-L6-V2"
DB_NAME = "RAG/vector_db"

load_dotenv(override=True)

#Create a document chunks using chroma
folders = glob.glob("RAG/knowledge-base/*")
documents = []
for folder in folders:
    doc_type = os.path.basename(folder)
    loader = DirectoryLoader(folder, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    folder_docs = loader.load()
    for doc in folder_docs:
        doc.metadata["doc_type"] = doc_type
        documents.append(doc)

print("[INFO] Number of documents in the knowledgebase: ", len(documents))

#Divide the documents into chunks which enables embedding for each chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)

print("[INFO] Number of documents chunks: ", len(chunks))
print("[INFO] First chunk: ", chunks[0])

embeddings = HuggingFaceEmbeddings(model_name = EMBEDDING_MODEL)
if os.path.exists(DB_NAME):
    Chroma(persist_directory=DB_NAME, embedding_function=embeddings).delete_collection()

vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=DB_NAME)
print(f"[INFO] Vector store created successfully with {vectorstore._collection.count()} documents")

retriever = vectorstore.as_retriever()
llm = ChatOpenAI(temperature=0, model_name=MODEL, base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

SYSTEM_PROMPT = """
You are a knowledgeable, friendly assistant representing the company Insurellm.
You are chatting with a user about Insurellm.
If relevant, use the given context to answer any question.
If you don't know the answer, say so.
Context:
{context}
"""

def collect_user_questions(question, history):
    context = ""
    for message in history:
        if message["role"] == "user":
            context += message["content"] + "\n"
    context += question + "\n"
    return context

def answer_question(question, history):
    context = collect_user_questions(question, history)
    docs = retriever.invoke(context)
    context = "\n\n".join(doc.page_content for doc in docs)
    system_prompt = SYSTEM_PROMPT.format(context=context)
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(convert_to_messages(history))
    messages.append(HumanMessage(content=question))
    response = llm.invoke(messages)
    return response.content

gr.ChatInterface(fn=answer_question, type="messages").launch()