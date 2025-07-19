"""
Function Constants for Maya Chatbot
Contains all function schemas for different template types
"""

# Function schema for guide template generation
GENERATE_GUIDE_TEMPLATE_FUNCTION = {
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
}

# Function schema for mock data generation
GENERATE_MOCK_DATA_FUNCTION = {
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
}

# Function schema for standard FAQ handling
HANDLE_STANDARD_FAQ_FUNCTION = {
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
}

# Function schema for movie recommendations
RECOMMEND_MOVIES_FUNCTION = {
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
}

# Function schema for voice movie recommendations
VOICE_RECOMMEND_MOVIES_FUNCTION = {
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

# Combine all functions for regular chat
functions = [
    GENERATE_GUIDE_TEMPLATE_FUNCTION,
    GENERATE_MOCK_DATA_FUNCTION,
    HANDLE_STANDARD_FAQ_FUNCTION,
    RECOMMEND_MOVIES_FUNCTION,
]

# Functions for voice interface
voice_functions = [
    VOICE_RECOMMEND_MOVIES_FUNCTION,
]
