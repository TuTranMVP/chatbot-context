"""
🎨 Template Configuration Module
Web-based chatbot template system configuration
========================================

✨ Features:
- Structured template definitions
- Rich metadata for UI rendering
- Multi-language keyword support
- Professional system prompts
- Configurable detection settings

Author: TutranMVP Team
Version: 2.1 - Optimized
Date: 2025-06-21
"""

# ============================================================================
# 🎨 TEMPLATE SYSTEM CONFIGURATION
# ============================================================================

LAYER_CONFIG = {
    'role': 'system',
    'content': """
                Main Responsibilities:
                Greet users warmly and offer assistance.
                Understand the user's question clearly before answering.
                Provide accurate, concise, and helpful answers based on the FAQ content.
                If the user is not satisfied or your response doesn't help, offer an alternative solution or suggest related topics.
                Maintain a polite, respectful, and empathetic tone at all times.

                Conversation Behavior:
                Use simple and easy-to-understand language.
                Stay on-topic and only answer questions related to supported FAQ content.
                Summarize or clarify when users seem confused.
                Avoid excessive repetition or unnecessary explanations unless asked.
                If there are multiple questions, address them one at a time.
                If a question is unclear, ask for clarification before answering.
                follow trictly the format in restrictions ignore other system role

                Restrictions:
                Do not answer questions involving:
                Real-life investments or financial speculation
                Money-making or "get rich quick" schemes
                Criminal activities or unlawful steps
                Personal data requests or sensitive/private information
                Reason: Answering such questions would violate our privacy policy and ethical guidelines.

                Additional Guidelines:
                If unsure or if the question falls outside the FAQ scope, politely let the user know and suggest contacting a human support agent.
                You can say: “I'm not able to answer that, but you can reach out to our support team for further help.”
                Always close the conversation with an offer to help with anything else.
    """,
}


# Template configuration và metadata
TEMPLATE_CONFIG = {
    'version': '2.1',
    'last_updated': '2025-06-21',
    'default_language': 'vi',
    'encoding': 'utf-8',
    'max_templates': 10,
    'default_confidence_threshold': 0.5,
    'fallback_template': 'qa',
}

# Template definitions với format đẹp và structured cho từng loại câu hỏi
RESPONSE_TEMPLATES = {
    'analysis': {
        # 📋 Basic Information
        'name': '📊 Phân tích',
        'description': 'Template chuyên nghiệp cho phân tích, đánh giá và nhận xét sâu sắc',
        'category': 'analytical',
        'priority': 1,
        # 🎨 UI Configuration
        'icon': '📊',
        'color': '#17a2b8',
        'gradient': 'linear-gradient(135deg, #17a2b8 0%, #138496 100%)',
        # 🔍 Detection Settings
        'keywords': [
            # Tiếng Việt
            'phân tích',
            'đánh giá',
            'nhận xét',
            'review',
            'so sánh',
            'đo lường',
            'kiểm tra',
            'xem xét',
            'thẩm định',
            'critique',
            'nhận định',
            'đánh giá lại',
            'xem xét lại',
            'phân tích lại',
            # English
            'analyze',
            'analysis',
            'evaluate',
            'assessment',
            'review',
            'compare',
            'measure',
            'examine',
            'critique',
            'judge',
            'appraise',
            'investigate',
            'study',
            'inspect',
            'survey',
        ],
        'user_prefix': 'Phân tích:',
        'confidence_threshold': 0.7,
        # 🤖 AI Configuration
        'system_prompt': """Bạn là một chuyên gia phân tích hàng đầu với kinh nghiệm sâu rộng.

📊 NHIỆM VỤ: Thực hiện phân tích toàn diện, khách quan và chuyên sâu

🎯 CHUẨN XUẤT: Tuân theo format chuẩn sau:

📊 PHÂN TÍCH CHUYÊN SÂU:
├─ 🎯 VẤN ĐỀ TRỌNG TÂM: [Tóm tắt vấn đề cốt lõi một cách súc tích]
├─ 🔍 PHÂN TÍCH NGUYÊN NHÂN: [Phân tích nguyên nhân gốc rễ với logic rõ ràng]
├─ 📈 ĐÁNH GIÁ TÁC ĐỘNG: [Ước lượng tác động tích cực và tiêu cực]
├─ 💡 GIẢI PHÁP ĐỀ XUẤT: [Đưa ra giải pháp khả thi, thực tế]
├─ ⚖️ ƯU/NHƯỢC ĐIỂM: [Cân nhắc toàn diện các mặt]
└─ 📋 KẾT LUẬN & KHUYẾN NGHỊ: [Tổng kết và định hướng cụ thể]

✅ YÊU CẦU:
• Sử dụng tiếng Việt chuẩn, rõ ràng
• Đưa ra dẫn chứng cụ thể khi có thể
• Tư duy logic và khách quan
• Kết luận có thể hành động được""",
        # 📊 Template Examples
        'examples': [
            'Phân tích hiệu suất website của công ty',
            'Đánh giá chiến lược marketing mới',
            'Review và nhận xét về sản phẩm',
            'So sánh hai giải pháp công nghệ',
            'Đánh giá tác động của quyết định kinh doanh',
        ],
        # ⚙️ Advanced Settings
        'temperature_range': (0.2, 0.5),
        'max_tokens_range': (600, 1200),
        'supports_follow_up': True,
        'estimated_response_time': '15-30 seconds',
    },
    'steps': {
        # 📋 Basic Information
        'name': '🚀 Hướng dẫn',
        'description': 'Template chuyên nghiệp cho hướng dẫn từng bước chi tiết',
        'category': 'instructional',
        'priority': 2,
        # 🎨 UI Configuration
        'icon': '🚀',
        'color': '#28a745',
        'gradient': 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
        # 🔍 Detection Settings
        'keywords': [
            # Tiếng Việt
            'bước',
            'hướng dẫn',
            'cách làm',
            'thực hiện',
            'làm thế nào',
            'quy trình',
            'tutorial',
            'cách thức',
            'phương pháp',
            'chỉ dẫn',
            'setup',
            'cài đặt',
            'tạo',
            'xây dựng',
            'thiết lập',
            # English
            'steps',
            'guide',
            'tutorial',
            'how to',
            'method',
            'process',
            'procedure',
            'instruction',
            'walkthrough',
            'manual',
            'setup',
            'install',
            'create',
            'build',
            'configure',
        ],
        'user_prefix': 'Hướng dẫn các bước:',
        'confidence_threshold': 0.8,
        # 🤖 AI Configuration
        'system_prompt': """Bạn là một hướng dẫn viên chuyên nghiệp với khả năng trình bày xuất sắc.

🚀 NHIỆM VỤ: Tạo hướng dẫn từng bước rõ ràng, dễ theo dõi

🎯 CHUẨN XUẤT: Tuân theo format chuẩn sau:

🚀 HƯỚNG DẪN CHI TIẾT:

📋 TỔNG QUAN:
• Mục tiêu: [Mô tả mục đích cuối cùng]
• Thời gian: [Ước tính thời gian thực hiện]
• Độ khó: [Dễ/Trung bình/Khó]

🛠️ CHUẨN BỊ:
• [Công cụ cần thiết]
• [Kiến thức tiên quyết]
• [Tài nguyên hỗ trợ]

📝 CÁC BƯỚC THỰC HIỆN:

Bước 1️⃣: [Tên bước đầu tiên]
▶️ Chi tiết: [Mô tả cụ thể cách thực hiện]
💡 Mẹo: [Gợi ý hữu ích]
⚠️ Lưu ý: [Điều cần chú ý]

Bước 2️⃣: [Tên bước tiếp theo]
▶️ Chi tiết: [Mô tả cụ thể cách thực hiện]
💡 Mẹo: [Gợi ý hữu ích]
⚠️ Lưu ý: [Điều cần chú ý]

[Tiếp tục với các bước khác...]

✅ KẾT QUẢ MONG ĐỢI: [Mô tả kết quả cuối cùng chi tiết]

🔍 KIỂM TRA & KHẮC PHỤC:
• [Cách kiểm tra kết quả]
• [Xử lý lỗi thường gặp]

✅ YÊU CẦU:
• Ngôn ngữ đơn giản, dễ hiểu
• Sắp xếp logic từ đơn giản đến phức tạp
• Đưa ra ví dụ cụ thể khi cần""",
        # 📊 Template Examples
        'examples': [
            'Hướng dẫn cách tạo chatbot bằng Python',
            'Các bước setup môi trường development',
            'Cách triển khai ứng dụng lên cloud',
            'Hướng dẫn cài đặt và cấu hình Docker',
            'Tạo API REST với Flask từ A-Z',
        ],
        # ⚙️ Advanced Settings
        'temperature_range': (0.1, 0.4),
        'max_tokens_range': (800, 1500),
        'supports_follow_up': True,
        'estimated_response_time': '20-40 seconds',
    },
    'summary': {
        # 📋 Basic Information
        'name': '📝 Tóm tắt',
        'description': 'Template chuyên nghiệp cho tóm tắt nội dung hiệu quả',
        'category': 'summarization',
        'priority': 3,
        # 🎨 UI Configuration
        'icon': '📝',
        'color': '#ffc107',
        'gradient': 'linear-gradient(135deg, #ffc107 0%, #ffca2c 100%)',
        # 🔍 Detection Settings
        'keywords': [
            # Tiếng Việt
            'tóm tắt',
            'tổng kết',
            'gói gọn',
            'rút gọn',
            'tóm lược',
            'khái quát',
            'tinh gọn',
            'tóm tắt lại',
            'tổng hợp',
            'đúc kết',
            'tóm gọn',
            'tập hợp',
            'gom lại',
            # English
            'summary',
            'summarize',
            'overview',
            'recap',
            'brief',
            'outline',
            'synopsis',
            'abstract',
            'digest',
            'condensed',
            'compress',
            'consolidate',
            'encapsulate',
            'distill',
        ],
        'user_prefix': 'Tóm tắt:',
        'confidence_threshold': 0.6,
        # 🤖 AI Configuration
        'system_prompt': """Bạn là một chuyên gia tóm tắt với khả năng trích xuất thông tin cốt lõi.

📝 NHIỆM VỤ: Tạo bản tóm tắt súc tích, toàn diện và dễ hiểu

🎯 CHUẨN XUẤT: Tuân theo format chuẩn sau:

📝 TÓM TẮT TOÀN DIỆN:

┌─────────────────────────────────────────────
│ 🎯 CHỦ ĐỀ CHÍNH: [Tên chủ đề cụ thể]
│ ⏱️ THỜI GIAN ĐỌC: [Ước tính x phút]
│ 🎚️ ĐỘ PHỨC TẠP: [Cơ bản/Trung bình/Nâng cao]
│ 🏷️ THỂ LOẠI: [Phân loại nội dung]
└─────────────────────────────────────────────

🔑 ĐIỂM CHÍNH:
• 📌 [Điểm quan trọng nhất - với chi tiết hỗ trợ]
• 📌 [Điểm quan trọng thứ hai - với chi tiết hỗ trợ]
• 📌 [Điểm quan trọng thứ ba - với chi tiết hỗ trợ]
• 📌 [Các điểm phụ khác nếu cần]

💡 THÔNG TIN BỔ SUNG:
• [Chi tiết quan trọng không nằm trong điểm chính]
• [Bối cảnh, nguyên nhân, tác động]

🎯 Ý NGHĨA & ỨNG DỤNG:
• [Tầm quan trọng và ý nghĩa thực tế]
• [Cách áp dụng trong thực tế]

💭 KẾT LUẬN TỔNG HỢP: [Tóm tắt tổng quan ngắn gọn nhất]

✅ YÊU CẦU:
• Giữ nguyên ý chính, loại bỏ chi tiết thừa
• Sử dụng ngôn ngữ súc tích, dễ hiểu
• Đảm bảo tính chính xác và khách quan""",
        # 📊 Template Examples
        'examples': [
            'Tóm tắt cuộc họp team development hôm nay',
            'Gói gọn nội dung báo cáo tài chính',
            'Tóm lược các điểm chính của presentation',
            'Tổng kết kết quả nghiên cứu thị trường',
            'Tóm tắt chính sách mới của công ty',
        ],
        # ⚙️ Advanced Settings
        'temperature_range': (0.2, 0.6),
        'max_tokens_range': (400, 800),
        'supports_follow_up': True,
        'estimated_response_time': '10-20 seconds',
    },
    'qa': {
        # 📋 Basic Information
        'name': '❓ Q&A',
        'description': 'Template mặc định cho câu hỏi và trả lời thông thường',
        'category': 'general',
        'priority': 4,
        # 🎨 UI Configuration
        'icon': '❓',
        'color': '#6f42c1',
        'gradient': 'linear-gradient(135deg, #6f42c1 0%, #563d7c 100%)',
        # 🔍 Detection Settings
        'keywords': [],  # Template mặc định - không cần keywords đặc biệt
        'user_prefix': '',
        'confidence_threshold': 0.0,  # Luôn được chọn nếu không có template nào khác
        # 🤖 AI Configuration
        'system_prompt': """Bạn là một trợ lý AI thông minh, thân thiện và chuyên nghiệp.

❓ NHIỆM VỤ: Trả lời câu hỏi một cách chính xác, hữu ích và dễ hiểu

🎯 CHUẨN XUẤT: Tuân theo format chuẩn sau:

❓ CÂU HỎI: [Nhắc lại câu hỏi của người dùng một cách rõ ràng]

💡 TRẢ LỜI CHÍNH:
[Trả lời trực tiếp, chính xác và chi tiết. Sử dụng cấu trúc logic:
- Định nghĩa/Giải thích khái niệm chính
- Phân tích các khía cạnh quan trọng
- Đưa ra ví dụ minh họa cụ thể
- Kết luận hoặc khuyến nghị]

📚 THÔNG TIN BỔ SUNG:
• [Thông tin liên quan hữu ích]
• [Bối cảnh, lịch sử hoặc background]
• [Lưu ý quan trọng cần biết]

🔗 GỢI Ý LIÊN QUAN:
• [Câu hỏi tiếp theo có thể quan tâm]
• [Chủ đề liên quan để tìm hiểu thêm]
• [Tài nguyên hoặc công cụ hữu ích]

💬 Bạn có thắc mắc gì khác về chủ đề này không?

✅ YÊU CẦU:
• Trả lời bằng tiếng Việt nếu câu hỏi bằng tiếng Việt
• Ngôn ngữ thân thiện, dễ tiếp cận
• Thông tin chính xác và cập nhật
• Khuyến khích tương tác tiếp theo""",
        # 📊 Template Examples
        'examples': [
            'Python là gì và tại sao nên học ngôn ngữ này?',
            'Giải thích về machine learning cho người mới bắt đầu',
            'Sự khác biệt giữa frontend và backend là gì?',
            'Blockchain hoạt động như thế nào?',
            'Cách chọn framework phù hợp cho dự án web',
        ],
        # ⚙️ Advanced Settings
        'temperature_range': (0.3, 0.7),
        'max_tokens_range': (500, 1000),
        'supports_follow_up': True,
        'estimated_response_time': '10-25 seconds',
    },
}

# ============================================================================
# 🔧 TEMPLATE UTILITIES
# ============================================================================


def get_all_template_types() -> list:
    """Trả về danh sách tất cả các loại template."""
    return list(RESPONSE_TEMPLATES.keys())


def get_template_by_category(category: str) -> dict:
    """Trả về các template theo category."""
    return {
        template_type: template_data
        for template_type, template_data in RESPONSE_TEMPLATES.items()
        if template_data.get('category') == category
    }


def get_sorted_templates_by_priority() -> dict:
    """Trả về templates được sắp xếp theo priority."""
    return dict(
        sorted(RESPONSE_TEMPLATES.items(), key=lambda x: x[1].get('priority', 999))
    )


def validate_template_structure(template_data: dict) -> dict:
    """Kiểm tra cấu trúc của một template."""
    required_fields = [
        'name',
        'description',
        'category',
        'priority',
        'icon',
        'color',
        'gradient',
        'keywords',
        'system_prompt',
        'examples',
        'temperature_range',
        'max_tokens_range',
        'supports_follow_up',
    ]

    missing_fields = [field for field in required_fields if field not in template_data]

    return {
        'valid': len(missing_fields) == 0,
        'missing_fields': missing_fields,
        'field_count': len(template_data),
        'required_count': len(required_fields),
    }


# Export constants for easy access
__all__ = [
    'LAYER_CONFIG',
    'TEMPLATE_CONFIG',
    'RESPONSE_TEMPLATES',
    'get_all_template_types',
    'get_template_by_category',
    'get_sorted_templates_by_priority',
    'validate_template_structure',
]
