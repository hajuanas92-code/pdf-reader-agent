from langchain_mcp_adapters.client import MultiServerMCPClient
import os

async def get_mcp_tools():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(dir_path,'mcp_server.py')
    print(dir_path,server_path)
    server = {
        'mcp_conn':{
          'command':'python',
          'args':[server_path],
          'transport':'stdio'
        }
    }
    client = MultiServerMCPClient(server) 
    print("Connected to server.")
    
    mcp_tools = await client.get_tools()
    print("\n\nMCP TOOLS: ",mcp_tools )
    return mcp_tools, client