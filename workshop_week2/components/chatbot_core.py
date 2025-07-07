"""
Core Chatbot Logic for Maya
Contains the main chatbot class and processing functions
"""

import json
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import chromadb
import openai
import streamlit as st
from sentence_transformers import SentenceTransformer

# Define function schemas for different template types
functions = [
    {
        'type': 'function',
        'function': {
            'name': 'generate_guide_template',
            'description': "Creates step-by-step instructions and tutorials ONLY when users explicitly ask for procedural help or instructions. Must contain clear action-oriented language like 'how to', 'steps to', 'guide me through', 'tutorial for', 'instructions to', 'walk me through', 'teach me to', 'show me how', 'create a guide', 'make a tutorial'. NEVER use for: reviews, opinions, explanations, 'what is', 'tell me about', 'explain', 'describe', 'compare', 'review of', 'thoughts on', career advice, or general informational questions.",
            'parameters': {
                'type': 'object',
                'properties': {
                    'title': {
                        'type': 'string',
                        'description': 'Title of the guide',
                    },
                    'category': {
                        'type': 'string',
                        'description': 'Category of the guide',
                    },
                    'difficulty_level': {
                        'type': 'string',
                        'enum': ['beginner', 'intermediate', 'advanced'],
                    },
                    'prerequisites': {
                        'type': 'array',
                        'items': {'type': 'string'},
                    },
                    'guide_steps': {
                        'type': 'array',
                        'items': {'type': 'string'},
                    },
                    'estimated_time': {
                        'type': 'string',
                        'description': 'Estimated time to complete',
                    },
                    'tools_required': {
                        'type': 'array',
                        'items': {'type': 'string'},
                    },
                },
                'required': ['title', 'category', 'guide_steps'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'generate_mock_data',
            'description': 'Generates sample, test, or mock data when users request data examples, want to create fake data, need sample datasets, or ask for data generation. Automatically triggered by questions containing words like: mock data, sample data, generate data, test data, fake data, dummy data, create data, data examples, sample users, example products. Only include optional parameters if the user specifically requests them.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'data_type': {
                        'type': 'string',
                        'description': "Type of data to generate (e.g., 'user', 'product', 'order', 'employee', 'custom'). Extract this from the user's request context.",
                    },
                    'output_format': {
                        'type': 'string',
                        'enum': ['json', 'csv', 'xml', 'sql', 'yaml', 'table'],
                        'description': 'Output format for the mock data. Only include if user specifically requests a format, otherwise omit to use default (json).',
                    },
                    'count': {
                        'type': 'integer',
                        'minimum': 1,
                        'maximum': 100,
                        'description': 'Number of mock data entries to generate. Only include if user specifies a number, otherwise omit to use default (5).',
                    },
                    'locale': {
                        'type': 'string',
                        'description': "Locale for data generation (e.g., 'en-US', 'vi-VN'). Only include if user mentions a specific locale or language preference.",
                    },
                    'fields': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': "Specific field names to include in the generated data (e.g., ['username', 'email']). Only include if user explicitly lists specific fields they want, otherwise omit to get AI-recommended fields.",
                    },
                },
                'required': ['data_type'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'handle_standard_faq',
            'description': "Handles general questions, provides information, answers FAQs, gives explanations, opinions, reviews, definitions, comparisons, and discussions. Use for ALL questions about careers, roles, technologies, concepts, reviews, opinions, descriptions, definitions. Triggered by: 'what is', 'tell me about', 'explain', 'describe', 'compare', 'review of', 'thoughts on', 'opinion about', career questions, informational queries, and any non-procedural questions that don't require step-by-step instructions.",
            'parameters': {
                'type': 'object',
                'properties': {
                    'question': {
                        'type': 'string',
                        'description': "The user's question",
                    },
                    'category': {
                        'type': 'string',
                        'description': 'Category of the question',
                    },
                    'answer': {
                        'type': 'string',
                        'description': 'The main answer to the question',
                    },
                    'related_topics': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Related topics or questions',
                    },
                },
                'required': ['question', 'answer'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'recommend_movies',
            'description': "Provides movie recommendations based on user preferences. Use when users ask for movie suggestions, recommendations by genre/category, or movies similar to a description they provide. Triggered by phrases like: 'recommend movies', 'suggest films', 'what movies should I watch', 'movies like', 'good [genre] movies', 'films about', 'movie recommendations', 'recommend action movie', 'suggest comedy films'. Can extract genre from natural language.",
            'parameters': {
                'type': 'object',
                'properties': {
                    'category': {
                        'type': 'string',
                        'description': "Movie genre/category (e.g., 'action', 'comedy', 'drama', 'horror', 'sci-fi', 'romance', 'thriller', 'animated'). Extract from user query if mentioned (e.g., 'action movie' -> 'action').",
                    },
                    'description': {
                        'type': 'string',
                        'description': "Full user query or description of what kind of movie they want. Include the complete user request for natural language processing (e.g., 'recommend action movie', 'movies about time travel', 'films with strong female leads').",
                    },
                    'similar_movie': {
                        'type': 'string',
                        'description': 'Name of a movie the user wants recommendations similar to. Only include if user mentions a specific movie.',
                    },
                    'limit': {
                        'type': 'integer',
                        'minimum': 1,
                        'maximum': 20,
                        'description': "Maximum number of movie recommendations to return. Only include if user specifies a number (e.g., 'recommend 5 movies', 'give me 3 films'). Default is 5 if not specified.",
                    },
                },
            },
        },
    },
]

# System message
SYSTEM_MESSAGE = """
You are Maya, a helpful and intelligent virtual assistant that can assist users with various tasks.

Your capabilities include:
- Answering general questions and providing information
- Creating step-by-step guides and tutorials 
- Generating sample data and examples

Always be friendly, helpful, and provide accurate information. Respond naturally to user requests without mentioning specific functions or technical details about how you process requests.

Keep responses conversational and focus on helping the user achieve their goals.
Use simple and easy-to-understand language.
Stay on-topic and only answer questions related to supported FAQ content.
Summarize or clarify when users seem confused.
Avoid excessive repetition or unnecessary explanations unless asked.
If there are multiple questions, address them one at a time.
If a question is unclear, ask for clarification before answering.

Restrictions:
Do not answer questions involving:
Real-life investments or financial speculation
Money-making or "get rich quick" schemes
Criminal activities or unlawful steps
Personal data requests or sensitive/private information
Reason: Answering such questions would violate our privacy policy and ethical guidelines.

Additional Guidelines:
If unsure or if the question falls outside the FAQ scope, politely let the user know and suggest contacting a human support agent.
You can say: "I'm not able to answer that, but you can reach out to our support team for further help."
Always close the conversation with an offer to help with anything else.
"""
VOICE_SYSTEM_MESSAGE = """
You are Maya, a helpful and intelligent virtual voice assistant that can assist users with various tasks.

Your capabilities include:
- Answering general questions and providing information through natural speech
- Creating step-by-step guides and tutorials in conversational voice format
- Generating sample data and examples with voice-friendly explanations
- Recommending movies with enthusiastic and natural voice responses

Voice Response Guidelines:
Always respond in a natural, conversational tone suitable for voice interaction.
Use friendly, warm, and engaging language that sounds natural when spoken aloud.
Keep responses clear and easy to understand when heard rather than read.
Use natural speech patterns, contractions, and conversational flow.
Avoid overly technical language or complex sentence structures.
Break down information into digestible spoken segments.
Use enthusiasm and personality in your voice responses.
Include natural transitions and speech markers like "Well", "So", "Now", etc.

Keep responses conversational and focus on helping the user achieve their goals through voice interaction.
Use simple, spoken language that flows naturally.
Stay on-topic and provide voice-optimized responses.
When explaining complex topics, use analogies and examples that work well in speech.
If there are multiple points, present them in a natural speaking rhythm.
If a question is unclear, ask for clarification in a friendly, conversational way.

Restrictions:
Do not answer questions involving:
Real-life investments or financial speculation
Money-making or "get rich quick" schemes
Criminal activities or unlawful steps
Personal data requests or sensitive/private information
Reason: Answering such questions would violate our privacy policy and ethical guidelines.

Additional Voice Guidelines:
If unsure or if the question falls outside your capabilities, politely let the user know in a conversational way.
You can say: "I'm not able to help with that, but you can reach out to our support team for more assistance."
Always end responses with a friendly offer to help with anything else.
Speak as if you're having a natural conversation with the user.
"""

voice_functions = [
    {
        'type': 'function',
        'function': {
            'name': 'recommend_movies',
            'description': "Provides movie recommendations based on user preferences. Use when users ask for movie suggestions, recommendations by genre/category, or movies similar to a description they provide. Triggered by phrases like: 'recommend movies', 'suggest films', 'what movies should I watch', 'movies like', 'good [genre] movies', 'films about', 'movie recommendations', 'recommend action movie', 'suggest comedy films'. Can extract genre from natural language.",
            'parameters': {
                'type': 'object',
                'properties': {
                    'category': {
                        'type': 'string',
                        'description': "Movie genre/category (e.g., 'action', 'comedy', 'drama', 'horror', 'sci-fi', 'romance', 'thriller', 'animated'). Extract from user query if mentioned (e.g., 'action movie' -> 'action').",
                    },
                    'description': {
                        'type': 'string',
                        'description': "Full user query or description of what kind of movie they want. Include the complete user request for natural language processing (e.g., 'recommend action movie', 'movies about time travel', 'films with strong female leads').",
                    },
                    'similar_movie': {
                        'type': 'string',
                        'description': 'Name of a movie the user wants recommendations similar to. Only include if user mentions a specific movie.',
                    },
                    'combined_request': {
                        'type': 'string',
                        'description': "If user provides multiple criteria, combine them in format 'description:{description}, category:{category}, similar:{similar_movie}'. Only include if multiple criteria are provided.",
                    },
                    'limit': {
                        'type': 'integer',
                        'minimum': 1,
                        'maximum': 20,
                        'description': "Maximum number of movie recommendations to return. Only include if user specifies a number (e.g., 'recommend 5 movies', 'give me 3 films'). Default is 5 if not specified.",
                    },
                },
            },
        },
    }
]


class MayaChatbot:
    """Main chatbot class with all core functionality"""

    def __init__(self):
        self.messages = [{'role': 'system', 'content': SYSTEM_MESSAGE}]
        self.voice_messages = [{'role': 'system', 'content': SYSTEM_MESSAGE}]
        self.client = self._get_openai_client()
        self.db_client = chromadb.PersistentClient(path='./chroma_db')
        self.init_db()

    @st.cache_resource
    def _get_openai_client(_self):
        """Initialize and cache OpenAI client"""
        return openai.AzureOpenAI(
            api_version='2024-07-01-preview',
            azure_endpoint='https://aiportalapi.stu-platform.live/jpe',
            api_key='sk-ht7c6K5jpVJUsJOdjTNtxA',
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
        """Generate mock data with specified parameters and format options."""

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
            'ai_enhanced': bool(recommended_fields) and not bool(fields),
        }

        # Generate data
        mock_data['generated_data'] = self._generate_data_by_type(
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

    def _generate_data_by_type(
        self,
        data_type: str,
        data_model: str,
        count: int,
        fields: List[str],
        locale: str,
    ) -> List[Dict[str, Any]]:
        """Generate data based on type and model."""
        # Always prefer AI-enhanced generation when fields are available
        if fields and len(fields) > 0:
            return self._generate_enhanced_data_with_fields(
                data_type, data_model, count, fields, locale
            )

        # Fallback to standard generators only if no AI fields are available
        data_generators = {
            'user': self._generate_user_data,
            'product': self._generate_basic_product_data,
            'order': lambda count,
            model,
            fields,
            locale: self._generate_custom_data(count, fields),
            'employee': lambda count,
            model,
            fields,
            locale: self._generate_custom_data(count, fields),
            'custom': lambda count,
            model,
            fields,
            locale: self._generate_custom_data(count, fields),
        }

        generator = data_generators.get(data_type.lower())
        if generator:
            if data_type.lower() == 'user':
                return generator(count, data_model, fields, locale)
            else:
                return generator(count, data_model, fields, locale)
        else:
            return self._generate_custom_data(count, fields)

    def _generate_enhanced_data_with_fields(
        self,
        data_type: str,
        data_model: str,
        count: int,
        fields: List[str],
        locale: str,
    ) -> List[Dict[str, Any]]:
        """Generate enhanced data using AI-recommended fields."""

        # Sample data pools for different field types
        sample_data = {
            # Names and identity
            'name': [
                'John Smith',
                'Jane Doe',
                'Mike Johnson',
                'Sarah Wilson',
                'David Brown',
            ],
            'first_name': [
                'John',
                'Jane',
                'Mike',
                'Sarah',
                'David',
                'Emily',
                'Chris',
                'Lisa',
            ],
            'last_name': [
                'Smith',
                'Johnson',
                'Williams',
                'Brown',
                'Jones',
                'Garcia',
                'Miller',
            ],
            'username': [
                'john_smith',
                'jane_doe',
                'mike_j',
                'sarah_w',
                'david_b',
                'emily_c',
                'chris_l',
                'lisa_m',
            ],
            'loginname': [
                'john.smith',
                'jane.doe',
                'mike.johnson',
                'sarah.wilson',
                'david.brown',
            ],
            'email': [
                'user@example.com',
                'test@gmail.com',
                'sample@yahoo.com',
            ],
            # Authentication and security
            'password': [
                'SecurePass123!',
                'MyPassword2024',
                'StrongPwd@456',
                'UserPass789#',
                'SafeLogin2024!',
            ],
            # Business and commerce
            'title': [
                'Software Engineer',
                'Product Manager',
                'Designer',
                'Analyst',
                'Director',
            ],
            'company': [
                'TechCorp',
                'DataSoft',
                'WebSolutions',
                'AppDev Inc',
                'Digital Pro',
            ],
            'department': [
                'Engineering',
                'Marketing',
                'Sales',
                'HR',
                'Finance',
            ],
            'category': ['Electronics', 'Clothing', 'Books', 'Home', 'Sports'],
            'brand': [
                'Brand A',
                'Brand B',
                'Premium Co',
                'Quality Ltd',
                'Best Corp',
            ],
            'status': [
                'active',
                'inactive',
                'pending',
                'completed',
                'cancelled',
            ],
            # Location
            'country': [
                'United States',
                'Canada',
                'United Kingdom',
                'Germany',
                'France',
            ],
            'city': [
                'New York',
                'Los Angeles',
                'Chicago',
                'Houston',
                'Phoenix',
            ],
            'address': [
                '123 Main St',
                '456 Oak Ave',
                '789 Pine Rd',
                '321 Elm St',
            ],
            # Technical
            'platform': ['web', 'mobile', 'desktop', 'api', 'cloud'],
            'technology': ['Python', 'JavaScript', 'Java', 'React', 'Node.js'],
            'version': ['1.0.0', '2.1.3', '3.2.1', '4.0.0', '5.1.2'],
        }

        generated_data = []

        for i in range(count):
            entry = {'id': i + 1}

            for field in fields:
                field_lower = field.lower()

                # Generate appropriate data based on field name patterns
                if any(
                    keyword in field_lower
                    for keyword in ['id', 'number', 'count', 'quantity']
                ):
                    entry[field] = random.randint(1, 10000)

                elif any(
                    keyword in field_lower
                    for keyword in [
                        'price',
                        'cost',
                        'amount',
                        'salary',
                        'revenue',
                    ]
                ):
                    entry[field] = round(random.uniform(10.99, 9999.99), 2)

                elif any(
                    keyword in field_lower
                    for keyword in ['date', 'time', 'created', 'updated']
                ):
                    base_date = datetime(2024, 1, 1)
                    random_days = random.randint(0, 365)
                    entry[field] = (
                        base_date + timedelta(days=random_days)
                    ).isoformat()

                elif any(
                    keyword in field_lower for keyword in ['email', 'mail']
                ):
                    domains = [
                        'gmail.com',
                        'yahoo.com',
                        'example.com',
                        'company.com',
                    ]
                    usernames = [
                        'john.smith',
                        'jane.doe',
                        'mike.johnson',
                        'sarah.wilson',
                        'david.brown',
                    ]
                    entry[field] = (
                        f'{random.choice(usernames).replace(".", "")}@{random.choice(domains)}'
                    )

                elif any(
                    keyword in field_lower
                    for keyword in ['username', 'user_name', 'login']
                ):
                    base_usernames = [
                        'john_smith',
                        'jane_doe',
                        'mike_j',
                        'sarah_w',
                        'david_b',
                        'emily_c',
                    ]
                    entry[field] = (
                        f'{random.choice(base_usernames)}{random.randint(1, 999)}'
                    )

                elif any(
                    keyword in field_lower
                    for keyword in ['loginname', 'login_name']
                ):
                    base_logins = [
                        'john.smith',
                        'jane.doe',
                        'mike.johnson',
                        'sarah.wilson',
                        'david.brown',
                    ]
                    entry[field] = (
                        f'{random.choice(base_logins)}{random.randint(10, 99)}'
                    )

                elif any(
                    keyword in field_lower
                    for keyword in ['password', 'pwd', 'pass']
                ):
                    passwords = [
                        'SecurePass123!',
                        'MyPassword2024',
                        'StrongPwd@456',
                        'UserPass789#',
                        'SafeLogin2024!',
                    ]
                    entry[field] = random.choice(passwords)

                elif any(
                    keyword in field_lower
                    for keyword in ['phone', 'mobile', 'tel']
                ):
                    entry[field] = (
                        f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}'
                    )

                elif any(
                    keyword in field_lower
                    for keyword in ['url', 'website', 'link']
                ):
                    entry[field] = (
                        f'https://example{random.randint(1, 100)}.com'
                    )

                elif any(
                    keyword in field_lower
                    for keyword in [
                        'bool',
                        'is_',
                        'has_',
                        'can_',
                        'verified',
                        'active',
                    ]
                ):
                    entry[field] = random.choice([True, False])

                elif any(
                    keyword in field_lower
                    for keyword in ['rating', 'score', 'rank']
                ):
                    entry[field] = round(random.uniform(1.0, 5.0), 1)

                else:
                    # Try to match field name with sample data
                    matched_samples = None
                    for key, samples in sample_data.items():
                        if key in field_lower or field_lower in key:
                            matched_samples = samples
                            break

                    if matched_samples:
                        if field_lower in ['username', 'loginname']:
                            # Add random number to make usernames unique
                            base_value = random.choice(matched_samples)
                            entry[field] = (
                                f'{base_value}{random.randint(1, 999)}'
                            )
                        else:
                            entry[field] = random.choice(matched_samples)
                    else:
                        # Generate generic field value based on field name patterns
                        if field_lower in ['username', 'user_name']:
                            entry[field] = f'user_{i + 1}'
                        elif field_lower in ['loginname', 'login_name']:
                            entry[field] = f'user.{i + 1}'
                        elif 'password' in field_lower:
                            entry[field] = 'password123'
                        elif 'email' in field_lower:
                            entry[field] = f'user{i + 1}@example.com'
                        else:
                            entry[field] = f'sample_{field}_value_{i + 1}'

            generated_data.append(entry)

        return generated_data

    def _generate_basic_user_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate basic user data."""
        first_names = [
            'John',
            'Jane',
            'Mike',
            'Sarah',
            'David',
            'Emily',
            'Chris',
            'Lisa',
            'Tom',
            'Anna',
        ]
        last_names = [
            'Smith',
            'Johnson',
            'Williams',
            'Brown',
            'Jones',
            'Garcia',
            'Miller',
            'Davis',
        ]
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'example.com']

        users = []
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            users.append(
                {
                    'id': i + 1,
                    'username': f'{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}',
                    'email': f'{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}',
                    'first_name': first_name,
                    'last_name': last_name,
                    'age': random.randint(18, 65),
                    'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    'status': random.choice(['active', 'inactive', 'pending']),
                    'created_at': '2024-01-01T00:00:00Z',
                }
            )
        return users

    def _generate_basic_product_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate basic product data."""
        categories = [
            'Electronics',
            'Clothing',
            'Books',
            'Home & Garden',
            'Sports',
        ]
        brands = ['TechCorp', 'StyleCo', 'ReadMore', 'HomeBasics', 'SportsPro']

        products = []
        for i in range(count):
            category = random.choice(categories)
            products.append(
                {
                    'product_id': i + 1,
                    'name': f'Product {i + 1}',
                    'category': category,
                    'brand': random.choice(brands),
                    'price': round(random.uniform(10.99, 999.99), 2),
                    'description': f'High quality product in {category.lower()} category',
                    'stock_quantity': random.randint(0, 100),
                    'rating': round(random.uniform(3.0, 5.0), 1),
                    'created_at': '2024-01-01T00:00:00Z',
                }
            )
        return products

    def _generate_custom_data(
        self, count: int, fields: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Generate custom data."""
        custom_data = []
        for i in range(count):
            entry = {'id': i + 1}
            if fields:
                for field in fields:
                    entry[field] = f'sample_{field}_value_{i + 1}'
            else:
                entry.update(
                    {
                        'name': f'Item {i + 1}',
                        'description': f'Description for item {i + 1}',
                        'value': f'Value_{i + 1}',
                        'created_at': '2024-01-01T00:00:00Z',
                    }
                )
            custom_data.append(entry)
        return custom_data

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
        """Process function calls and return structured responses."""
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
        self, user_question: str
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Process user message and return response."""
        try:
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
            # Use the original collection query approach
            result = self.collection.query(
                query_texts=[message], n_results=limit or 2
            )
            print(f"Query result: {result}")
            movie_names = [
                metadata['title'] for metadata in result['metadatas'][0]
            ]

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
        """Initialize the ChromaDB database."""
        self.collection = self.db_client.get_or_create_collection(
            name='my_movie_collection'
        )
        print("ChromaDB collection initialized.")

        existing_data = self.collection.get()
        if len(existing_data["ids"]) > 0:
            return

        with open('dmovies.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Nếu chỉ có 1 phim, chuyển thành list
        if isinstance(data, dict):
            data = [data]

        titles = [item['title'] for item in data]
        genres_list = [item['genres'] for item in data]
        descriptions = [item['description'] for item in data]
        ratings = [item.get('ratings', None) for item in data]
        comments = [item.get('comments', []) for item in data]
        countries = [item.get('countries', None) for item in data]
        years = [item.get('year', None) for item in data]
        labels = [1] * len(
            titles
        )  # Gán nhãn Positive, hoặc tự xử lý nếu có trường label

        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(descriptions)

        self.collection.add(
            documents=f'{descriptions}, name: {titles}',
            embeddings=embeddings,
            ids=[str(i) for i in range(len(descriptions))],
            metadatas=[
                {
                    'title': titles[i],
                    'genres': ', '.join(genres_list[i])
                    if isinstance(genres_list[i], list)
                    else str(genres_list[i]),
                    'label': labels[i],
                    'ratings': ratings[i],
                    'comments': '\n'.join(comments[i])
                    if isinstance(comments[i], list)
                    else str(comments[i]),
                    'countries': countries[i],
                    'year': years[i],
                    'description': descriptions[i],
                }
                for i in range(len(descriptions))
            ],
        )
