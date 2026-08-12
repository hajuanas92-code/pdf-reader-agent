import streamlit as st
import requests, os
from project.backend.database import show_files, get_chat_history

#    ---- setting url for fastapi endpoints ----
if "CODESPACE_NAME" in os.environ:
   codespace_name = os.environ.get('CODESPACE_NAME')

   BASE_URL = f"https://{codespace_name}-8000.app.github.dev"

elif "BACKEND_URL" in os.environ:
   BASE_URL = os.environ.get('BACKEND_URL')
   
else:
   BASE_URL = "http://backend:8000"

ask_url = f"{BASE_URL}/ask"
upload_url = f"{BASE_URL}/upload_pdf"

#   ---- streamlit -----
st.title("PDf Chatbot")
st.caption("Powered by powerfull advanced RAG.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
if "current_file" not in st.session_state:
    st.session_state.current_file = None

# ---  PDF Uploading ---
with st.sidebar:

    st.title("📗 Upload your pdf here")

    upload_file = st.file_uploader("upload pdf",type='pdf') 

    if upload_file is None:
       st.session_state.uploaded = False
       st.session_state.current_file = False

       st.write("Please Upload a PDF")

    if upload_file is not None and not st.session_state.uploaded:

      with st.spinner("processing PDF..."):
          try:

            files = {'file':(upload_file.name,upload_file.getvalue(),'application/pdf')} 
                     
            pdf_response = requests.post(upload_url,files=files)
            if pdf_response.status_code == 200:
                st.session_state.uploaded = True
                st.session_state.current_file = upload_file.name
                st.success("PDF uploaded successfully.")

          except Exception as e:
            st.error(f"Error {e}")
            
      if upload_file is None and st.session_state.uploaded:
         pass
    #  ----- showing pdf data  ------
      if st.session_state.current_file:
        st.sidebar.info(f"Active file : **{st.session_state.current_file}**")
        st.info("📁 PDF DATA.")
        st.dataframe(show_files())
          

# --- input section ---
for msg in st.session_state.messages:
    label = "YOU" if msg['role'] == 'user' else "AI"
    st.markdown(f"**{label}** {msg['content']}")

if st.session_state.current_file:
  st.divider()
  if query := st.text_input('Ask your questions.'):

    st.session_state.messages.append({'role':'user','content':query})
    with st.spinner("Answering your question..."):
        try:
            payload = {'query':query,
                       'filename':st.session_state.current_file}
            
            response = requests.post(ask_url,json=payload)
            if response.status_code == 200:

                data = response.json()
                answer = data.get('answer')
                st.write(f"✨{answer}")

                st.session_state.messages.append({"role":'assistant','content':answer})
            else:
                st.info(f"error {response.status_code}")

            with st.expander("Chat History"):
               st.dataframe(get_chat_history())
        except Exception as e:
            st.error(f"Error {e}")
else:
   st.info("📄 Please upload a PDF first in the sidebar")

