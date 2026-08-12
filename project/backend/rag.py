from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import ParentDocumentRetriever, EnsembleRetriever
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_classic.retrievers.document_compressors import FlashrankRerank
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.storage import LocalFileStore
from langchain_classic.storage import create_kv_docstore  
from dotenv import load_dotenv
import sys, os

load_dotenv()

BASE_DIR = os.getcwd()
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")
DOCSTORE_DIR = os.path.join(BASE_DIR, "docstore_db")

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=4000,chunk_overlap=200)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=600,chunk_overlap=100)

fs = LocalFileStore(DOCSTORE_DIR)
bytes_store = create_kv_docstore(fs)
 # --- embeddings and storing ---
embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
vector_store = Chroma(
    embedding_function=embeddings,
    collection_name='first-collection',
    persist_directory=PERSIST_DIR
  )


 # --- parent document retrievel ---
parent_retrieval = ParentDocumentRetriever(
    vectorstore=vector_store,
    parent_splitter=parent_splitter,
    child_splitter=child_splitter,
    docstore=bytes_store
 )

bm25_registery = {}
def add_pdf(file_docs: list[Document],filename: str):

 parent_retrieval.add_documents(file_docs,ids=None)
 
 bm25 = BM25Retriever.from_documents(file_docs)
 bm25.k = 3
 bm25_registery[filename] = bm25
 print("Ingested and isolated for file: ",filename)
 print("\n\nBM25 REGISTERY: ",bm25_registery)

CACHED_COMPRESSOR = None
def get_compressor():
  global CACHED_COMPRESSOR
  if CACHED_COMPRESSOR is None:
    CACHED_COMPRESSOR = FlashrankRerank(model="ms-marco-TinyBERT-L-2-v2")
    print("Loding compressor for first time")

  return CACHED_COMPRESSOR

def search_pdf(query: str,filename: str) -> str:
 
 print(f"[TOOL EXECUTION] Triggered database search for file {filename} | Query {query}",file=sys.stderr)

 # --- hybrid retriever ---
 try:
   bm25 = bm25_registery.get(filename)
   print('\n\nBM25 CHECKING: ',bm25,file=sys.stderr)

   isolater_parent_retriever = parent_retrieval.vectorstore.as_retriever(search_kwargs={'filter':{'source':filename}})
   print('\n\n isolater_parent_retriever CHECKING: ',isolater_parent_retriever,file=sys.stderr)

   if bm25 is None:
    base_retriever = isolater_parent_retriever
    print(f"[FALLBACK WARNING] NO active context found for file {filename}",file=sys.stderr)
  
   else:
    base_retriever =  EnsembleRetriever(
     retrievers = [isolater_parent_retriever,bm25],
     weights = [0.7,0.3]
    )
    print(f"[ROUTE VERIFIED] Executing hybrid search for file {filename}",file=sys.stderr)
   
   final_retriever = ContextualCompressionRetriever(
    base_retriever = base_retriever,
    base_compressor = get_compressor()
 )

   result = final_retriever.invoke(query)
   for doc in result:
     print('FINAL RETRIEVER: ',doc.page_content[:500],file=sys.stderr)

   context = "\n\n".join(doc.page_content for doc in result)
   if not context.strip():
     return "No matching found"
   
   return str(context) 
   
 except Exception as e:
    
    return str(e)