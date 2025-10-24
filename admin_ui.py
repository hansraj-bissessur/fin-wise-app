import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- Configuration ---
st.set_page_config(layout="wide", page_title="FinLit Admin")
BACKEND_URL = "http://localhost:8000"  # URL of your FastAPI backend

# --- Initialize Session State ---
# This is used to store the list of uploaded documents, just like the React state
if "documents" not in st.session_state:
    st.session_state.documents = []

# --- Helper Functions ---

def format_file_size(bytes_size):
    if bytes_size == 0: return '0 Bytes'
    k = 1024
    sizes = ['Bytes', 'KB', 'MB']
    i = min(len(sizes) - 1, int(bytes_size.bit_length() / 10))
    return f"{bytes_size / (k**i):.2f} {sizes[i]}"

# --- Main Page UI ---

st.title("Financial Literacy Chatbot - Admin Portal")
st.caption("Manage the document knowledge base for the RAG chatbot.")

# --- Tabs (replaces the React component routing) ---
tab_upload, tab_documents, tab_admin = st.tabs([
    "📄 Document Upload", 
    "🗂️ Document History", 
    "⚙️ Admin Panel"
])

# --- Tab 1: Document Upload (replaces DocumentUpload.js) ---
with tab_upload:
    st.subheader("Upload New Documents")
    
    with st.form("upload_form", clear_on_submit=True):
        # Replicates the User ID input
        user_id = st.text_input("User ID", "admin123", help="An ID to associate with this upload batch.")
        
        # Replaces the FileDropzone component
        uploaded_files = st.file_uploader(
            "Select files to upload (PDF, DOCX, XLSX)",
            accept_multiple_files=True,
            type=["pdf", "docx", "doc", "xlsx", "xls"]
        )
        
        submitted = st.form_submit_button("Upload Files")

    if submitted and uploaded_files:
        if not user_id.strip():
            st.error("Please enter a valid User ID.")
        else:
            # Replicates the progress bar and status
            progress_bar = st.progress(0, text="Starting upload...")
            
            # Prepare files for multipart/form-data request
            files_to_send = [
                ("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files
            ]
            data = {"user_id": user_id}

            try:
                progress_bar.progress(30, text="Sending files to backend...")
                
                # Replicates the documentService.js API call
                response = requests.post(
                    f"{BACKEND_URL}/api/v1/chatbot/documents/upload-multiple",
                    files=files_to_send,
                    data=data,
                    timeout=300 # 5 minute timeout for large uploads
                )

                progress_bar.progress(70, text="Backend processing...")
                
                if response.status_code == 200:
                    res_data = response.json()
                    st.success(res_data.get("message", "Upload successful!"))
                    
                    # Add successfully uploaded files to our session state list
                    # This replicates the behavior of the React app
                    new_docs = []
                    for f in uploaded_files:
                        new_docs.append({
                            "File Name": f.name,
                            "Size": format_file_size(f.size),
                            "Upload Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Status": "Success",
                            "Chunks": res_data.get("total_chunks_created", "N/A") / len(uploaded_files) # Approximate
                        })
                    
                    # Prepend new documents to the list
                    st.session_state.documents = new_docs + st.session_state.documents
                    
                    progress_bar.progress(100, text="Upload complete!")
                    
                else:
                    st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
                    progress_bar.progress(100, text="Upload failed.")

            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")
                progress_bar.progress(100, text="Connection error.")

    elif submitted and not uploaded_files:
        st.warning("Please select at least one file to upload.")

# --- Tab 2: Document History (replaces DocumentList.js) ---
with tab_documents:
    st.subheader("Uploaded Document History")
    
    if not st.session_state.documents:
        st.info("No documents have been uploaded in this session.")
    else:
        # Replicates the DocumentList table with Pandas DataFrame
        df = pd.DataFrame(st.session_state.documents)
        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "Chunks": st.column_config.NumberColumn(format="%.0f")
            }
        )

# --- Tab 3: Admin Panel (replaces AdminPanel.js) ---
with tab_admin:
    st.subheader("System Health Check")
    
    if st.button("Run Health Check"):
        try:
            # Replicates the checkHealth API call
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                st.success("Backend service is healthy!")
                st.json(response.json())
            else:
                st.error(f"Health check failed. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Health check failed: Unable to connect to backend. {e}")

    st.divider()
    
    st.subheader("Danger Zone")
    st.warning("This action is permanent and will delete all documents from the knowledge base.")
    
    # Replicates the clearAllDocuments API call
    admin_key = st.text_input(
        "Enter Admin Key to clear database", 
        type="password",
        help="Matches the 'admin123' key from your Java code."
    )
    
    if st.button("Clear All Documents", type="primary", disabled=(not admin_key)):
        with st.spinner("Attempting to clear all documents..."):
            try:
                params = {"admin_key": admin_key}
                response = requests.delete(
                    f"{BACKEND_URL}/api/v1/chatbot/documents/clear-all",
                    params=params,
                    timeout=60
                )
                
                if response.status_code == 200:
                    st.success(response.json().get("message", "Database cleared successfully!"))
                    # Clear the local session state as well
                    st.session_state.documents = []
                elif response.status_code == 403:
                    st.error("Unauthorized: Incorrect admin key.")
                else:
                    st.error(f"Failed to clear database: {response.json().get('detail', 'Unknown error')}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")
