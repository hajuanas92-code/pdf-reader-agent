from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from project.backend.langgraph_agent import graph_state
from dotenv import load_dotenv
from pydantic import BaseModel
from io import BytesIO
from project.backend.rag import add_pdf
from project.backend.database import create_table, insert_pdf, insert_chat
from project.backend.mcp_client import get_mcp_tools
from contextlib import asynccontextmanager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
  try:
    client = None
    tools,client = await get_mcp_tools()
    app.state.graph = graph_state(tools)

    yield 
     
  except Exception as e:
    raise e
  finally:
     
     try:
       if client is not None:
        await client.aclose()
     except RuntimeError:
        pass
   
app = FastAPI(lifespan=lifespan)

create_table()

@app.post('/upload_pdf')
async def pdf_uploading(file: UploadFile = File(...)):

    file_bytes = await file.read()
    stream = BytesIO(file_bytes)
    reader = PdfReader(stream)
    
    doc_list = []
    for txts in reader.pages:
      text = txts.extract_text() 
      if text.strip():
        docs = Document(page_content=text,
                      metadata={'source':file.filename})
        doc_list.append(docs)
 
    if doc_list:
      insert_pdf(file.filename,len(doc_list))
      add_pdf(doc_list,file.filename)
      print("saved both functions")
     

    return {"message":f'Your uploaded pdf had {len(doc_list)} pages and saved successfully',
            'filename':file.filename,
            'message2':'please use this file name in ask/ endpoint'}

class Query(BaseModel):
    query: str
    filename: str
    session_id: str = 'default_session'

@app.post('/ask')
async def user_query(query_data: Query):

    user_state = {
      'query' : query_data.query,
      'filename' : query_data.filename,
      'messages':[HumanMessage(content=query_data.query)]}
    session = query_data.session_id
    
    config = {'configurable':{'thread_id':session}}
    try:
      result = await app.state.graph.ainvoke(user_state,config)

      ai_answer = result['messages'][-1].content
      print("\n\n\nresult.get",result.get('answer'))

      insert_chat(result.get('query'),ai_answer)
      
      return {'query':result.get('query'),
              'answer':ai_answer,
              'session_id':session}
     
    except Exception as e:
       raise HTTPException(status_code=500,detail=str(e))