import os
import signal
import sys

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

KEY_GEMINI = os.getenv('key_gemini')



model_name = "gemini-2.0-flash-exp"


# adeus colega.
def signal_handler(sig, frame):
    print('\nObrigado por usar o QUATROIMIBICO')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# prompt que o gemini vai entender
def gerar_prompt_rag(query, context):
    escape = contexto.replace("'","''").replace('"', '""').replace("\n", " ")
    prompt = ("""You are a helpful and informative bot that answers questions using text in portuguese from brazil, and the reference context included below. \
  Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
  However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
  strike a friendly and converstional tone. \
  If the context is irrelevant to the answer, you may ignore it.
                QUESTION: '{query}'
                CONTEXT: '{context}'
              
              ANSWER:
              """).format(query=query, context=context)
    return prompt


def get_contexto_relevante_from_db(query):
    contexto = ""
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
    vector_db = Chroma(persist_directory="./chroma_db_nccn", embedding_function=embedding_function)
    resultados_busca = vector_db.similarity_search(query, k=6) # numeros de pesquisa dentro da semelhança com a pergunta.
    for resultado in resultados_busca:
        contexto += resultado.page_content + "\n"
    return contexto
        
        
# gerar resposta prestativa.
def gerar_resposta(prompt):
    genai.configure(api_key=KEY_GEMINI)
    model = genai.GenerativeModel(model_name)
    resposta = model.generate_content(prompt)
    return resposta.text 
# progamar o input pra pode fazer a pergunta
while True:
    print("--------------------------------------------------------------------")
    print("O que você deseja saber?")
    query = input("Query: ")
    contexto = get_contexto_relevante_from_db(query)
    prompt = gerar_prompt_rag(query=query, context=contexto)
    resposta = gerar_resposta(prompt=prompt)
    print(resposta)