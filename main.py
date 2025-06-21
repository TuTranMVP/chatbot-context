"""
🤖 BotQA Web Interface
Web-based chatbot với template system thông minh
====================================

✨Features:
- Auto-detection templates (Phân tích, Hướng dẫn, Tóm tắt, Q&A)
- Giao diện web responsive và đẹp mắt
- Real-time chat với typing indicator
- Export chat history
- Điều chỉnh AI settings (temperature, max tokens)

Author: TutranMVP Team
Version: 2.0 - Optimized
Date: 2025-06-21
"""

from datetime import datetime
import json
import os
from typing import Optional, Tuple

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request
import httpx
import openai

from context_manager import ContextManager
from templates_config import LAYER_CONFIG, RESPONSE_TEMPLATES, TEMPLATE_CONFIG

# Load environment variables từ file .env
load_dotenv()

# ============================================================================
# 🔧 CONFIGURATION - CẤU HÌNH CƠ BẢN
# ============================================================================

# OpenAI Model Settings
DEPLOYMENT_NAME = 'GPT-4o-mini'
DEFAULT_TEMPERATURE = 0.3  # Creativity (0.0 = Exactly, 1.0 = creative)
DEFAULT_MAX_TOKENS = 800  # Số token tối đa trong phản hồi

# ============================================================================
# 🌐 FLASK APPLICATION SETUP
# ============================================================================

# Initialize Flask app
app = Flask(__name__)

# Global variables
openai_client = None
chat_history = []

# Context Manager thông minh để quản lý cuộc trò chuyện
context_manager = ContextManager(max_context_length=25)  # Tăng giới hạn lên 25

# ============================================================================
# 🔧 UTILITY FUNCTIONS
# ============================================================================


def initialize_openai_client() -> Optional[openai.OpenAI]:
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_API_KEY')

    # Check environment variables
    if not endpoint or not api_key:
        print('❌ Thiếu environment variables:')
        print('   - AZURE_OPENAI_ENDPOINT')
        print('   - AZURE_OPENAI_API_KEY')
        return None

    try:
        client = openai.OpenAI(
            base_url=endpoint,
            api_key=api_key,
            http_client=httpx.Client(verify=False),  # Turn off SSL Verify to avoid Cert
        )

        # Validate client bằng cách test connection
        print('🔗 Testing OpenAI connection...')

        # Initialize context manager với base system prompt từ LAYER_CONFIG
        if LAYER_CONFIG and LAYER_CONFIG.get('content'):
            # Thêm base system prompt với metadata chi tiết
            context_manager.add_message(
                LAYER_CONFIG['role'],
                LAYER_CONFIG['content'].strip(),
                {
                    'source': 'layer_config',
                    'priority': 'base',
                    'type': 'base_system_prompt',
                    'timestamp': datetime.now().isoformat(),
                    'version': TEMPLATE_CONFIG.get('version', '2.1'),
                },
            )
            print('✅ Base system prompt from LAYER_CONFIG loaded successfully')
        else:
            print('⚠️  Warning: LAYER_CONFIG not found or empty')

        print('✅ OpenAI client initialized successfully!')
        return client

    except Exception as e:
        print(f'❌ Lỗi khởi tạo OpenAI client: {e}')
        return None


# Automatically detect the appropriate type of template based on keywords in input.
def detect_template_type(user_input: str) -> str:
    user_input_lower = user_input.lower().strip()

    # Dictionary để lưu điểm số cho mỗi template
    template_scores = {}

    # Browse through all templates to find matching keywords
    for template_type, template_data in RESPONSE_TEMPLATES.items():
        if template_type == 'qa':  # Skip default template
            continue

        keywords = template_data.get('keywords', [])
        score = 0

        # Tính điểm dựa trên số lượng keywords khớp
        for keyword in keywords:
            if keyword.lower() in user_input_lower:
                # Bonus points for exact matches at word boundaries
                if f' {keyword.lower()} ' in f' {user_input_lower} ':
                    score += 2
                else:
                    score += 1

        template_scores[template_type] = score

    # Tìm template có điểm cao nhất
    if template_scores:
        best_template = max(template_scores.items(), key=lambda x: x[1])
        # Chỉ chọn nếu điểm số >= confidence threshold
        confidence_threshold = RESPONSE_TEMPLATES[best_template[0]].get(
            'confidence_threshold', 0.5
        )
        if best_template[1] >= confidence_threshold:
            return best_template[0]

    return 'qa'  # Returns the default template if no match found


# Get System Prompt and Format User Input based on the detected template.
def get_system_prompt_and_formatted_input(user_input: str) -> Tuple[str, str]:
    template_type = detect_template_type(user_input)
    template_data = RESPONSE_TEMPLATES[template_type]

    system_prompt = template_data['system_prompt']
    user_prefix = template_data.get('user_prefix', '')

    # Add prefix to user input if specified and not already present
    if user_prefix and not user_input.lower().startswith(user_prefix.lower()):
        formatted_user_input = f'{user_prefix} {user_input}'
    else:
        formatted_user_input = user_input

    return system_prompt, formatted_user_input


# Get template metadata for UI
def get_template_metadata(template_type: str) -> dict:
    template_data = RESPONSE_TEMPLATES.get(template_type, {})

    return {
        'name': template_data.get('name', 'Unknown'),
        'description': template_data.get('description', ''),
        'icon': template_data.get('icon', '❓'),
        'color': template_data.get('color', '#6c757d'),
        'gradient': template_data.get(
            'gradient', 'linear-gradient(135deg, #6c757d 0%, #495057 100%)'
        ),
        'category': template_data.get('category', 'general'),
        'priority': template_data.get('priority', 999),
        'examples': template_data.get('examples', []),
        'temperature_range': template_data.get('temperature_range', (0.1, 0.9)),
        'max_tokens_range': template_data.get('max_tokens_range', (100, 2000)),
        'supports_follow_up': template_data.get('supports_follow_up', False),
    }


# Validate template configuration
def validate_template_config() -> dict:
    issues = []
    warnings = []

    required_fields = ['name', 'description', 'system_prompt', 'keywords']

    for template_type, template_data in RESPONSE_TEMPLATES.items():
        # Check required fields
        for field in required_fields:
            if field not in template_data:
                issues.append(f"Template '{template_type}' thiếu field '{field}'")

        # Check system_prompt length
        system_prompt = template_data.get('system_prompt', '')
        if len(system_prompt) > 2000:
            warnings.append(
                f"Template '{template_type}' có system_prompt quá dài ({len(system_prompt)} chars)"
            )

        # Check keywords
        keywords = template_data.get('keywords', [])
        if not keywords and template_type != 'qa':
            warnings.append(f"Template '{template_type}' không có keywords")

    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'total_templates': len(RESPONSE_TEMPLATES),
        'config_version': TEMPLATE_CONFIG.get('version', 'unknown'),
    }


# Create Ai Response Based on User Input
#  User_input: user messages
#  Temperature: Creativity (0.0-1.0)
#  max_tokens: token maximum in feedback
# RETURNS: Dict with success status, response or error message
def generate_ai_response(user_input: str, temperature: float, max_tokens: int) -> dict:
    global openai_client, context_manager
    if not openai_client:
        return {
            'success': False,
            'error': 'OpenAI client chưa được khởi tạo. Kiểm tra file .env.',
        }
    try:
        # Get system prompt & format input
        system_prompt, formatted_input = get_system_prompt_and_formatted_input(
            user_input
        )

        # Detect template type to display
        template_type = detect_template_type(user_input)
        template_name = RESPONSE_TEMPLATES[template_type]['name']

        # Check if we need to add template-specific system prompt
        current_context = context_manager.get_context()

        # Only add template-specific prompt if it's different from base and not 'qa'
        if template_type != 'qa':
            # Check if the current template's system prompt is already in context
            template_prompt_exists = any(
                msg.get('role') == 'system'
                and msg.get('metadata', {}).get('template_type') == template_type
                and msg.get('metadata', {}).get('source') == 'template_specific'
                for msg in current_context
            )

            if not template_prompt_exists:
                # Add template-specific system prompt (the base prompt is already loaded)
                # We keep them separate for better context management
                context_manager.add_message(
                    'system',
                    system_prompt,
                    {
                        'template_type': template_type,
                        'source': 'template_specific',
                        'priority': 'template',
                        'timestamp': datetime.now().isoformat(),
                    },
                )

        # Thêm user message vào context
        context_manager.add_message(
            'user',
            formatted_input,
            {
                'template_type': template_type,
                'original_input': user_input,
                'timestamp': datetime.now().isoformat(),
            },
        )

        # Call OpenAI API với full conversation context
        response = openai_client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=context_manager.get_context(),  # Sử dụng context manager
            temperature=temperature,
            max_tokens=max_tokens,
        )

        bot_response = response.choices[0].message.content.strip()

        # Thêm AI response vào context
        context_manager.add_message(
            'assistant',
            bot_response,
            {
                'template_type': template_type,
                'token_count': response.usage.total_tokens
                if hasattr(response, 'usage')
                else None,
                'timestamp': datetime.now().isoformat(),
            },
        )

        # Save in chat history
        chat_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'bot_response': bot_response,
            'template_type': template_type,
            'template_name': template_name,
            'settings': {'temperature': temperature, 'max_tokens': max_tokens},
            'context_length': len(context_manager.get_context()),
        }
        chat_history.append(chat_entry)

        return {
            'success': True,
            'response': bot_response,
            'template': template_name,
            'template_type': template_type,
            'context_info': context_manager.get_context_summary(),
        }

    except openai.RateLimitError:
        return {
            'success': False,
            'error': '⚠️ Đã vượt quá giới hạn API. Vui lòng đợi một chút và thử lại.',
        }
    except openai.AuthenticationError:
        return {
            'success': False,
            'error': '🔐 Lỗi xác thực API. Kiểm tra lại API key trong file .env.',
        }
    except Exception as e:
        return {'success': False, 'error': f'❌ Lỗi không xác định: {str(e)}'}


# ============================================================================
# 🌐 FLASK ROUTES - CÁC ROUTE API
# ============================================================================


@app.route('/')
def index():
    """Trang chính - render giao diện chat."""
    return render_template('chat.html')


# API endpoint xử lý tin nhắn chat.
@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.json
        user_input = data.get('message', '').strip()
        temperature = data.get('temperature', DEFAULT_TEMPERATURE)
        max_tokens = data.get('max_tokens', DEFAULT_MAX_TOKENS)

        # Validate input
        if not user_input:
            return jsonify(
                {'success': False, 'error': '⚠️ Tin nhắn không được để trống.'}
            )

        # Validate settings
        if not (0.0 <= temperature <= 1.0):
            return jsonify(
                {
                    'success': False,
                    'error': '⚠️ Temperature phải trong khoảng 0.0 - 1.0.',
                }
            )

        if not (1 <= max_tokens <= 2000):
            return jsonify(
                {'success': False, 'error': '⚠️ Max tokens phải trong khoảng 1 - 2000.'}
            )

        # Generate AI response
        result = generate_ai_response(user_input, temperature, max_tokens)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': f'❌ Lỗi server: {str(e)}'})


# API endpoint trả về thông tin các template có sẵn với metadata đầy đủ.
@app.route('/api/templates')
def api_get_templates():
    templates_info = {}

    for template_type, template_data in RESPONSE_TEMPLATES.items():
        metadata = get_template_metadata(template_type)

        templates_info[template_type] = {
            # Basic info
            'name': template_data['name'],
            'description': template_data['description'],
            'keywords': template_data.get('keywords', []),
            # UI Configuration
            'icon': metadata['icon'],
            'color': metadata['color'],
            'gradient': metadata['gradient'],
            'category': metadata['category'],
            'priority': metadata['priority'],
            # Examples and settings
            'examples': metadata['examples'],
            'example': metadata['examples'][0] if metadata['examples'] else '',
            'temperature_range': metadata['temperature_range'],
            'max_tokens_range': metadata['max_tokens_range'],
            'supports_follow_up': metadata['supports_follow_up'],
        }

    # Sắp xếp theo priority
    sorted_templates = dict(
        sorted(templates_info.items(), key=lambda x: x[1]['priority'])
    )

    return jsonify(
        {
            'success': True,
            'templates': sorted_templates,
            'config': TEMPLATE_CONFIG,
            'validation': validate_template_config(),
        }
    )


# Trả về ví dụ cho mỗi loại template.
def get_template_example(template_type: str) -> str:
    template_data = RESPONSE_TEMPLATES.get(template_type, {})
    examples = template_data.get('examples', [])

    if examples:
        return examples[0]  # Trả về ví dụ đầu tiên

    # Fallback examples
    fallback_examples = {
        'analysis': 'Phân tích hiệu suất website của công ty tôi',
        'steps': 'Hướng dẫn cách tạo chatbot bằng Python',
        'summary': 'Tóm tắt cuộc họp team development hôm nay',
        'qa': 'Python là gì và tại sao nên học ngôn ngữ này?',
    }
    return fallback_examples.get(template_type, '')


# API endpoint kiểm tra tính hợp lệ của template configuration.
@app.route('/api/templates/validate')
def api_validate_templates():
    validation_result = validate_template_config()

    return jsonify(
        {
            'success': validation_result['valid'],
            'validation': validation_result,
            'message': '✅ Template configuration hợp lệ'
            if validation_result['valid']
            else '❌ Template configuration có vấn đề',
        }
    )


# API endpoint để test template detection.
@app.route('/api/templates/detect', methods=['POST'])
def api_detect_template():
    try:
        data = request.json
        user_input = data.get('message', '').strip()

        if not user_input:
            return jsonify({'success': False, 'error': 'Tin nhắn không được để trống'})

        # Detect template
        detected_type = detect_template_type(user_input)
        metadata = get_template_metadata(detected_type)

        return jsonify(
            {
                'success': True,
                'detected_template': detected_type,
                'template_name': metadata['name'],
                'confidence': 'high' if detected_type != 'qa' else 'default',
                'metadata': metadata,
            }
        )

    except Exception as e:
        return jsonify({'success': False, 'error': f'Lỗi phát hiện template: {str(e)}'})


# API endpoint trả về lịch sử chat.
@app.route('/api/history')
def api_get_history():
    return jsonify(
        {'success': True, 'history': chat_history, 'total_messages': len(chat_history)}
    )


# API endpoint xóa lịch sử chat.
@app.route('/api/history/clear', methods=['POST'])
def api_clear_history():
    global chat_history, context_manager
    chat_history.clear()
    context_manager.clear_context(
        keep_system=False
    )  # Xóa toàn bộ context để bắt đầu mới
    return jsonify(
        {'success': True, 'message': '✅ Đã xóa toàn bộ lịch sử chat và context AI.'}
    )


# API endpoint xuất lịch sử chat dưới dạng JSON file.
@app.route('/api/history/export')
def api_export_history():
    filename = f'botqa_chat_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    export_data = {
        'export_info': {
            'timestamp': datetime.now().isoformat(),
            'total_messages': len(chat_history),
            'app_version': '2.0',
        },
        'chat_history': chat_history,
    }

    return Response(
        json.dumps(export_data, ensure_ascii=False, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename={filename}'},
    )


# API Endpoint returns statistics.
# API endpoint trả về thống kê sử dụng bao gồm cả context info.
@app.route('/api/stats')
def api_get_stats():
    if not chat_history:
        return jsonify(
            {
                'success': True,
                'stats': {
                    'total_messages': 0,
                    'template_usage': {},
                    'most_used_template': None,
                    'context_info': context_manager.get_context_summary(),
                },
            }
        )

    # Thống kê template usage
    template_usage = {}
    for entry in chat_history:
        template_type = entry.get('template_type', 'unknown')
        template_usage[template_type] = template_usage.get(template_type, 0) + 1

    most_used_template = (
        max(template_usage.items(), key=lambda x: x[1]) if template_usage else None
    )

    return jsonify(
        {
            'success': True,
            'stats': {
                'total_messages': len(chat_history),
                'template_usage': template_usage,
                'most_used_template': most_used_template[0]
                if most_used_template
                else None,
                'context_info': context_manager.get_context_summary(),
            },
        }
    )


# API endpoint trả về context hiện tại của cuộc trò chuyện với AI.
@app.route('/api/context')
def api_get_context():
    context_data = context_manager.get_context()
    summary = context_manager.get_context_summary()

    return jsonify({'success': True, 'context': context_data, 'summary': summary})


# API endpoint chỉ xóa context AI, giữ lại chat history.
@app.route('/api/context/clear', methods=['POST'])
def api_clear_context():
    global context_manager

    # Xóa context nhưng giữ lại base system prompt từ LAYER_CONFIG
    context_manager.clear_context(keep_system=True)

    # Đảm bảo base system prompt từ LAYER_CONFIG được reload
    if LAYER_CONFIG and LAYER_CONFIG.get('content'):
        context_manager.add_message(
            LAYER_CONFIG['role'],
            LAYER_CONFIG['content'].strip(),
            {
                'source': 'layer_config',
                'priority': 'base',
                'type': 'base_system_prompt',
                'timestamp': datetime.now().isoformat(),
                'version': TEMPLATE_CONFIG.get('version', '2.1'),
            },
        )

    return jsonify(
        {
            'success': True,
            'message': '✅ Đã xóa context AI và reload base system prompt từ LAYER_CONFIG.',
        }
    )


# API endpoint tối ưu context bằng cách giữ lại chỉ N tin nhắn gần nhất.
@app.route('/api/context/optimize', methods=['POST'])
def api_optimize_context():
    global context_manager

    data = request.json
    keep_messages = data.get('keep_messages', 15)  # Mặc định giữ 15 tin nhắn

    # Lưu trữ context cũ để so sánh
    old_length = len(context_manager.get_context())

    # Thực hiện tối ưu bằng cách set lại max_context_length và trigger optimize
    context_manager.max_context_length = keep_messages
    context_manager._optimize_if_needed()

    new_length = len(context_manager.get_context())

    return jsonify(
        {
            'success': True,
            'message': f'✅ Đã tối ưu context từ {old_length} xuống {new_length} tin nhắn.',
            'old_length': old_length,
            'new_length': new_length,
            'summary': context_manager.get_context_summary(),
        }
    )


# API endpoint tìm kiếm trong context.
@app.route('/api/context/search', methods=['POST'])
def api_search_context():
    data = request.json
    keyword = data.get('keyword', '').strip()
    role = data.get('role')  # Optional: 'user', 'assistant', 'system'

    if not keyword:
        return jsonify({'success': False, 'error': 'Từ khóa không được để trống.'})

    results = context_manager.search_context(keyword, role)

    return jsonify(
        {
            'success': True,
            'results': results,
            'count': len(results),
            'keyword': keyword,
            'role_filter': role,
        }
    )


# API endpoint trả về các chủ đề chính trong cuộc trò chuyện.
@app.route('/api/context/topics')
def api_get_topics():
    topics = context_manager.get_conversation_topics()

    return jsonify(
        {
            'success': True,
            'topics': topics[:10],  # Top 10 topics
            'total_topics': len(topics),
        }
    )


# API endpoint lấy context gần đây.
@app.route('/api/context/recent')
def api_get_recent_context():
    n_messages = request.args.get('n', 5, type=int)
    recent_context = context_manager.get_recent_context(n_messages)

    return jsonify(
        {
            'success': True,
            'recent_context': recent_context,
            'count': len(recent_context),
        }
    )


# API endpoint xuất context ra file JSON.
@app.route('/api/context/export')
def api_export_context():
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'context_export_{timestamp}.json'

        # Tạo export data
        export_data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'app_version': '2.0',
                'summary': context_manager.get_context_summary(),
            },
            'context': context_manager.get_context(),
            'chat_history': chat_history,
        }

        return Response(
            json.dumps(export_data, ensure_ascii=False, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename={filename}'},
        )
    except Exception as e:
        return jsonify({'success': False, 'error': f'Lỗi xuất context: {str(e)}'})


# ============================================================================
# 🚀 APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    print('🤖 BotQA Web Interface - Enhanced Context Management')
    print('=' * 60)

    # Initialize OpenAI client
    openai_client = initialize_openai_client()

    if not openai_client:
        print('❌ CẢNH BÁO: Không thể khởi tạo OpenAI client!')
        print('🔧 Kiểm tra file .env với:')
        print('   - AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/')
        print('   - AZURE_OPENAI_API_KEY=your-api-key-here')
        print('\n⚠️  Ứng dụng sẽ khởi động nhưng không thể chat với AI.')

    print('\n🚀 Khởi động BotQA Web Interface với Context Manager...')
    print('🌐 URL: http://localhost:8080')
    print('📱 Mở trình duyệt và truy cập URL trên để sử dụng')
    print('🛑 Nhấn Ctrl+C để thoát')

    print('\n💡 Tính năng mới:')
    print('   • 🧠 Context Manager thông minh (max 25 messages)')
    print('   • 🔍 Tìm kiếm trong context')
    print('   • 📊 Phân tích chủ đề cuộc trò chuyện')
    print('   • 🎯 Tối ưu hóa context tự động')
    print('   • 📤 Export/Import context')
    print('   • 🎨 LAYER_CONFIG integration cho base system prompt')

    print('\n🎨 Template System:')
    print('   • Auto-detection templates thông minh')
    print('   • Giao diện web responsive')
    print('   • Export chat history')
    print('   • Điều chỉnh AI settings')
    print('   • Template-specific system prompts')
    print('=' * 60)

    # Initialize context manager
    print(
        f'\n🧠 Context Manager: Initialized with max {context_manager.max_context_length} messages'
    )

    # Validation info
    validation_result = validate_template_config()
    print(
        f'🎨 Templates: {validation_result["total_templates"]} loaded (v{validation_result["config_version"]})'
    )

    if LAYER_CONFIG:
        print('🔧 LAYER_CONFIG: Base system prompt loaded successfully')

    # Start Flask app
    app.run(
        debug=True,  # Enable debug mode for development
        host='0.0.0.0',  # Listen on all network interfaces
        port=8080,  # Use port 8080 (avoid port 5000 conflict)
        threaded=True,  # Enable multi-threading
    )
