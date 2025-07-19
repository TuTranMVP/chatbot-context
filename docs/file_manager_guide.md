# File Manager - Hướng dẫn Code Flow

## 📋 Tổng quan
File Manager là component quan trọng trong Maya AI Assistant, cho phép người dùng upload, quản lý và tích hợp file văn bản (.txt, .md) với AI chatbot. Component này được thiết kế theo mô hình modular, dễ bảo trì và mở rộng.

## 🏗️ Kiến trúc tổng thể

```
File Manager Component
├── FileManager Class (Backend Logic)
├── render_file_manager() (UI Rendering)
├── render_file_manager_css() (Styling)
└── get_file_content_for_ai() (AI Integration)
```

## 🔧 Chi tiết các thành phần

### 1. FileManager Class - Logic xử lý file

#### 🔸 Khởi tạo (`__init__`)
```python
def __init__(self, upload_dir: str = "uploaded_files"):
    self.upload_dir = upload_dir
    self.ensure_upload_directory()
```
**Mục đích**: Khởi tạo thư mục lưu trữ file
**Luồng hoạt động**:
1. Thiết lập đường dẫn thư mục upload
2. Gọi `ensure_upload_directory()` để tạo thư mục nếu chưa tồn tại

#### 🔸 Tạo thư mục (`ensure_upload_directory`)
```python
def ensure_upload_directory(self):
    if not os.path.exists(self.upload_dir):
        os.makedirs(self.upload_dir)
```
**Mục đích**: Đảm bảo thư mục upload tồn tại
**Luồng hoạt động**:
1. Kiểm tra thư mục có tồn tại không
2. Nếu chưa tồn tại → tạo thư mục

#### 🔸 Lưu file (`save_uploaded_file`)
```python
def save_uploaded_file(self, uploaded_file) -> Dict:
    try:
        # Generate unique filename
        file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8]
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{file_hash}_{uploaded_file.name}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
            
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
        return None
```

**Mục đích**: Lưu file upload và tạo metadata
**Luồng hoạt động**:
1. **Tạo tên file unique**: Sử dụng MD5 hash của nội dung file
2. **Lưu file vào disk**: Ghi binary data vào file
3. **Tạo file_info dictionary**: Chứa metadata đầy đủ
4. **Tạo preview**: Gọi `get_file_preview()` để tạo preview nội dung
5. **Xử lý lỗi**: Hiển thị thông báo lỗi nếu có

**Tại sao dùng MD5 hash?**
- Tránh trùng lặp file
- Tạo ID unique cho file
- Bảo mật tên file gốc

#### 🔸 Tạo preview (`get_file_preview`)
```python
def get_file_preview(self, file_path: str, extension: str) -> str:
    try:
        if extension.lower() in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content[:500] + "..." if len(content) > 500 else content
        return "Preview not available for this file type"
    except Exception:
        return "Could not read file content"
```

**Mục đích**: Tạo preview ngắn gọn của file
**Luồng hoạt động**:
1. **Kiểm tra extension**: Chỉ hỗ trợ .txt, .md
2. **Đọc file**: Sử dụng encoding UTF-8
3. **Cắt ngắn nội dung**: Tối đa 500 ký tự
4. **Xử lý lỗi**: Return thông báo lỗi nếu không đọc được

#### 🔸 Đọc full content (`read_file_content`)
```python
def read_file_content(self, file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
```

**Mục đích**: Đọc toàn bộ nội dung file để gửi cho AI
**Luồng hoạt động**:
1. **Mở file**: Sử dụng encoding UTF-8
2. **Đọc toàn bộ**: Không giới hạn kích thước
3. **Xử lý lỗi**: Return thông báo lỗi có chi tiết

#### 🔸 Xóa file (`delete_file`)
```python
def delete_file(self, file_info: Dict) -> bool:
    try:
        if os.path.exists(file_info["path"]):
            os.remove(file_info["path"])
            return True
        return False
    except Exception:
        return False
```

**Mục đích**: Xóa file khỏi disk
**Luồng hoạt động**:
1. **Kiểm tra file tồn tại**: Dùng `os.path.exists()`
2. **Xóa file**: Dùng `os.remove()`
3. **Return status**: True nếu thành công, False nếu thất bại

#### 🔸 Tìm kiếm file (`search_files`)
```python
def search_files(self, query: str, files: List[Dict]) -> List[Dict]:
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
```

**Mục đích**: Tìm kiếm file theo tên hoặc nội dung
**Luồng hoạt động**:
1. **Kiểm tra query**: Nếu trống thì return tất cả
2. **Chuẩn hóa query**: Chuyển về lowercase
3. **Tìm kiếm trong tên**: So sánh với tên file
4. **Tìm kiếm trong nội dung**: So sánh với content preview
5. **Return kết quả**: Danh sách file phù hợp

### 2. render_file_manager() - Giao diện chính

#### 🔸 Session State Management
```python
# Initialize file manager
if 'file_manager' not in st.session_state:
    st.session_state.file_manager = FileManager()
    
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
```

**Mục đích**: Quản lý trạng thái ứng dụng
**Luồng hoạt động**:
1. **Khởi tạo FileManager**: Chỉ tạo 1 lần duy nhất
2. **Khởi tạo uploaded_files**: List lưu trữ metadata các file

#### 🔸 File Upload Section
```python
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
                st.warning(f"⚠️ File already exists: {uploaded_file.name}")
```

**Mục đích**: Xử lý upload file từ người dùng
**Luồng hoạt động**:
1. **Hiển thị file uploader**: Chỉ chấp nhận .txt, .md
2. **Kiểm tra file trùng lặp**: Dựa vào tên file
3. **Lưu file mới**: Gọi `save_uploaded_file()`
4. **Cập nhật session state**: Thêm file_info vào list
5. **Hiển thị thông báo**: Success hoặc warning

#### 🔸 Search & Filter Section
```python
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
```

**Mục đích**: Cung cấp tính năng tìm kiếm và xóa hàng loạt
**Luồng hoạt động**:
1. **Kiểm tra có file**: Chỉ hiển thị nếu có file
2. **Tạo search input**: Text input để nhập query
3. **Tạo Clear All button**: Xóa tất cả file
4. **Xử lý Clear All**: Xóa từng file và reset session state

#### 🔸 File Display Section
```python
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
                
                # Add to chat button
                if st.button("💬 Use in Chat", key=f"use_chat_{idx}", type="primary"):
                    file_content = st.session_state.file_manager.read_file_content(file_info['path'])
                    prompt = f"Based on this file content:\n\n**{file_info['name']}**\n\n{file_content}\n\nPlease analyze and help me with this document."
                    st.session_state.pending_message = prompt
                    st.session_state.current_mode = 'chat'
                    st.rerun()
```

**Mục đích**: Hiển thị danh sách file và các thao tác
**Luồng hoạt động**:
1. **Filter files**: Áp dụng search query
2. **Hiển thị từng file**: Sử dụng expander
3. **Hiển thị metadata**: Type, upload time, ID
4. **Preview button**: Toggle hiển thị/ẩn preview
5. **Delete button**: Xóa file cụ thể
6. **Use in Chat button**: Gửi full content cho AI

### 3. AI Integration Flow

#### 🔸 File-to-Chat Integration
```python
if st.button("💬 Use in Chat", key=f"use_chat_{idx}", type="primary"):
    file_content = st.session_state.file_manager.read_file_content(file_info['path'])
    prompt = f"Based on this file content:\n\n**{file_info['name']}**\n\n{file_content}\n\nPlease analyze and help me with this document."
    st.session_state.pending_message = prompt
    st.session_state.current_mode = 'chat'
    st.rerun()
```

**Mục đích**: Tích hợp file content với AI chatbot
**Luồng hoạt động**:
1. **Đọc full content**: Gọi `read_file_content()`
2. **Tạo prompt**: Format content với instruction
3. **Set pending message**: Để main app xử lý
4. **Chuyển mode**: Chuyển sang chat mode
5. **Trigger rerun**: Refresh UI

#### 🔸 Helper Function
```python
def get_file_content_for_ai(file_id: str) -> Optional[str]:
    if 'uploaded_files' not in st.session_state:
        return None
        
    file_info = next(
        (f for f in st.session_state.uploaded_files if f["id"] == file_id),
        None
    )
    
    if file_info and 'file_manager' in st.session_state:
        return st.session_state.file_manager.read_file_content(file_info['path'])
    
    return None
```

**Mục đích**: Utility function để lấy file content theo ID
**Luồng hoạt động**:
1. **Kiểm tra session state**: Đảm bảo có uploaded_files
2. **Tìm file theo ID**: Sử dụng next() với generator
3. **Đọc content**: Gọi read_file_content()
4. **Return content**: Hoặc None nếu không tìm thấy

## 🔄 Luồng hoạt động tổng thể

### 1. Khởi tạo
```
User truy cập Files mode
    ↓
render_file_manager() được gọi
    ↓
Khởi tạo FileManager instance
    ↓
Khởi tạo uploaded_files list
    ↓
Hiển thị UI upload
```

### 2. Upload File
```
User chọn file → st.file_uploader
    ↓
Kiểm tra file đã tồn tại chưa
    ↓
Gọi save_uploaded_file()
    ↓
Tạo unique filename với MD5 hash
    ↓
Lưu file vào disk
    ↓
Tạo file_info metadata
    ↓
Thêm vào uploaded_files list
    ↓
Hiển thị success message
```

### 3. Search & Filter
```
User nhập search query
    ↓
Gọi search_files() với query
    ↓
Tìm kiếm trong tên file
    ↓
Tìm kiếm trong content preview
    ↓
Return filtered list
    ↓
Hiển thị kết quả
```

### 4. Use in Chat
```
User click "Use in Chat"
    ↓
Gọi read_file_content()
    ↓
Tạo prompt với file content
    ↓
Set pending_message
    ↓
Chuyển sang chat mode
    ↓
Main app xử lý message
    ↓
AI phân tích và trả lời
```

## 🎯 Những điểm quan trọng

### ✅ Ưu điểm của thiết kế

1. **Modular Architecture**: Tách biệt logic và UI
2. **Error Handling**: Xử lý lỗi chu đáo
3. **Unique File Naming**: Tránh conflict với MD5 hash
4. **Search Functionality**: Tìm kiếm linh hoạt
5. **AI Integration**: Tích hợp mượt mà với chatbot
6. **Session State Management**: Quản lý trạng thái hiệu quả

### ⚠️ Những điểm cần lưu ý

1. **File Size Limit**: Chưa có giới hạn kích thước file
2. **Memory Usage**: Đọc toàn bộ file vào memory
3. **File Type Validation**: Chỉ dựa vào extension
4. **Concurrent Access**: Chưa xử lý truy cập đồng thời

### 🔧 Suggestions for Improvement

1. **Add file size limit**: Giới hạn kích thước upload
2. **Implement chunked reading**: Đọc file theo chunk
3. **Add file type validation**: Kiểm tra MIME type
4. **Add progress bar**: Hiển thị tiến trình upload
5. **Add file compression**: Nén file để tiết kiệm không gian

## 📚 Tài liệu tham khảo

- [Streamlit File Uploader](https://docs.streamlit.io/library/api-reference/widgets/st.file_uploader)
- [Python File Operations](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
- [Hashlib Documentation](https://docs.python.org/3/library/hashlib.html)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)
