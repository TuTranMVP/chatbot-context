# Changelog - Lịch sử phát triển Maya AI

## Version 2.0.0 - Workshop Week 4 (2025-07-12)
### New Features:
- ✨ **File Manager**: Upload và quản lý file .txt, .md
- 🔍 **Advanced Search**: Tìm kiếm file theo tên và nội dung
- 📄 **File Preview**: Xem trước nội dung file trước khi sử dụng
- 💬 **File-to-Chat Integration**: Gửi nội dung file trực tiếp cho Maya phân tích
- 🗑️ **File Management**: Xóa file đơn lẻ hoặc xóa tất cả
- 🎨 **UI Improvements**: Cải thiện giao diện với navigation bars

### Technical Updates:
- 📁 Added `FileManager` class for file operations
- 🔧 Improved error handling for file operations
- 🎯 Added unique file ID system using MD5 hash
- 💾 Secure file storage in dedicated directory
- 🔄 Enhanced state management for file operations

### Bug Fixes:
- 🐛 Fixed import issues in file_manager module
- 🔧 Improved CSS styling for file manager components
- ✅ Added proper lint error handling

## Version 1.5.0 - Workshop Week 2
### Features:
- 🎤 **Voice Mode**: Tương tác bằng giọng nói
- 💬 **Chat Mode**: Trò chuyện văn bản
- 🎨 **Duolingo-style UI**: Giao diện thân thiện
- 📚 **Guides Section**: Hướng dẫn sử dụng
- 📊 **Data Display**: Hiển thị dữ liệu mẫu

### Technical:
- 🔧 Modular component architecture
- 🎵 TTS (Text-to-Speech) integration
- 🎙️ Voice recording and processing
- 🏗️ Streamlit-based web interface

## Version 1.0.0 - Initial Release
### Core Features:
- 🤖 **Basic AI Chat**: Trả lời câu hỏi cơ bản
- 🗄️ **ChromaDB Integration**: Lưu trữ và tìm kiếm văn bản
- 🌐 **Web Interface**: Giao diện web đơn giản
- 🔤 **Multi-language Support**: Hỗ trợ tiếng Việt và tiếng Anh

### Technical Foundation:
- 🐍 Python backend with Streamlit
- 🧠 OpenAI API integration
- 📚 Document processing and indexing
- 🔍 Vector similarity search
