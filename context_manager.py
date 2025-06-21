"""
🧠 Context Manager - Quản lý Context cho BotQA
================================================
   Manage and optimize the context of the conversation with,
   Help maintain context in long conversations.
"""

from datetime import datetime
import json
from typing import Dict, List, Optional


# Init Context Manager.
# Args:
#  max_context_length: The maximum number of messages is kept in Context
class ContextManager:
    def __init__(self, max_context_length: int = 20):
        self.message_history: List[Dict] = []
        self.max_context_length = max_context_length
        self.conversation_start = datetime.now()
        self.total_tokens_used = 0

    # Add a message to Context.
    #  role: 'system', 'user', or 'assistant'
    #  content: Message content
    #  metadata: Thông tin bổ sung (timestamp, token count, v.v.)
    def add_message(
        self, role: str, content: str, metadata: Optional[Dict] = None
    ) -> None:
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
        }

        self.message_history.append(message)
        self._optimize_if_needed()

    # Automatically optimize Context when exceeding the limit.
    def _optimize_if_needed(self) -> None:
        if len(self.message_history) > self.max_context_length:
            self._smart_optimize()

    # Smart Context optimization:
    # -Giữ lại system messages
    # -Giữ lại một số tin nhắn quan trọng đầu cuộc trò chuyện
    # -Giữ lại các tin nhắn gần đây nhất
    def _smart_optimize(self) -> None:
        # Tách các loại tin nhắn
        system_messages = [
            msg for msg in self.message_history if msg['role'] == 'system'
        ]
        user_assistant_messages = [
            msg for msg in self.message_history if msg['role'] != 'system'
        ]

        # Tính toán số tin nhắn cần giữ
        keep_recent = (
            self.max_context_length - len(system_messages) - 2
        )  # -2 để dành chỗ cho tin nhắn quan trọng

        if keep_recent < 4:
            keep_recent = 4  # Tối thiểu giữ 4 tin nhắn gần đây

        # Giữ lại: system messages + 2 tin nhắn đầu + N tin nhắn gần nhất
        important_early = (
            user_assistant_messages[:2]
            if len(user_assistant_messages) > keep_recent
            else []
        )
        recent_messages = user_assistant_messages[-keep_recent:]

        # Tránh trùng lặp
        if important_early:
            recent_messages = [
                msg for msg in recent_messages if msg not in important_early
            ]

        # Tạo context mới
        self.message_history = system_messages + important_early + recent_messages

    # Return to current context
    def get_context(self) -> List[Dict]:
        return self.message_history.copy()

    # Return statistics context
    def get_context_summary(self) -> Dict:
        user_count = len([msg for msg in self.message_history if msg['role'] == 'user'])
        assistant_count = len(
            [msg for msg in self.message_history if msg['role'] == 'assistant']
        )
        system_count = len(
            [msg for msg in self.message_history if msg['role'] == 'system']
        )

        # Ước tính tokens (1 từ ≈ 1.3 tokens)
        estimated_tokens = sum(
            len(msg['content'].split()) * 1.3 for msg in self.message_history
        )

        duration = datetime.now() - self.conversation_start

        return {
            'total_messages': len(self.message_history),
            'user_messages': user_count,
            'assistant_messages': assistant_count,
            'system_messages': system_count,
            'estimated_tokens': round(estimated_tokens),
            'conversation_duration': str(duration).split('.')[0],  # Remove microseconds
            'max_context_length': self.max_context_length,
            'context_usage_percent': round(
                (len(self.message_history) / self.max_context_length) * 100, 1
            ),
        }

    # Xóa context
    # keep_system: Có giữ lại system messages không
    def clear_context(self, keep_system: bool = True) -> None:
        if keep_system:
            system_messages = [
                msg for msg in self.message_history if msg['role'] == 'system'
            ]
            self.message_history = system_messages
        else:
            self.message_history.clear()

        self.conversation_start = datetime.now()

    # Xuất context ra file JSON.
    def export_context(self, filename: Optional[str] = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'context_export_{timestamp}.json'

        export_data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'conversation_start': self.conversation_start.isoformat(),
                'summary': self.get_context_summary(),
            },
            'context': self.message_history,
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        return filename

    # Tải context từ file JSON.
    # Returns True if the load is successful, false if there is an error
    def load_context(self, filename: str) -> bool:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.message_history = data.get('context', [])

            # Khôi phục thời gian bắt đầu cuộc trò chuyện
            export_info = data.get('export_info', {})
            if 'conversation_start' in export_info:
                self.conversation_start = datetime.fromisoformat(
                    export_info['conversation_start']
                )

            return True
        except Exception as e:
            print(f'❌ Lỗi khi tải context: {e}')
            return False

    # Get N the most recent message.
    # n_messages: Số tin nhắn cần lấy
    # Returns: danh sách tin nhắn gần đây
    def get_recent_context(self, n_messages: int = 5) -> List[Dict]:
        return self.message_history[-n_messages:] if self.message_history else []

    # Tìm kiếm trong context.
    # keyword: Từ khóa cần tìm
    # role: Lọc theo role ('user', 'assistant', 'system')
    # Returns: danh sách tin nhắn chứa từ khóa
    # Nếu role là None, tìm kiếm trong tất cả các tin nhắn
    def search_context(self, keyword: str, role: Optional[str] = None) -> List[Dict]:
        results = []
        keyword_lower = keyword.lower()

        for msg in self.message_history:
            # Lọc theo role nếu có
            if role and msg['role'] != role:
                continue

            # Tìm kiếm trong content
            if keyword_lower in msg['content'].lower():
                results.append(msg)

        return results

    # Phân tích và trả về các chủ đề chính trong cuộc trò chuyện.
    def get_conversation_topics(self) -> List[str]:
        # Lấy tất cả user messages
        user_messages = [
            msg['content'] for msg in self.message_history if msg['role'] == 'user'
        ]

        if not user_messages:
            return []

        # Extract keywords (simplified)
        topics = []
        common_words = {
            'là',
            'của',
            'và',
            'có',
            'trong',
            'được',
            'này',
            'đó',
            'với',
            'cho',
            'về',
            'như',
            'từ',
            'một',
            'sẽ',
            'để',
            'bạn',
            'tôi',
            'chúng',
            'ta',
            'họ',
        }

        for message in user_messages:
            words = message.lower().split()
            # Lấy các từ có độ dài >= 3 và không phải stop words
            meaningful_words = [
                word for word in words if len(word) >= 3 and word not in common_words
            ]
            topics.extend(meaningful_words)

        # Đếm tần suất và lấy top topics
        from collections import Counter

        topic_counts = Counter(topics)
        top_topics = [topic for topic, count in topic_counts.most_common(10)]

        return top_topics


# Ví dụ sử dụng
if __name__ == '__main__':
    # Demo Context Manager
    print('🧠 Demo Context Manager')
    print('=' * 50)

    # Tạo context manager
    context = ContextManager(max_context_length=10)

    # Thêm system prompt
    context.add_message('system', 'Bạn là một trợ lý AI thông minh và thân thiện.')

    # Simulation conversation
    context.add_message('user', 'Xin chào! Python là gì?')
    context.add_message(
        'assistant', 'Python là một ngôn ngữ lập trình mạnh mẽ và dễ học...'
    )
    context.add_message('user', 'Tại sao nên học Python?')
    context.add_message(
        'assistant', 'Python có nhiều ưu điểm: syntax đơn giản, community lớn...'
    )

    # Hiển thị thống kê
    summary = context.get_context_summary()
    print('📊 Context Summary:')
    for key, value in summary.items():
        print(f'   {key}: {value}')

    # Tìm kiếm
    search_results = context.search_context('Python')
    print(f"\n🔍 Tìm kiếm 'Python': {len(search_results)} kết quả")

    # Xuất context
    filename = context.export_context()
    print(f'\n💾 Đã xuất context ra file: {filename}')

    print('\n✅ Demo hoàn thành!')
