"""
Enhanced Streamlit UI for Text Import and Search
Phiên bản cải tiến với nhiều tính năng mới
"""
 
import streamlit as st
import os
import tempfile
import time
from typing import List, Dict, Any
import json
from vector_text_processor import VectorTextProcessor
 
# Cấu hình trang
st.set_page_config(
    page_title="🔍 Text Search Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# CSS cho UI đẹp hơn
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .search-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
    }
    .result-item {
        background: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stats-box {
        background: #e3f2fd;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)
 
def init_session_state():
    """Khởi tạo session state"""
    if 'processor' not in st.session_state:
        st.session_state.processor = None
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
 
def create_processor():
    """Tạo VectorTextProcessor instance"""
    if st.session_state.processor is None:
        with st.spinner("🤖 Đang khởi tạo Text Processor..."):
            try:
                st.session_state.processor = VectorTextProcessor()
                st.success("✅ Text Processor đã sẵn sàng!")
                return True
            except Exception as e:
                st.error(f"❌ Lỗi khởi tạo: {str(e)}")
                return False
    return True
 
def display_stats():
    """Hiển thị thống kê"""
    if st.session_state.processor:
        try:
            collection = st.session_state.processor.collection
            doc_count = collection.count()
           
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 Tài liệu", doc_count)
            with col2:
                st.metric("🔍 Tìm kiếm", len(st.session_state.search_history))
            with col3:
                st.metric("📁 File tải lên", len(st.session_state.uploaded_files))
        except:
            st.info("📊 Chưa có dữ liệu thống kê")
 
def process_uploaded_files(uploaded_files):
    """Xử lý files được upload"""
    if not uploaded_files:
        return
   
    progress_bar = st.progress(0)
    status_text = st.empty()
   
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"📂 Đang xử lý: {uploaded_file.name}")
       
        # Lưu file tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_file_path = tmp_file.name
       
        try:
            # Xử lý file và lưu vào database
            result = st.session_state.processor.process_and_store_file(tmp_file_path)
            if result:
                st.session_state.uploaded_files.append({
                    'name': uploaded_file.name,
                    'size': uploaded_file.size,
                    'time': time.strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success(f"✅ Đã xử lý: {uploaded_file.name}")
            else:
                st.error(f"❌ Lỗi xử lý: {uploaded_file.name}")
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")
        finally:
            # Xóa file tạm
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
       
        progress_bar.progress((i + 1) / len(uploaded_files))
   
    status_text.text("✅ Hoàn thành xử lý tất cả files!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()
 
def perform_search(query: str, top_k: int = 5):
    """Thực hiện tìm kiếm"""
    if not query.strip():
        st.warning("⚠️ Vui lòng nhập từ khóa tìm kiếm")
        return
   
    with st.spinner("🔍 Đang tìm kiếm..."):
        try:
            results = st.session_state.processor.search(query, top_k=top_k)
           
            # Lưu lịch sử tìm kiếm
            st.session_state.search_history.append({
                'query': query,
                'results_count': len(results),
                'time': time.strftime("%Y-%m-%d %H:%M:%S")
            })
           
            return results
        except Exception as e:
            st.error(f"❌ Lỗi tìm kiếm: {str(e)}")
            return []
 
def display_search_results(results: List[Dict[str, Any]]):
    """Hiển thị kết quả tìm kiếm"""
    if not results:
        st.info("🔍 Không tìm thấy kết quả phù hợp")
        return
   
    st.markdown(f"### 📋 Tìm thấy {len(results)} kết quả:")
   
    for i, result in enumerate(results):
        with st.container():
            st.markdown(f"""
            <div class="result-item">
                <h4>📄 {result.get('source', 'Unknown')}</h4>
                <div class="stats-box">
                    <strong>Độ phù hợp:</strong> {result.get('distance', 0):.3f} |
                    <strong>Chunk:</strong> {result.get('chunk_id', 'N/A')}
                </div>
                <p>{result.get('content', '')[:500]}{'...' if len(result.get('content', '')) > 500 else ''}</p>
            </div>
            """, unsafe_allow_html=True)
 
def main():
    """Main function"""
    init_session_state()
   
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Advanced Text Search Engine</h1>
        <p>Upload, process, and search through your documents with AI-powered vector embeddings</p>
    </div>
    """, unsafe_allow_html=True)
   
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Control Panel")
       
        # Khởi tạo processor
        if st.button("🚀 Initialize System", type="primary"):
            create_processor()
       
        st.divider()
       
        # Thống kê
        st.subheader("📊 Statistics")
        display_stats()
       
        st.divider()
       
        # Lịch sử tìm kiếm
        if st.session_state.search_history:
            st.subheader("📝 Search History")
            for item in st.session_state.search_history[-5:]:  # 5 tìm kiếm gần nhất
                st.text(f"🔍 {item['query'][:30]}...")
                st.caption(f"📅 {item['time']} | 📄 {item['results_count']} results")
       
        st.divider()
       
        # Settings
        st.subheader("⚙️ Settings")
        search_limit = st.slider("Max Results", 1, 20, 5)
       
        if st.button("🗑️ Clear History"):
            st.session_state.search_history = []
            st.success("✅ History cleared!")
   
    # Main content
    tab1, tab2, tab3 = st.tabs(["📤 Upload Files", "🔍 Search", "📊 Database Info"])
   
    with tab1:
        st.header("📤 Upload & Process Documents")
       
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=['txt', 'md', 'pdf'],
            accept_multiple_files=True,
            help="Supported formats: TXT, MD, PDF"
        )
       
        col1, col2 = st.columns([3, 1])
       
        with col1:
            if uploaded_files:
                st.info(f"📁 Selected {len(uploaded_files)} file(s)")
                for file in uploaded_files:
                    st.text(f"📄 {file.name} ({file.size:,} bytes)")
       
        with col2:
            if uploaded_files and st.button("🚀 Process Files", type="primary"):
                if create_processor():
                    process_uploaded_files(uploaded_files)
       
        # Uploaded files history
        if st.session_state.uploaded_files:
            st.subheader("📚 Processed Files")
            for file_info in st.session_state.uploaded_files[-10:]:  # 10 files gần nhất
                st.text(f"📄 {file_info['name']} - {file_info['time']}")
   
    with tab2:
        st.header("🔍 Search Documents")
       
        if not st.session_state.processor:
            st.warning("⚠️ Please initialize the system first (use sidebar)")
            return
       
        # Search interface
        col1, col2 = st.columns([4, 1])
       
        with col1:
            search_query = st.text_input(
                "Enter your search query:",
                placeholder="e.g., 'machine learning algorithms'",
                key="search_input"
            )
       
        with col2:
            search_button = st.button("🔍 Search", type="primary")
       
        # Advanced search options
        with st.expander("🔧 Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                top_k = st.number_input("Number of results", 1, 20, search_limit)
            with col2:
                search_mode = st.selectbox("Search mode", ["Semantic", "Keyword", "Hybrid"])
       
        # Perform search
        if search_button or (search_query and st.session_state.get('auto_search', False)):
            results = perform_search(search_query, top_k)
            if results:
                display_search_results(results)
       
        # Quick search examples
        st.subheader("💡 Quick Search Examples")
        example_queries = [
            "machine learning",
            "data analysis",
            "python programming",
            "artificial intelligence",
            "database design"
        ]
       
        cols = st.columns(len(example_queries))
        for i, query in enumerate(example_queries):
            def set_query(q=query):
                st.session_state.search_input = q
                st.rerun()
            with cols[i]:
                st.button(f"🔍 {query}", key=f"example_{i}", on_click=set_query)
   
    with tab3:
        st.header("📊 Database Information")
       
        if not st.session_state.processor:
            st.warning("⚠️ Please initialize the system first")
            return
       
        try:
            collection = st.session_state.processor.collection
            doc_count = collection.count()
           
            col1, col2 = st.columns(2)
           
            with col1:
                st.metric("📄 Total Documents", doc_count)
                st.metric("🗂️ Collection Name", collection.name)
           
            with col2:
                st.info(f"💾 Database Path: {st.session_state.processor.db_path}")
                if st.session_state.processor.embedding_model:
                    st.success("🤖 ML Embeddings: Active")
                else:
                    st.warning("🔧 Using Hash Embeddings (Fallback)")
           
            # Database actions
            st.subheader("🔧 Database Actions")
            col1, col2, col3 = st.columns(3)
           
            with col1:
                if st.button("🔄 Refresh Stats"):
                    st.experimental_rerun()
           
            with col2:
                if st.button("💾 Export Data"):
                    st.info("🚧 Feature coming soon...")
           
            with col3:
                if st.button("⚠️ Clear Database", type="secondary"):
                    if st.confirm("Are you sure? This will delete all data."):
                        try:
                            collection.delete()
                            st.success("✅ Database cleared!")
                            st.session_state.uploaded_files = []
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
           
        except Exception as e:
            st.error(f"❌ Database error: {str(e)}")
 
if __name__ == "__main__":
    main()