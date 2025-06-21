# 🤖 BotQA - Smart Chatbot Web Interface

<div align="center">

![BotQA Logo](https://img.shields.io/badge/🤖_BotQA-Smart_Chatbot-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-red?style=for-the-badge&logo=flask)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple?style=for-the-badge&logo=openai)

**Một ứng dụng chatbot web thông minh với hệ thống template tự động phát hiện và quản lý context nâng cao**

[🚀 Demo](#-demo) • [📋 Cài đặt](#-cài-đặt--setup) • [📖 Sử dụng](#-sử-dụng) • [🔧 API](#-api-endpoints) • [🤝 Đóng góp](#-contributing)

</div>

---

## ✨ Tính năng chính

### 🎯 **Template System Thông minh**
- **🔍 Auto-detection**: Tự động phát hiện loại câu hỏi và áp dụng template phù hợp
- **📊 Phân tích**: Cho các câu hỏi phân tích, đánh giá, review
- **🚀 Hướng dẫn**: Cho các câu hỏi về quy trình, bước thực hiện  
- **📝 Tóm tắt**: Cho các yêu cầu tóm tắt, gói gọn nội dung
- **❓ Q&A**: Template mặc định cho câu hỏi thông thường

### 🧠 **Context Management Nâng cao**
- **Smart Context**: Quản lý context thông minh với giới hạn 25 tin nhắn
- **Auto Optimization**: Tự động tối ưu context khi vượt giới hạn
- **Search & Topics**: Tìm kiếm trong lịch sử và phân tích chủ đề
- **Export/Import**: Xuất nhập context và lịch sử chat

### 🎨 **Giao diện Web Responsive**
- **Modern UI**: Thiết kế gradient, animations và visual indicators
- **Real-time Chat**: Chat thời gian thực với typing indicator
- **Template Controls**: Điều chỉnh AI settings (temperature, max tokens)
- **Mobile Friendly**: Tối ưu cho cả desktop và mobile

### 🔧 **LAYER_CONFIG Integration**
- **Base System Prompt**: Đảm bảo AI có hành vi nhất quán
- **Restriction Enforcement**: Áp dụng các hạn chế về nội dung
- **Dynamic Reload**: Reload cấu hình mà không cần restart

---

## 🚀 Demo

### 📸 Screenshots

```
🖥️ Desktop Interface:
Empty
```

### 🎬 Template Examples

**📊 Phân tích**
```
Input:  "Phân tích hiệu suất website của công ty"
Output: 🎨 Template: 📊 Phân tích
        🤖 Bot: Tôi sẽ giúp bạn phân tích hiệu suất website...
```

**🚀 Hướng dẫn**  
```
Input:  "Hướng dẫn cách setup Python environment"
Output: 🎨 Template: 🚀 Hướng dẫn
        🤖 Bot: Đây là các bước chi tiết để setup Python...
```

---

## 📋 Cài đặt & Setup

### 🔧 **Yêu cầu hệ thống**
- ![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python) Python 3.8 trở lên
- ![Azure](https://img.shields.io/badge/Azure-OpenAI_API-blue?logo=microsoft-azure) Azure OpenAI API access
- ![RAM](https://img.shields.io/badge/RAM-2GB+-orange) 2GB RAM (khuyến nghị)
- ![Browser](https://img.shields.io/badge/Browser-Modern-purple) Modern web browser

### 🛠️ **Cài đặt nhanh**

#### 1️⃣ **Clone Repository**
```bash
git clone <your-repository-url>
cd chatbot-context
```

#### 2️⃣ **Tạo Virtual Environment**
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (macOS/Linux)  
source venv/bin/activate
```

#### 3️⃣ **Cài đặt Dependencies**
```bash
# Cài đặt các package cần thiết
pip install flask python-dotenv openai httpx

# Hoặc từ requirements.txt (nếu có)
pip install -r requirements.txt
```

#### 4️⃣ **Cấu hình Environment Variables**
Tạo file `.env` trong thư mục gốc:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
```

> ⚠️ **Lưu ý**: Thay thế `your-resource` và `your-api-key-here` bằng thông tin thực tế của bạn.

#### 5️⃣ **Khởi chạy ứng dụng**
```bash
python main.py
```

#### 6️⃣ **Truy cập Web Interface**
Mở trình duyệt và truy cập:
```
🌐 http://localhost:8080
```

---

## 📁 Cấu trúc Project

```
chatbot-context/
├── 📄 main.py                      # Flask application chính
├── 🧠 context_manager.py           # Quản lý context AI  
├── 🎨 templates_config.py          # Cấu hình templates
├── 🔐 .env                         # Environment variables
├── ⚙️ pyproject.toml               # Ruff configuration
├── 📖 README.md                    # Documentation này
├── templates/
│   └── 🌐 chat.html               # Web interface chính
├── static/                         # Static files (Flask standard)
│   ├── css/
│   │   └── 🎨 chat.css            # Main stylesheet
│   └── js/
│       └── ⚡ chat.js              # Frontend JavaScript
├── docs/
│   ├── 📋 TEMPLATE_OPTIMIZATION.md
│   ├── 🔧 LAYER_CONFIG_INTEGRATION.md
│   └── 📊 LAYER_CONFIG_INTEGRATION_SUMMARY.md
└── __pycache__/                    # Python cache files
```

---

## 📖 Sử dụng

### 🎯 **Template Examples**

#### 📊 **Phân tích**
```
✅ "Phân tích hiệu suất website của công ty"
✅ "Đánh giá chiến lược marketing mới"  
✅ "Review sản phẩm này giúp tôi"
✅ "So sánh hai phương án đầu tư"
```

#### 🚀 **Hướng dẫn**
```
✅ "Hướng dẫn cách tạo chatbot bằng Python"
✅ "Các bước setup môi trường development"
✅ "Cách triển khai ứng dụng lên cloud"
✅ "Quy trình xử lý bug trong code"
```

#### 📝 **Tóm tắt**
```
✅ "Tóm tắt cuộc họp team development hôm nay"
✅ "Gói gọn nội dung báo cáo tài chính"
✅ "Tổng kết kết quả nghiên cứu thị trường"
✅ "Rút gọn bài thuyết trình 50 slide"
```

#### ❓ **Q&A (Default)**
```
✅ "Python là gì và tại sao nên học?"
✅ "Blockchain hoạt động như thế nào?"
✅ "Khác biệt giữa AI và Machine Learning?"
```

### 🎛️ **Controls & Settings**

| Control | Range | Description |
|---------|-------|-------------|
| 🌡️ **Temperature** | 0.0 - 1.0 | Điều chỉnh độ sáng tạo của AI |
| 📝 **Max Tokens** | 100 - 2000 | Giới hạn độ dài phản hồi |
| 📋 **Template Buttons** | - | Click để xem ví dụ template |

### 🛠️ **Chat Management**
- **🗑️ Xóa Chat**: Xóa giao diện chat và context
- **💾 Lưu Chat**: Copy toàn bộ chat vào clipboard
- **📋 Xuất JSON**: Tải xuống lịch sử dưới dạng JSON

---

## 🔧 API Endpoints

### 💬 **Chat & Templates**
```http
POST /api/chat                    # Gửi tin nhắn chat
GET  /api/templates               # Lấy thông tin templates  
POST /api/templates/detect        # Test template detection
GET  /api/templates/validate      # Kiểm tra cấu hình templates
```

### 🧠 **Context Management**
```http
GET  /api/context                 # Lấy context hiện tại
POST /api/context/clear           # Xóa context AI
POST /api/context/search          # Tìm kiếm trong context
GET  /api/context/topics          # Phân tích chủ đề
POST /api/context/optimize        # Tối ưu context
GET  /api/context/recent          # Lấy context gần đây
GET  /api/context/export          # Xuất context
```

### 🔧 **LAYER_CONFIG Management**
```http
GET  /api/layer-config            # Thông tin LAYER_CONFIG
POST /api/layer-config/reload     # Reload base system prompt
```

### 📊 **History & Stats**
```http
GET  /api/history                 # Lịch sử chat
POST /api/history/clear           # Xóa lịch sử
GET  /api/history/export          # Xuất lịch sử
GET  /api/stats                   # Thống kê sử dụng
```

### 📝 **API Usage Example**
```javascript
// Gửi tin nhắn
const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: "Phân tích hiệu suất website",
        temperature: 0.3,
        max_tokens: 800
    })
});

const data = await response.json();
console.log(data.response); // AI response
```

---

## 🔍 Troubleshooting

### ❌ **Lỗi thường gặp**

#### **OpenAI Connection Error**
```bash
❌ Lỗi khởi tạo OpenAI client
```
**💡 Giải pháp**:
1. Kiểm tra file `.env` có đúng format
2. Verify Azure OpenAI endpoint và API key
3. Đảm bảo resource OpenAI đang active

#### **Template không hoạt động**
```bash
⚠️ Template configuration có vấn đề
```
**💡 Giải pháp**:
1. Truy cập `/api/templates/validate` để kiểm tra
2. Xem console logs khi khởi động
3. Verify `templates_config.py`

#### **Context bị đầy**
```bash
🧠 Context usage: 100%
```
**💡 Giải pháp**:
1. Click "🗑️ Xóa Chat" để reset
2. Sử dụng API `/api/context/optimize`
3. Tăng `max_context_length` trong `main.py`

#### **Static files không load**
```bash
❌ 404 Not Found: /templates/static/css/chat.css
```
**💡 Giải pháp**:
1. Tạo thư mục structure: `templates/static/css/` và `templates/static/js/`
2. Copy CSS và JS files vào đúng vị trí
3. Restart Flask application

### 🔧 **Debug Commands**
```bash
# Kiểm tra API status
curl http://localhost:8080/api/templates/validate

# Test template detection
curl -X POST http://localhost:8080/api/templates/detect \
  -H "Content-Type: application/json" \
  -d '{"message": "Phân tích website"}'

# Check context status  
curl http://localhost:8080/api/context
```

---

## 🚀 Development

### 📋 **Code Quality**
Project sử dụng **Ruff** để maintain code quality:

```bash
# Format code
ruff format .

# Check linting
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### 🎨 **Adding New Templates**
1. **Thêm template** vào `templates_config.py`:
```python
'new_template': {
    'name': '🆕 Template Mới',
    'description': 'Mô tả template',
    'system_prompt': 'System prompt cho template...',
    'keywords': ['keyword1', 'keyword2'],
    # ... các fields khác
}
```

2. **Update UI** trong `chat.html`:
```html
<div class="template-btn new-template" data-template="new_template">
    <div style="font-weight: bold;">🆕 Template Mới</div>
    <div style="font-size: 11px; color: #6c757d;">Keywords...</div>
</div>
```

3. **Test template**:
```bash
curl -X GET http://localhost:8080/api/templates/validate
```

### 🔧 **Customizing LAYER_CONFIG**
Base system prompt có thể customize trong `templates_config.py`:

```python
LAYER_CONFIG = {
    'role': 'system',
    'content': """
    Custom base prompt here...
    
    Main Responsibilities:
    - Your custom instructions
    - Behavior guidelines
    
    Restrictions:
    - Custom restrictions
    """
}
```

### 🎨 **UI Customization**
Modify styles trong `templates/static/css/chat.css`:

```css
/* Custom theme colors */
:root {
    --primary-color: #your-color;
    --secondary-color: #your-secondary;
    --accent-color: #your-accent;
}
```

---

## 📊 Technical Details

### 🏗️ **Architecture**
- **🌐 Backend**: Flask 2.x với REST API
- **🤖 AI Integration**: OpenAI GPT-4o-mini via Azure  
- **🎨 Frontend**: Vanilla JavaScript + CSS3
- **🧠 Context Management**: Custom implementation với smart optimization
- **🎯 Template Detection**: Keyword-based scoring system

### ⚡ **Performance**
- **🚀 Response Time**: < 2s average cho standard queries
- **💾 Memory Usage**: ~50MB base + context data
- **🔄 Context Optimization**: Tự động khi > 25 messages
- **📱 Mobile Support**: Responsive design cho tất cả devices

### 🔒 **Security**
- **🔐 API Key Protection**: Environment variables
- **🚫 Content Filtering**: Built-in restrictions via LAYER_CONFIG
- **🛡️ Input Validation**: Server-side validation cho tất cả inputs
- **📝 Audit Logging**: Full request/response logging

---

## 📝 Changelog

### 🆕 **Version 2.1** (2025-06-21)
- ✅ Enhanced LAYER_CONFIG integration  
- ✅ Improved template detection accuracy
- ✅ Added dynamic reload APIs
- ✅ Better error handling và user feedback
- ✅ Mobile-responsive improvements

### 📋 **Version 2.0** (2025-06-20)
- ✅ Template system với auto-detection
- ✅ Context management system
- ✅ Modern web interface
- ✅ REST API endpoints
- ✅ Export/import functionality

---

## 🤝 Contributing

Chúng tôi hoan nghênh mọi đóng góp! 

### 🔄 **Process**
1. **Fork** repository
2. **Create** feature branch: `git checkout -b feature-name`
3. **Commit** changes: `git commit -am 'Add feature'`
4. **Push** branch: `git push origin feature-name`  
5. **Submit** Pull Request

### 📋 **Guidelines**
- Follow existing code style
- Add tests cho new features
- Update documentation
- Ensure all tests pass

### 🐛 **Bug Reports**
- Use GitHub Issues
- Include reproduction steps
- Provide system information
- Add relevant screenshots

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 TutranMVP Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🎉 Credits & Acknowledgments

### 👥 **Team**
- **Author**: TutranMVP Team
- **Version**: 2.1 - Optimized  
- **Date**: 2025-06-21

### 🙏 **Special Thanks**
- OpenAI team cho GPT-4o-mini model
- Flask community cho amazing framework
- Microsoft Azure cho OpenAI hosting

### 💝 **Built with**
- ❤️ Love for intelligent conversation experiences
- ☕ Lots of coffee
- 🎵 Great music
- 🚀 Passion for AI innovation

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

![GitHub stars](https://img.shields.io/github/stars/yourusername/chatbot-context?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/chatbot-context?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/yourusername/chatbot-context?style=social)

---

**Made with 🤖 by [TutranMVP Team](https://github.com/yourusername)**

</div>
