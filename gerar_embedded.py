from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings  
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

loaders = [PyPDFLoader('./report.pdf')]

docs = []

for arquivo in loaders:
    docs.extend(arquivo.load())
    
# separar todos os embedd pra poder ler melhor ne 
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap = 100)
docs = text_splitter.split_documents(docs)

embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})

# armazenar o vetor e criar  a base de dados.

vectorstore = Chroma.from_documents(
    docs,
    embedding = embedding_function,
    persist_directory="./chroma_db_nccn")

print(vectorstore._collection.count())