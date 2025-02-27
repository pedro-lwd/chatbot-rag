from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings  
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader
import os
from dotenv import load_dotenv

load_dotenv()
caminho_arquivo = os.getenv("PASTA_UPLOAD")


# receber os arquivos que foram jogados pelo upload e jogar para o loader
def processar_arquivos(caminho_arquivo, persist_directory="./chroma_db_nccn"):
    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    
    # se for pdf usar ...
    if extensao == '.pdf':
        loader = PyPDFLoader(caminho_arquivo)
        print(f"Arquivo {extensao} carregado no loader")
    # se for powerpoint ...
    elif extensao in ['.ppt', '.pptx']:
        loader = UnstructuredPowerPointLoader(caminho_arquivo)
        print(f"Arquivo {extensao} carregado no loader")

    else:
        raise ValueError(f"Tipo de arquivo não suportado: {extensao}")
    
    
    docs = loader.load()

# separar todos os embedd pra poder ler melhor ne 
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap = 100)
    chunks = text_splitter.split_documents(docs)
    # print(f"Informações splitadas em {chunks}.")

    embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    
    )

# criar o vectorstore, que é uma estrutura de dados que vai armazenar as informações dos documentos

    vectorstore = Chroma.from_documents(
        docs,
        embedding = embedding_function,
        persist_directory="./chroma_db_nccn")
    

    count = vectorstore.collection.count()
    print(f"Armazenamento de vetores criado com um total de {count} embeddings.")
    
    return vectorstore, count

if __name__ == "__main__":
    arquivos = [os.path.join(caminho_arquivo, f) for f in os.listdir(caminho_arquivo) if os.path.isfile(os.path.join(caminho_arquivo, f))]

    if not arquivos:
        raise ValueError("Nenhum arquivo encontrado na pasta especificada.")

    for arquivo in arquivos:
        vectorstore, num_chunks = processar_arquivos(arquivo)
        print(f"Processamento concluído: {num_chunks} chunks foram criados para {arquivo}.")