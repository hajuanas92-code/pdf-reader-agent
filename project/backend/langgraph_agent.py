from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage

load_dotenv()

llm = ChatGroq(model='llama-3.1-8b-instant')

class Graph(TypedDict):
    messages: Annotated[list, add_messages]
    filename: str
    query: str
    
def graph_state(tools):

  llm_tools = llm.bind_tools(tools)
  
  def agent(state: Graph):

    current_file = state.get('filename','')
    user_query = state.get('query','')
    print(f"\n\nCURRENT FILE {current_file} \n QUERY {user_query}")

    sys_msg = f"""You are a helpful assistant. The user has uploaded a file named {current_file}.
    Answer the user's question from the given pdf."""
  
    msg = [SystemMessage(content=sys_msg)] + state['messages'] 
    llm_response = llm_tools.invoke(msg)

    print(f"\n\n LLM TOOL RESPONSE {llm_response}")
    print(f"\n\nSTATE MESSAGES {state['messages']}")
    
    return {'messages':[llm_response],
            'answer':llm_response.content}

  build = StateGraph(Graph)
  build.add_node('agent',agent)
  build.add_node('tools',ToolNode(tools))

  build.add_edge(START,'agent')
  build.add_conditional_edges(
      'agent',
      tools_condition,
      {
        'tools':'tools',
        "__end__":END
      }
      )
    
  build.add_edge('tools','agent')

  memory = MemorySaver()
  graph = build.compile(checkpointer=memory) 
  return graph