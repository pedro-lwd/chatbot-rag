from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings  
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader
import os
import shutil
import json
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

caminho_arquivo = os.getenv("PASTA_UPLOAD")

arquivo_registro = os.getenv("ARQUIVO_REGISTRO")

persist_directory = os.getenv("PERSIST_DIRECTORY")

def carregar_registro():
    if os.path.exists(arquivo_registro):
        with open(arquivo_registro, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# salvar o registro dos arquivos processados
def salvar_registro(registro):
    with open(arquivo_registro, 'w') as f:
        json.dump(registro, f, indent=2)
        



# receber os arquivos que foram jogados pelo upload e jogar para o loader
def processar_arquivos(caminho_arquivo, persist_directory=persist_directory):
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Caminho do arquivo não encontrado: {caminho_arquivo}.")
    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    print(f"Processando arquivo: {caminho_arquivo}.")
    
    # se for pdf usar ...
    if extensao == '.pdf':
        loader = PyPDFLoader(caminho_arquivo)
        print(f"Arquivo {extensao} carregado no loader")
    # se for powerpoint ...
    elif extensao in ['.ppt', '.pptx']:
        loader = UnstructuredPowerPointLoader(caminho_arquivo)
        print(f"Arquivo {extensao} carregado no loader")

    else:
        raise ValueError(f"Tipo de arquivo não suportado: {extensao}. Apenas arquivos PDF, ppt, pptx irmão.")
    
    
    docs = loader.load()

# separar todos os embedd pra poder ler melhor ne 
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap = 100)
    chunks = text_splitter.split_documents(docs)
    print(f"Documento dividido em {len(chunks)} chunks")

    embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    
    )

# criar o vectorstore, que é uma estrutura de dados que vai armazenar as informações dos documentos

    vectorstore = Chroma.from_documents(
        docs,
        embedding = embedding_function,
        persist_directory=persist_directory)
    

    count = vectorstore._collection.count()
    print(f"Armazenamento de vetores criado com um total de {count} embeddings.")
    
    return vectorstore, count

# (NOVO) Função pra processar apenas os arquivos novos em um diretório.
def processar_arquivos_novos(diretorio, persist_directory=persist_directory):
    if not os.path.exists(diretorio):
        raise FileNotFoundError(f"Diretório não encontrado: {diretorio}")
    
    if not os.path.isdir(diretorio):
        raise NotADirectoryError(F"{diretorio} não é um diretório")
    
    registro = carregar_registro()
    
    arquivos_novos = 0
    total_chunks = 0
    ultimo_vectorstore = None
    
    # processar cada arquivo no diretório
    for nome_arquivo in os.listdir(diretorio):
        caminho_completo = os.path.join(diretorio, nome_arquivo)
        
        if not os.path.isfile(caminho_completo):
            continue
        
        # verificar extensão
        extensao = os.path.splitext(nome_arquivo)[1]
        if extensao not in ['.pdf', '.ppt', '.pptx']:
            continue
        
        info_arquivo = os.stat(caminho_arquivo)
        ultima_modificacao = info_arquivo.st_mtime
        tamanho_arquivo = info_arquivo.st_size
        
        arquivo_id = f"{nome_arquivo}_{tamanho_arquivo}"
        
        if arquivo_id in registro and registro[arquivo_id]['modificado'] >= ultima_modificacao:
            print(f"Arquivo '{nome_arquivo} ja foi processado e não foi modificado. Pulando ele.")
            continue
        
        print(f"Processando novo arquivo: {nome_arquivo}")
        try:
            vectorstore, num_chunks = processar_arquivos(caminho_completo, persist_directory)
            
            # atualizar o nosso registro
            registro[arquivo_id] = {
                'caminho': caminho_completo,
                'modificado': ultima_modificacao,
                'tamanho': tamanho_arquivo, 
                'processado_em': datetime.now().isoformat(), 
                'chunks': num_chunks
            }
            
            arquivos_novos += 1
            total_chunks += num_chunks
            ultimo_vectorstore = vectorstore
            
        except Exception as e:
            print(f"Errro ao processar arquivo {nome_arquivo}: {e}")
    salvar_registro(registro)
    
    print(f"\nProcessamento concluído. {arquivos_novos} novos arquivos foram processados, gerando {total_chunks} novos chunks.")
    return ultimo_vectorstore, total_chunks
            
def limpar_e_recriar_embedding(diretorio, persist_directory=persist_directory):
    # limpar o diretorio de persistencia
    if os.path.exists(persist_directory):
        print(f"Limpando diretório de embeddings")
        shutil.rmtree(persist_directory)
        os.makedirs(persist_directory, exist_ok=True)
        
    if os.path.exists(arquivo_registro):
        os.remove(arquivo_registro)
        print("arquivos de registro processados foram removidos.")
    
    print("Recriando embeddings para todos os arquivos...")
    return processar_arquivos_novos(diretorio, persist_directory)
    
if __name__ == "__main__":    
    if not caminho_arquivo:
        print("Erro: Váriavel do ambiente não está definida no arquivo")
        exit(1)
        
    print(f"Usando caminho do arquivo: {caminho_arquivo}")
    
    # menu
    print("\nEscolha uma opção")
    print("1. Processar apenas arquivos novos")
    print("2. Limpar e recriar todos os embeddings")
    print("3. Ler todos os embeddings novamente")
    print("4. Sair.")
    
    opcao = input("Digite a opção (1-4): ")
    try:
        if opcao == "1":
            vectorstore, num_chunks = processar_arquivos_novos(caminho_arquivo)
            print(f"Processamento de novos arquivos concluído com sucesso.")
        elif opcao == "2":
            vectorstore, num_chunks = limpar_e_recriar_embedding(caminho_arquivo)
            print(f"Todos os embeddings foram limpos e recriados com sucesso.")
        
        elif opcao == "3":
            vectorstore, num_chunks = processar_arquivos(caminho_arquivo)
            print(f"Todos os arquivos foram processados novamente.")
        
        elif opcao == "4":
            print(f"Adeus, mundo :(")
            exit
        
        else:
            print("Responde direito cara")
            
    except Exception as e:
        print(f"Erro durante o processamento: {e}")    