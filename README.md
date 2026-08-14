#  📁 PDF Chatbot with Advanced RAG and AI Agent

This project is a smart **PDF Chatbot** web application Streamlit. 
It lets you upload text base PDF file, save the data securely, and ask questions about the text inside. The system uses an AI Agent that can search your PDF using advanced search tools.

#  🚀 How It Works 
1. **Upload**: You put a PDF into the app via the sidebar *Streamlit*.
2. **Save**: The backend server *FastAPI* reads the PDF pages, saves text data into a local database SQLite, and cuts the text into smart pieces.
3. **Ask**: When you type a question, an **AI Agent** powered by *LangGraph* decides to use a special search tool.
4. **Search**: The search tool (built using Model Context Protocol / MCP) looks at your specific PDF using both normal keyword search and smart AI search, then cleans up the best answers to send back to the AI.

# 🛠️ The Tech Stack
- **Frontend**: Streamlit for a simple chat screen.
- **Backend API**: FastAPI to handle uploads and questions.
- **AI Brain**: LangGraph and Groq for the smart agent.
- **Search & Rerank**: Chroma, BM25, and Flashrank to find and rank the best text from your PDF.
- **Tool Protocol**: FastMCP to keep the search tool separate and clean.
- **Database**: SQLite to keep chat history and file lists.
  
# 💻 How to Run This Project Locally
If you want to run this app on your own computer, follow these simple steps:
1. **Clone the code** from this GitHub repository.
2. **Add your API keys**: Create a .env file in your root folder and add your Groq key:
```text
GROQ_API_KEY=your_actual_api_key_here
```
4. **Run with Docker**: Make sure Docker is installed, open your terminal, and type:
```bash
docker compose up --build
```
6. **Open the app**: Go to `http://localhost:8501` in your web browser

> **Note** : Upload a text-based PDF. This project does not support scanned based PDFs.>
