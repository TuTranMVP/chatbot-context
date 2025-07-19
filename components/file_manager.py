"""
File Manager Component for Maya Chatbot
Handles file upload, storage, and management for AI processing
"""

import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st

from .vector_text_processor import VectorTextProcessor


class FileManager:
    """File manager for handling uploaded files"""
    
    def __init__(self, upload_dir: str = "uploaded_files"):
        self.upload_dir = upload_dir
        self.ensure_upload_directory()
        
        # Initialize vector processor for ChromaDB integration
        try:
            self.vector_processor = VectorTextProcessor(
                db_path="./vector_chroma_db",
                embedding_model="all-MiniLM-L6-v2",
                enable_caching=True
            )
            self.vector_processing_enabled = True
        except Exception as e:
            st.warning(f"Vector processing disabled: {str(e)}")
            self.vector_processor = None
            self.vector_processing_enabled = False
        
    def ensure_upload_directory(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
            
    def save_uploaded_file(self, uploaded_file) -> Dict:
        """Save uploaded file and return file info"""
        try:
            # Generate unique filename
            file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8]
            file_extension = os.path.splitext(uploaded_file.name)[1]
            unique_filename = f"{file_hash}_{uploaded_file.name}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Process and store file in ChromaDB using vector processor
            vector_chunk_ids = None
            vector_processing_success = False
            
            if self.vector_processing_enabled and self.vector_processor:
                try:
                    # Check if file type is supported by vector processor
                    if file_extension.lower() in ['.pdf', '.txt', '.md', '.markdown']:
                        vector_chunk_ids = self.vector_processor.process_and_store_file(
                            file_path=file_path,
                            use_chunking=True
                        )
                        vector_processing_success = vector_chunk_ids is not None
                        
                        if vector_processing_success:
                            st.success(f"✅ File processed and stored in vector database: {len(vector_chunk_ids)} chunks") # type: ignore
                        else:
                            st.warning("⚠️ File saved but vector processing failed")
                    else:
                        st.info(f"ℹ️ File type {file_extension} not supported for vector processing")
                        
                except Exception as e:
                    st.warning(f"⚠️ Vector processing failed: {str(e)}")
                    vector_processing_success = False
                
            # Create file info
            file_info = {
                "id": file_hash,
                "name": uploaded_file.name,
                "filename": unique_filename,
                "path": file_path,
                "size": uploaded_file.size,
                "type": uploaded_file.type,
                "extension": file_extension,
                "upload_time": datetime.now().isoformat(),
                "content_preview": self.get_file_preview(file_path, file_extension)
            }
            
            return file_info
            
        except Exception as e:
            st.error(f"Lỗi khi lưu file: {str(e)}")
            return None # type: ignore
            
    def get_file_preview(self, file_path: str, extension: str) -> str:
        """Get file content preview"""
        try:
            if extension.lower() in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return content[:500] + "..." if len(content) > 500 else content
            return "Preview not available for this file type"
        except Exception:
            return "Could not read file content"
            
    def read_file_content(self, file_path: str) -> str:
        """Read full file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
            
    def delete_file(self, file_info: Dict) -> bool:
        """Delete uploaded file and remove from vector database"""
        try:
            if os.path.exists(file_info["path"]):
                # Remove the physical file
                os.remove(file_info["path"])
                
                # Remove from vector database if vector processing is enabled
                if self.vector_processing_enabled:
                    try:
                        filename = file_info.get("name", os.path.basename(file_info["path"]))
                        removed_count = self.vector_processor.remove_by_filename(filename) # type: ignore
                        print(f"Removed {removed_count} chunks for file '{filename}' from vector database")
                    except Exception as e:
                        print(f"Warning: Failed to remove file from vector database: {str(e)}")
                        # Don't fail the deletion if vector removal fails
                
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False
            
    def search_files(self, query: str, files: List[Dict]) -> List[Dict]:
        """Search files by name or content"""
        if not query:
            return files
            
        query_lower = query.lower()
        filtered_files = []
        
        for file_info in files:
            # Search in filename
            if query_lower in file_info["name"].lower():
                filtered_files.append(file_info)
                continue
                
            # Search in content preview
            if query_lower in file_info.get("content_preview", "").lower():
                filtered_files.append(file_info)
                continue
                
        return filtered_files
    
    def save_uploaded_file_replace(self, uploaded_file, existing_file_info) -> Dict:
        """Save uploaded file replacing existing one using remove_and_add_file"""
        try:
            # Generate unique filename (reuse existing hash if possible)
            file_hash = existing_file_info.get("id", hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8])
            file_extension = os.path.splitext(uploaded_file.name)[1]
            unique_filename = f"{file_hash}_{uploaded_file.name}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Process and store file in ChromaDB using remove_and_add_file
            vector_chunk_ids = None
            vector_processing_success = False
            
            if self.vector_processing_enabled and self.vector_processor:
                try:
                    # Check if file type is supported by vector processor
                    if file_extension.lower() in ['.pdf', '.txt', '.md', '.markdown']:
                        # Use remove_and_add_file to replace existing vector entries
                        vector_chunk_ids = self.vector_processor.remove_and_add_file(
                            file_path=file_path,
                            use_chunking=True
                        )
                        vector_processing_success = vector_chunk_ids is not None
                        
                        if vector_processing_success:
                            st.success(f"✅ File replaced and updated in vector database: {len(vector_chunk_ids)} chunks") # type: ignore
                        else:
                            st.warning("⚠️ File replaced but vector processing failed")
                    else:
                        st.info(f"ℹ️ File type {file_extension} not supported for vector processing")
                        
                except Exception as e:
                    st.warning(f"⚠️ Vector processing failed during replacement: {str(e)}")
                    vector_processing_success = False
                
            # Create file info
            file_info = {
                "id": file_hash,
                "name": uploaded_file.name,
                "filename": unique_filename,
                "path": file_path,
                "size": uploaded_file.size,
                "type": uploaded_file.type,
                "extension": file_extension,
                "upload_time": datetime.now().isoformat(),
                "content_preview": self.get_file_preview(file_path, file_extension)
            }
            
            return file_info
            
        except Exception as e:
            st.error(f"Error replacing file: {str(e)}")
            return None # type: ignore
    
    # ...existing code...
def render_file_manager():
    """Render file manager UI"""
    st.markdown(
        """
        <div class="file-manager-container">
            <h3 style="color: #58cc02; margin-bottom: 1rem;">📁 File Manager</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize file manager
    if 'file_manager' not in st.session_state:
        st.session_state.file_manager = FileManager()
        
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    # File upload section
    with st.expander("📤 Upload Files", expanded=True):
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=['txt', 'md'],
            accept_multiple_files=True,
            help="Support .txt and .md files"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Check if file already exists
                existing_file = next(
                    (f for f in st.session_state.uploaded_files if f["name"] == uploaded_file.name),
                    None
                )
                
                if not existing_file:
                    file_info = st.session_state.file_manager.save_uploaded_file(uploaded_file)
                    if file_info:
                        st.session_state.uploaded_files.append(file_info)
                        st.success(f"✅ Uploaded: {uploaded_file.name}")
                else:
                    # File already exists - use remove_and_add_file to replace it
                    st.info(f"🔄 File already exists. Replacing: {uploaded_file.name}")
                    
                    # Remove the existing file from the list first
                    st.session_state.uploaded_files.remove(existing_file)
                    
                    # Delete the existing physical file
                    if os.path.exists(existing_file["path"]):
                        os.remove(existing_file["path"])
                    
                    # Save the new file with remove_and_add_file logic
                    file_info = st.session_state.file_manager.save_uploaded_file_replace(uploaded_file, existing_file)
                    if file_info:
                        st.session_state.uploaded_files.append(file_info)
                        st.success(f"✅ Replaced: {uploaded_file.name}")
    
    # Search and filter section
    if st.session_state.uploaded_files:
        st.markdown("### 🔍 Search & Filter")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "Search files by name or content",
                placeholder="Enter search terms...",
                key="file_search"
            )
        with col2:
            if st.button("🗑️ Clear All", type="secondary"):
                if st.session_state.uploaded_files:
                    # Delete all files
                    for file_info in st.session_state.uploaded_files:
                        st.session_state.file_manager.delete_file(file_info)
                    st.session_state.uploaded_files = []
                    st.success("All files cleared!")
                    st.rerun()
        
        # Filter files based on search
        filtered_files = st.session_state.file_manager.search_files(
            search_query, st.session_state.uploaded_files
        )
        
        # Display files
        if filtered_files:
            st.markdown(f"### 📋 Files ({len(filtered_files)} found)")
            
            for idx, file_info in enumerate(filtered_files):
                with st.expander(f"📄 {file_info['name']} ({file_info['size']} bytes)", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Type:** {file_info['extension']}")
                        st.write(f"**Uploaded:** {file_info['upload_time'][:19]}")
                        st.write(f"**ID:** {file_info['id']}")
                    
                    with col2:
                        if st.button("👁️ Preview", key=f"preview_{idx}"):
                            st.session_state[f"show_preview_{idx}"] = not st.session_state.get(f"show_preview_{idx}", False)
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{idx}", type="secondary"):
                            if st.session_state.file_manager.delete_file(file_info):
                                st.session_state.uploaded_files.remove(file_info)
                                st.success(f"Deleted: {file_info['name']}")
                                st.rerun()
                    
                    # Show preview if toggled
                    if st.session_state.get(f"show_preview_{idx}", False):
                        st.markdown("**Content Preview:**")
                        st.code(file_info['content_preview'], language="text")
                        
        else:
            if search_query:
                st.info("🔍 No files found matching your search.")
            else:
                st.info("📁 No files uploaded yet.")
    else:
        st.info("📁 No files uploaded yet. Upload some files to get started!")


def render_file_manager_css():
    """Render CSS for file manager"""
    st.markdown(
        """
        <style>
        .file-manager-container {
            padding: 1rem;
            border-radius: 12px;
            border: 2px solid #58cc02;
            margin: 1rem 0;
        }

        .file-item {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .file-item:hover {
            border-color: #58cc02;
            box-shadow: 0 2px 8px rgba(88, 204, 2, 0.1);
        }
        
        .file-stats {
            display: flex;
            gap: 1rem;
            margin: 0.5rem 0;
        }
        
        .file-stat {
            background: #f8f9fa;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.85rem;
            color: #666;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def get_file_content_for_ai(file_id: str) -> Optional[str]:
    """Get file content for AI processing"""
    if 'uploaded_files' not in st.session_state:
        return None
        
    file_info = next(
        (f for f in st.session_state.uploaded_files if f["id"] == file_id),
        None
    )
    
    if file_info and 'file_manager' in st.session_state:
        return st.session_state.file_manager.read_file_content(file_info['path'])
    
    return None
