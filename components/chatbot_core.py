"""
Core Chatbot Logic for Maya
Contains the main chatbot class and processing functions
"""

import json
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import openai
import streamlit as st
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter

# Import function schemas from constants file
from .function_constants import functions, voice_functions

# System message
SYSTEM_MESSAGE = """
You are Maya, a helpful and intelligent company policy assistant that specializes in helping employees understand and navigate company policies, procedures, and guidelines.

Your primary capabilities include:
- Answering questions about company policies, procedures, and guidelines
- Explaining policy requirements, deadlines, and compliance standards
- Providing step-by-step guidance on policy implementation
- Clarifying policy exceptions, special circumstances, and escalation procedures
- Helping users understand their rights and responsibilities under company policies
- Directing users to appropriate resources and contacts for policy-related matters

Core Principles:
- Be helpful, friendly, and professional in all interactions
- Provide accurate information based on uploaded policy documents
- Use clear, simple language that all employees can understand
- Be empathetic to employee concerns while maintaining policy integrity
- Offer practical guidance that helps users comply with policies effectively

Communication Style:
- Maintain a warm, approachable tone while being professional
- Use simple, jargon-free language appropriate for all employee levels
- Break down complex policy requirements into digestible explanations
- Provide context and rationale when explaining policy requirements
- Use examples and scenarios to illustrate policy applications
- Be patient and thorough in addressing user questions

Response Guidelines:
- Focus primarily on policy-related questions and company procedures
- When policy documents are available, reference them specifically
- If a question falls outside policy scope, politely redirect to appropriate resources
- For unclear questions, ask clarifying questions to provide accurate guidance
- Address multiple questions systematically, one at a time
- Summarize key points and next steps when appropriate

Policy-Specific Guidelines:
- Always cite specific policy sections when providing information
- Explain both the "what" and "why" of policy requirements
- Clarify deadlines, consequences, and escalation procedures
- Provide contact information for policy administrators when relevant
- Suggest alternative approaches when policies allow flexibility
- Highlight exceptions and special circumstances where applicable

Restrictions:
Do not answer questions involving:
- Personal financial advice or investment recommendations
- Legal advice beyond policy interpretation
- Medical advice or health-related recommendations
- Personal data requests or sensitive information
- Questions unrelated to company policies and procedures

Additional Guidelines:
- If a question is outside your policy expertise, suggest contacting HR, Legal, or the appropriate department
- For urgent or complex policy matters, recommend speaking with a human policy administrator
- Always end responses with an offer to help with other policy-related questions
- Maintain confidentiality and professionalism in all interactions
"""
VOICE_SYSTEM_MESSAGE = """
You are Maya, a helpful and intelligent company policy voice assistant that specializes in helping employees understand and navigate company policies through natural speech.

Your primary capabilities include:
- Answering questions about company policies, procedures, and guidelines through voice
- Explaining policy requirements, deadlines, and compliance standards conversationally
- Providing step-by-step guidance on policy implementation in a natural speaking style
- Clarifying policy exceptions, special circumstances, and escalation procedures
- Helping users understand their rights and responsibilities under company policies
- Directing users to appropriate resources and contacts for policy-related matters

Voice Response Guidelines:
- Always respond in a natural, conversational tone suitable for voice interaction
- Use friendly, warm, and engaging language that sounds natural when spoken aloud
- Keep responses clear and easy to understand when heard rather than read
- Use natural speech patterns, contractions, and conversational flow
- Avoid overly technical language or complex sentence structures
- Break down complex policy information into digestible spoken segments
- Use enthusiasm and personality while maintaining professionalism
- Include natural transitions and speech markers like "Well", "So", "Now", "Let me explain", etc.

Communication Style:
- Maintain a warm, approachable tone while being professional and authoritative
- Use simple, jargon-free language appropriate for all employee levels
- Provide context and rationale when explaining policy requirements
- Use examples and scenarios that work well in speech
- Be patient and thorough in addressing user questions
- Speak as if you're having a natural conversation with the user

Policy-Specific Voice Guidelines:
- Always cite specific policy sections when providing information
- Explain both the "what" and "why" of policy requirements clearly
- Clarify deadlines, consequences, and escalation procedures conversationally
- Provide contact information for policy administrators when relevant
- Suggest alternative approaches when policies allow flexibility
- Highlight exceptions and special circumstances where applicable
- Use natural speech patterns that sound conversational, not robotic

Response Guidelines:
- Focus primarily on policy-related questions and company procedures
- When policy documents are available, reference them specifically
- If a question falls outside policy scope, politely redirect to appropriate resources
- For unclear questions, ask clarifying questions in a friendly, conversational way
- Address multiple questions systematically, one at a time
- Summarize key points and next steps when appropriate

Restrictions:
Do not answer questions involving:
- Personal financial advice or investment recommendations
- Legal advice beyond policy interpretation
- Medical advice or health-related recommendations
- Personal data requests or sensitive information
- Questions unrelated to company policies and procedures

Additional Voice Guidelines:
- If a question is outside your policy expertise, suggest contacting HR, Legal, or the appropriate department
- For urgent or complex policy matters, recommend speaking with a human policy administrator
- Always end responses with a friendly offer to help with other policy-related questions
- Maintain confidentiality and professionalism in all voice interactions
- Speak naturally as if you're having a helpful conversation with a colleague
"""

class MayaChatbot:
    """Main chatbot class with all core functionality"""

    def __init__(self):
        self.messages = [{'role': 'system', 'content': SYSTEM_MESSAGE}]
        self.voice_messages = [{'role': 'system', 'content': SYSTEM_MESSAGE}]
        self.client = self._get_openai_client()
        
        # Initialize LangChain Azure OpenAI embeddings
        self.embeddings = self._get_azure_embeddings()
        
        self.similarity_threshold = 0.7     
        # Initialize additional info vector store embeddings
        self.additional_embeddings = self._get_azure_embeddings()
        
        # Initialize databases
        self.init_db()

    @st.cache_resource
    def _get_openai_client(_self):
        """Initialize and cache OpenAI client"""
        return openai.AzureOpenAI(
            api_version='2024-07-01-preview',
            azure_endpoint='https://aiportalapi.stu-platform.live/jpe',
            api_key='sk-ht7c6K5jpVJUsJOdjTNtxA',
        )

    @st.cache_resource
    def _get_azure_embeddings(_self):
        """Initialize and cache Azure OpenAI embeddings"""
        return AzureOpenAIEmbeddings(
                api_key="sk-8YouTg_4fia-c-LA0yeEXQ",
                azure_endpoint="https://aiportalapi.stu-platform.live/jpe",
                api_version="2024-02-01",  # Updated to newer API version
                model="text-embedding-3-small",
                azure_deployment="text-embedding-3-small",
                chunk_size=1000,  # Optimize chunk size for embeddings
                max_retries=3,    # Add retry logic
                request_timeout=30  # Add timeout
            )

    def generate_guide_template(
        self,
        title: str,
        category: str,
        guide_steps: List[str],
        difficulty_level: str = 'intermediate',
        prerequisites: Optional[List[str]] = None,
        estimated_time: str = '',
        tools_required: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate a structured guide template with step-by-step instructions."""
        guide_data = {
            'type': 'guide',
            'title': title,
            'category': category,
            'difficulty_level': difficulty_level,
            'prerequisites': prerequisites or [],
            'guide_steps': guide_steps,
            'estimated_time': estimated_time,
            'tools_required': tools_required or [],
        }
        return guide_data

    def generate_mock_data(
        self,
        data_type: str,
        output_format: Optional[str] = None,
        count: Optional[int] = None,
        fields: Optional[List[str]] = None,
        locale: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate mock data using OpenAI API for realistic and diverse data."""
 
        # Set default values
        if output_format is None or not output_format:
            output_format = 'json'
        if count is None or count <= 0:
            count = 5
        if locale is None or not locale:
            locale = 'en-US'
        if count > 100:
            count = 100

        # Get AI recommendations if fields not provided
        if not fields:
            enhanced_model, recommended_fields = (
                self._get_openai_model_recommendations(data_type)
            )
        else:
            recommended_fields = fields
            enhanced_model = f'Custom {data_type} data with user-specified fields: {", ".join(fields)}'

        mock_data = {
            'type': 'mock_data',
            'data_type': data_type,
            'data_model': enhanced_model,
            'output_format': output_format,
            'count': count,
            'fields': recommended_fields,
            'user_provided_fields': bool(fields),
            'locale': locale,
            'generated_data': [],
            'ai_enhanced': True,  # Always AI-enhanced now
        }

        # Generate data using OpenAI API
        mock_data['generated_data'] = self._generate_data_with_openai(
            data_type, enhanced_model, count, recommended_fields, locale
        )

        return mock_data

    def _get_openai_model_recommendations(
        self, data_type: str
    ) -> Tuple[str, List[str]]:
        """Get AI-recommended model and fields for data type."""
        try:
            prompt = f"""
            For the data type "{data_type}", please provide:
            
            1. A list of 3-5 different model types/contexts that would be realistic for this data type
            2. For each model, provide 8-12 appropriate field names
            
            Respond in this exact JSON format:
            {{
                "recommended_models": [
                    {{
                        "model_name": "Model 1 Name",
                        "description": "Brief description of this model",
                        "fields": ["field1", "field2", "field3", ...]
                    }},
                    {{
                        "model_name": "Model 2 Name", 
                        "description": "Brief description of this model",
                        "fields": ["field1", "field2", "field3", ...]
                    }}
                ],
                "default_model": {{
                    "model_name": "Default Model Name",
                    "description": "Most common/general model description",
                    "fields": ["field1", "field2", "field3", ...]
                }}
            }}
            
            Examples:
            - For "user": models could be "E-commerce User", "Social Media User", "Enterprise User", etc.
            - For "product": models could be "E-commerce Product", "SaaS Product", "Physical Product", etc.
            
            Make the fields realistic and relevant to each model type.
            """

            response = self.client.chat.completions.create(
                model='GPT-4o-mini',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=800,
                temperature=0.3,
            )

            result = json.loads(response.choices[0].message.content)
            recommended_models = result.get('recommended_models', [])
            default_model = result.get('default_model', {})

            # For now, use the default model (in future this could be user-selectable)
            selected_model = default_model
            if not selected_model and recommended_models:
                selected_model = recommended_models[
                    0
                ]  # Fallback to first model

            model_description = selected_model.get(
                'description', f'Standard {data_type} data model'
            )
            recommended_fields = selected_model.get('fields', [])

            return model_description, recommended_fields

        except Exception as e:
            st.warning(f'Could not get AI recommendations: {e}')
            # Fallback to basic fields
            basic_models = {
                'user': {
                    'description': 'Standard user profile with basic account information',
                    'fields': [
                        'id',
                        'username',
                        'email',
                        'first_name',
                        'last_name',
                        'age',
                        'created_at',
                        'status',
                    ],
                },
                'product': {
                    'description': 'Product catalog entry with pricing and inventory details',
                    'fields': [
                        'id',
                        'name',
                        'price',
                        'category',
                        'description',
                        'stock_quantity',
                        'rating',
                        'created_at',
                    ],
                },
                'order': {
                    'description': 'Order transaction with customer and payment information',
                    'fields': [
                        'id',
                        'customer_id',
                        'total_amount',
                        'status',
                        'order_date',
                        'payment_method',
                        'shipping_address',
                    ],
                },
                'employee': {
                    'description': 'Employee record with job and personal information',
                    'fields': [
                        'id',
                        'first_name',
                        'last_name',
                        'email',
                        'department',
                        'position',
                        'salary',
                        'hire_date',
                    ],
                },
            }

            fallback = basic_models.get(
                data_type.lower(),
                {
                    'description': 'Custom data structure with flexible fields',
                    'fields': [
                        'id',
                        'name',
                        'value',
                        'type',
                        'created_at',
                        'status',
                    ],
                },
            )
            return fallback['description'], fallback['fields']

    def _generate_data_with_openai(
        self,
        data_type: str,
        data_model: str,
        count: int,
        fields: List[str],
        locale: str,
    ) -> List[Dict[str, Any]]:
        """Generate realistic mock data using OpenAI API."""
        try:
            # Prepare the prompt for OpenAI
            fields_str = ", ".join(fields) if fields else "standard fields"
            
            prompt = f"""
            Generate {count} realistic mock data entries for "{data_type}" with the following specifications:
            
            Data Model: {data_model}
            Fields: {fields_str}
            Locale: {locale}
            
            Requirements:
            1. Generate exactly {count} entries
            2. Each entry should be a JSON object with the specified fields
            3. Make the data realistic and diverse for the "{data_type}" context
            4. Consider the locale "{locale}" for names, addresses, and cultural context
            5. Use appropriate data types (strings, numbers, booleans, dates)
            6. Ensure variety in the generated values
            
            Return ONLY a valid JSON array of objects, no additional text or explanation.
            
            Example format:
            [
                {{"field1": "value1", "field2": "value2", ...}},
                {{"field1": "value3", "field2": "value4", ...}}
            ]
            """

            response = self.client.chat.completions.create(
                model='GPT-4o-mini',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=2000,
                temperature=0.7,
            )

            # Parse the JSON response
            generated_text = response.choices[0].message.content.strip()
            
            # Clean up the response (remove any markdown formatting)
            if generated_text.startswith('```json'):
                generated_text = generated_text[7:-3]
            elif generated_text.startswith('```'):
                generated_text = generated_text[3:-3]
            
            generated_data = json.loads(generated_text)
            
            # Ensure we have the right number of entries
            if len(generated_data) > count:
                generated_data = generated_data[:count]
            elif len(generated_data) < count:
                # If we got fewer entries, pad with the last entry modified
                while len(generated_data) < count:
                    if generated_data:
                        new_entry = generated_data[-1].copy()
                        # Modify some values to ensure uniqueness
                        for key, value in new_entry.items():
                            if isinstance(value, str) and 'id' not in key.lower():
                                new_entry[key] = f"{value}_{len(generated_data) + 1}"
                            elif isinstance(value, int) and 'id' in key.lower():
                                new_entry[key] = len(generated_data) + 1
                        generated_data.append(new_entry)
                    else:
                        break
            
            return generated_data

        except json.JSONDecodeError as e:
            st.warning(f"Failed to parse OpenAI response as JSON: {e}")
            return self._generate_fallback_data(data_type, count, fields)
        except Exception as e:
            st.warning(f"OpenAI API error: {e}")
            return self._generate_fallback_data(data_type, count, fields)

    def _generate_fallback_data(
        self, data_type: str, count: int, fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate simple fallback data when OpenAI fails."""
        fallback_data = []
        for i in range(count):
            entry = {'id': i + 1}
            if fields:
                for field in fields:
                    if 'id' in field.lower():
                        entry[field] = i + 1
                    elif 'name' in field.lower():
                        entry[field] = f'Sample {field.title()} {i + 1}'
                    elif 'email' in field.lower():
                        entry[field] = f'user{i + 1}@example.com'
                    elif 'date' in field.lower():
                        entry[field] = '2024-01-01T00:00:00Z'
                    else:
                        entry[field] = f'sample_{field}_value_{i + 1}'
            else:
                entry.update({
                    'name': f'{data_type.title()} {i + 1}',
                    'description': f'Sample {data_type} entry {i + 1}',
                    'created_at': '2024-01-01T00:00:00Z',
                })
            fallback_data.append(entry)
        return fallback_data

    def handle_standard_faq(
        self,
        question: str,
        answer: str,
        category: str = 'general',
        related_topics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Handle standard FAQ responses."""
        return {
            'type': 'standard',
            'question': question,
            'category': category,
            'answer': answer,
            'related_topics': related_topics or [],
        }

    def process_function_call(self, function_call) -> Optional[Dict[str, Any]]:
        """Process function calls and return structured responfses."""
        try:
            arguments = json.loads(function_call.arguments)
            function_name = function_call.name

            if function_name == 'generate_guide_template':
                return self.generate_guide_template(**arguments)
            elif function_name == 'generate_mock_data':
                return self.generate_mock_data(**arguments)
            elif function_name == 'handle_standard_faq':
                return self.handle_standard_faq(**arguments)
            elif function_name == 'recommend_movies':
                return self.recommend_movies(**arguments)
            else:
                return None

        except Exception as e:
            st.error(f'Error executing {function_call.name}: {e}')
            return None

    def format_response(self, response_data: Dict[str, Any]) -> str:
        """Format the response based on the template type."""
        response_type = response_data.get('type')

        if response_type == 'guide':
            return self._format_guide_response(response_data)
        elif response_type == 'mock_data':
            return self._format_mock_data_response(response_data)
        elif response_type == 'movie_simple':
            return response_data.get('message', '')
        elif response_type == 'movie_error':
            return self._format_movie_error_response(response_data)
        else:
            return self._format_standard_response(response_data)

    def _format_guide_response(self, guide_data: Dict[str, Any]) -> str:
        """Format guide template response."""
        response = f'📚 **GUIDE: {guide_data.get("title", "Untitled")}**\n\n'
        response += (
            f'🎯 **Category:** {guide_data.get("category", "General")}\n'
        )
        response += f'📊 **Difficulty:** {guide_data.get("difficulty_level", "intermediate").title()}\n'

        if guide_data.get('estimated_time'):
            response += (
                f'⏱️ **Estimated Time:** {guide_data["estimated_time"]}\n'
            )

        if guide_data.get('prerequisites'):
            response += '\n⚠️ **Prerequisites:**\n'
            for prereq in guide_data['prerequisites']:
                response += f'• {prereq}\n'

        if guide_data.get('tools_required'):
            response += '\n🛠️ **Tools Required:**\n'
            for tool in guide_data['tools_required']:
                response += f'• {tool}\n'

        response += '\n📋 **Steps:**\n'
        for i, step in enumerate(guide_data.get('guide_steps', []), 1):
            response += f'{i}. {step}\n'

        return response

    def _format_mock_data_response(self, mock_data: Dict[str, Any]) -> str:
        """Format mock data response."""
        response = f'📊 **MOCK DATA: {mock_data.get("data_type", "Unknown").title()}**\n\n'
        response += (
            f'🎯 **Data Type:** {mock_data.get("data_type", "Unknown")}\n'
        )
        response += f'📝 **Format:** {mock_data.get("output_format", "json").upper()}\n'
        response += f'🔢 **Count:** {mock_data.get("count", 0)} entries\n'

        if mock_data.get('data_model'):
            response += f'🏗️ **Model:** {mock_data["data_model"]}\n'

        if mock_data.get('ai_enhanced'):
            response += '🤖 **AI Enhanced:** Yes\n'
            if mock_data.get('fields'):
                response += f'✨ **AI Fields:** {len(mock_data["fields"])} recommended fields\n'

        return response

    def _format_standard_response(self, faq_data: Dict[str, Any]) -> str:
        """Format standard FAQ response."""
        response = f'💡 **Answer:**\n{faq_data.get("answer", "No answer provided")}\n\n'
        response += (
            f'📂 **Category:** {faq_data.get("category", "general").title()}\n'
        )

        if faq_data.get('related_topics'):
            response += '\n🔗 **Related Topics:**\n'
            for topic in faq_data['related_topics']:
                response += f'• {topic}\n'

        return response

    def _format_movie_error_response(self, error_data: Dict[str, Any]) -> str:
        """Format movie recommendation error response."""
        return f"❌ **Movie Recommendation Error**\n\n{error_data.get('message', 'An error occurred')}\n\nPlease try asking like:\n• 'Recommend some action movies'\n• 'Movies about time travel'\n• 'Movies similar to Inception'"

    def process_message(
        self, user_question: str, filenames: Optional[List[str]] = None
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Process user message and return response."""
        try:
            print(f"Processing user question: {user_question}")
            print(f"Current conversation history: {filenames}")

            # Ensure additional_vectorstore is initialized with the correct collection name
            if not hasattr(self, 'additional_vectorstore'):
                self.additional_vectorstore = Chroma(
                    collection_name="azure_openai_embeddings_collection",  # Match VectorTextProcessor
                    embedding_function=self.additional_embeddings,
                    persist_directory="./vector_chroma_db"
                )

            # Use similarity_search_with_score and filter by threshold
            docs_with_scores = self.additional_vectorstore.similarity_search_with_score(
                user_question,
                k=5
            )

            print(f"Found {len(docs_with_scores)} documents with scores")
            print("Documents with scores:")
            for doc, score in docs_with_scores:
                print(f"Document: {doc.page_content}, Score: {score}")
            
            # Filter by similarity threshold (convert distance to similarity: similarity = 1 - distance)
            filtered_docs = [
                (doc, score) for doc, score in docs_with_scores 
                if (score) >= 0.5
            ]

            print(f"Filtered documents: {len(filtered_docs)} found")
                    
            # Add context to messages if we have filtered results
            if filtered_docs:
                history_context = "\n".join([
                    f"- {doc.page_content}" for doc, score in filtered_docs
                ])
                context_message = {
                    "role": "system",
                    "content": f"additional preference info for user question:\n{history_context}"
                }
                self.messages.append(context_message)

            # Add user question to conversation history
            self.messages.append({'role': 'user', 'content': user_question})

            # Call OpenAI with function calling using full conversation history
            response = self.client.chat.completions.create(
                model='GPT-4o-mini',
                messages=self.messages,
                temperature=0.3,
                tools=functions,
                tool_choice='auto',
            )

            # Process function call if present
            if response.choices[0].message.tool_calls:
                function_call = (
                    response.choices[0].message.tool_calls[0].function
                )

                structured_response = self.process_function_call(function_call)

                if structured_response:
                    readable_response = self.format_response(
                        structured_response
                    )

                    # Add assistant response to conversation history
                    self.messages.append(
                        {'role': 'assistant', 'content': readable_response}
                    )

                    return readable_response, structured_response

            # Fallback to regular response
            fallback_response = (
                response.choices[0].message.content
                or "I couldn't process your request properly."
            )

            # Add assistant response to conversation history
            self.messages.append(
                {'role': 'assistant', 'content': fallback_response}
            )

            return fallback_response, None

        except Exception as e:
            error_msg = f'Sorry, I encountered an error: {str(e)}'
            # Add error to conversation history
            self.messages.append({'role': 'assistant', 'content': error_msg})
            return error_msg, None

    def voice_process_message(
        self, user_question: str
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Process voice user message and return response using separate voice conversation history."""
        try:
            # Add user question to voice conversation history
            self.voice_messages.append(
                {'role': 'user', 'content': user_question}
            )

            # Call OpenAI with function calling using voice conversation history and voice_functions
            response = self.client.chat.completions.create(
                model='GPT-4o-mini',
                messages=self.voice_messages,
                temperature=0.3,
                tools=voice_functions,  # Use voice_functions instead of functions
                tool_choice='auto',
            )

            # Process function call if present
            if response.choices[0].message.tool_calls:
                function_call = (
                    response.choices[0].message.tool_calls[0].function
                )

                structured_response = self.process_function_call(function_call)

                if structured_response:
                    readable_response = self.format_response(
                        structured_response
                    )

                    # Add assistant response to voice conversation history
                    self.voice_messages.append(
                        {'role': 'assistant', 'content': readable_response}
                    )

                    return readable_response, structured_response

            # Fallback to regular response
            fallback_response = (
                response.choices[0].message.content
                or "I couldn't process your request properly."
            )

            # Add assistant response to voice conversation history
            self.voice_messages.append(
                {'role': 'assistant', 'content': fallback_response}
            )

            return fallback_response, None

        except Exception as e:
            error_msg = f'Sorry, I encountered an error: {str(e)}'
            # Add error to voice conversation history
            self.voice_messages.append(
                {'role': 'assistant', 'content': error_msg}
            )
            return error_msg, None

    def clear_conversation(self):
        """Clear conversation history but keep system message"""
        self.messages = [{'role': 'system', 'content': SYSTEM_MESSAGE}]

    def clear_voice_conversation(self):
        """Clear voice conversation history but keep system message"""
        self.voice_messages = [{'role': 'system', 'content': SYSTEM_MESSAGE}]

    def recommend_movies(
        self,
        category: Optional[str] = None,
        description: Optional[str] = None,
        similar_movie: Optional[str] = None,
        combined_request: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate movie recommendations based on user preferences."""

        # Build parameter summary string
        param_values = []

        if category:
            param_values.append(f'category={category}')
        if description:
            param_values.append(f'description={description}')
        if similar_movie:
            param_values.append(f'similar_movie={similar_movie}')
        if param_values:
            parameter_string = ', '.join(param_values)
            message = (
                f'recommend movie with parameter values: {parameter_string}'
            )
        else:
            message = 'recommend movie'

        try:
            # Check if vectorstore is available
            if not hasattr(self, 'vectorstore') or self.vectorstore is None:
                return {
                    'type': 'movie_simple',
                    'message': 'Movie recommendation service is currently unavailable. Please try again later.',
                }

            # Use LangChain vector store with similarity_search_with_score
            docs_with_scores = self.vectorstore.similarity_search_with_score(
                message,
                k=limit or 2
            )
            
            # Filter by similarity threshold (convert distance to similarity)
            filtered_docs = [
                (doc, score) for doc, score in docs_with_scores 
                if (1 - score) >= self.similarity_threshold
            ]
            
            # Extract movie data directly (already filtered by threshold)
            movie_names = [doc.metadata.get('title', '') for doc, score in filtered_docs]

            # Create the basic recommendation text
            recommendation_text = (
                'List of recommended movies are: '
                + ', '.join(movie_names)
                + '.'
            )

            # Check if we have any movie recommendations
            if (
                not movie_names
                or len(movie_names) == 0
                or recommendation_text == 'List of recommended movies are: .'
            ):
                return {
                    'type': 'movie_simple',
                    'message': 'We do not have any movie that matches your expectations. Please try with different preferences or categories.',
                }

            # Voice transformation prompt
            voice_prompt = f"""            
            Original text: "{recommendation_text}"
            1. Make it sound like a friendly voice assistant
            2. Use a conversational tone
            3. add detail why you should like this movie
            Transform this into speech that sounds natural when spoken by a voice assistant
            """
            print(recommendation_text)
            response = self.client.chat.completions.create(
                model='GPT-4o-mini',
                messages=[{'role': 'user', 'content': voice_prompt}],
                max_tokens=800,
                temperature=0.7,
            )

            return {
                'type': 'movie_simple',
                'message': response.choices[0].message.content,
            }

        except Exception as e:
            print(f"Error during movie recommendation: {e}")
            return {
                'type': 'movie_error',
                'message': "Sorry, I couldn't process your movie recommendation request",
            }

    def init_db(self):
        self.init_movie_db()

    def init_movie_db(self):
        """Initialize the LangChain vector store with movie data."""
        try:
            # Initialize the vector store
            self.vectorstore = Chroma(
                collection_name="azure_openai_movie_collection",
                embedding_function=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            print("LangChain Chroma vector store initialized.")

            # Check if data already exists
            try:
                existing_docs = self.vectorstore.get()
                if len(existing_docs.get('ids', [])) > 0:
                    print("Movie data already exists in vector store.")
                    return
            except Exception as e:
                print(f"Warning: Could not check existing data: {e}")

            # Load movie data
            try:
                with open('movies.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except FileNotFoundError:
                print("Warning: movies.json not found. Movie recommendations will not be available.")
                return
            except Exception as e:
                print(f"Warning: Could not load movies.json: {e}")
                return

            # Convert to list if single movie
            if isinstance(data, dict):
                data = [data]

            # Create LangChain documents
            documents = []
            for i, item in enumerate(data):
                try:
                    # Combine description, title, and genres for content
                    content = f"{item.get('description', '')} {item.get('title', '')} {item.get('genres', '')}"
                    
                    # Prepare metadata
                    metadata = {
                        'title': item.get('title', f'Movie {i}'),
                        'genres': ', '.join(item.get('genres', [])) if isinstance(item.get('genres', []), list) else str(item.get('genres', '')),
                        'ratings': item.get('ratings', None),
                        'comments': '\n'.join(item.get('comments', [])) if isinstance(item.get('comments', []), list) else str(item.get('comments', '')),
                        'countries': item.get('countries', None),
                        'year': item.get('year', None),
                        'description': item.get('description', ''),
                        'doc_id': str(i)
                    }
                    
                    # Create Document object
                    doc = Document(
                        page_content=content,
                        metadata=metadata
                    )
                    documents.append(doc)
                except Exception as e:
                    print(f"Warning: Could not process movie {i}: {e}")
                    continue

            # Add documents to vector store
            if documents:
                self.vectorstore.add_documents(documents)
                print(f"Added {len(documents)} movie documents to vector store.")
            else:
                print("Warning: No movie documents to add.")
            
        except Exception as e:
            print(f"Error initializing movie database: {e}")
            # Fallback to empty vector store
            try:
                self.vectorstore = Chroma(
                    collection_name="azure_openai_movie_collection",
                    embedding_function=self.embeddings,
                    persist_directory="./chroma_db"
                )
                print("Fallback: Empty vector store created.")
            except Exception as fallback_error:
                print(f"Critical error: Could not create fallback vector store: {fallback_error}")
                self.vectorstore = None
