"""
LangGraph Tools for Maya Chatbot
Replaces the function-based tool system with LangGraph tools
"""

import json
import random
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field


class GuideTemplate(BaseModel):
    """Model for guide template generation"""
    title: str = Field(description="Title of the guide")
    category: str = Field(description="Category of the guide")
    difficulty_level: str = Field(description="Difficulty level", default="beginner")
    prerequisites: List[str] = Field(description="Prerequisites", default_factory=list)
    guide_steps: List[str] = Field(description="Guide steps")
    estimated_time: str = Field(description="Estimated time", default="30 minutes")
    tools_required: List[str] = Field(description="Tools required", default_factory=list)


class MockDataRequest(BaseModel):
    """Model for mock data generation"""
    data_type: str = Field(description="Type of data to generate")
    output_format: str = Field(description="Output format", default="json")
    count: int = Field(description="Number of entries", default=5, ge=1, le=100)
    locale: Optional[str] = Field(description="Locale for data generation", default=None)
    fields: Optional[List[str]] = Field(description="Specific fields", default=None)


class MovieRecommendation(BaseModel):
    """Model for movie recommendations"""
    category: Optional[str] = Field(description="Movie genre/category", default=None)
    description: str = Field(description="Description of desired movies")
    similar_movie: Optional[str] = Field(description="Similar movie reference", default=None)
    limit: int = Field(description="Number of recommendations", default=5, ge=1, le=20)


class FAQRequest(BaseModel):
    """Model for FAQ handling"""
    question: str = Field(description="The user's question")
    category: Optional[str] = Field(description="Category of the question", default=None)


@tool
def generate_guide_template(
    title: str,
    category: str,
    guide_steps: List[str],
    difficulty_level: str = "beginner",
    prerequisites: List[str] = None,
    estimated_time: str = "30 minutes",
    tools_required: List[str] = None
) -> str:
    """
    Creates step-by-step instructions and tutorials ONLY when users explicitly ask for 
    procedural help or instructions. Must contain clear action-oriented language like 
    'how to', 'steps to', 'guide me through', 'tutorial for', 'instructions to', 
    'walk me through', 'teach me to', 'show me how', 'create a guide', 'make a tutorial'. 
    NEVER use for: reviews, opinions, explanations, 'what is', 'tell me about', 'explain', 
    'describe', 'compare', 'review of', 'thoughts on', career advice, or general informational questions.
    """
    if prerequisites is None:
        prerequisites = []
    if tools_required is None:
        tools_required = []
    
    guide = {
        "title": title,
        "category": category,
        "difficulty_level": difficulty_level,
        "prerequisites": prerequisites,
        "estimated_time": estimated_time,
        "tools_required": tools_required,
        "steps": guide_steps,
        "step_count": len(guide_steps)
    }
    
    # Format the guide as a readable response
    response = f"# {title}\n\n"
    response += f"**Category:** {category}\n"
    response += f"**Difficulty:** {difficulty_level.title()}\n"
    response += f"**Estimated Time:** {estimated_time}\n\n"
    
    if prerequisites:
        response += "## Prerequisites:\n"
        for prereq in prerequisites:
            response += f"- {prereq}\n"
        response += "\n"
    
    if tools_required:
        response += "## Tools Required:\n"
        for tool in tools_required:
            response += f"- {tool}\n"
        response += "\n"
    
    response += "## Steps:\n"
    for i, step in enumerate(guide_steps, 1):
        response += f"{i}. {step}\n"
    
    return response


@tool
def generate_mock_data(
    data_type: str,
    output_format: str = "json",
    count: int = 5,
    locale: str = None,
    fields: List[str] = None
) -> str:
    """
    Generates sample, test, or mock data when users request data examples, want to create 
    fake data, need sample datasets, or ask for data generation. Automatically triggered 
    by questions containing words like: mock data, sample data, generate data, test data, 
    fake data, dummy data, create data, data examples, sample users, example products.
    """
    # Sample data templates
    user_fields = ["id", "username", "email", "first_name", "last_name", "age", "city", "country"]
    product_fields = ["id", "name", "price", "category", "description", "stock", "rating"]
    order_fields = ["id", "user_id", "product_id", "quantity", "total_price", "order_date", "status"]
    employee_fields = ["id", "name", "email", "department", "position", "salary", "hire_date"]
    
    # Determine fields to use
    if fields is None:
        if data_type.lower() == "user":
            fields = user_fields
        elif data_type.lower() == "product":
            fields = product_fields
        elif data_type.lower() == "order":
            fields = order_fields
        elif data_type.lower() == "employee":
            fields = employee_fields
        else:
            fields = ["id", "name", "value", "category", "description"]
    
    # Generate mock data
    mock_data = []
    for i in range(count):
        entry = {}
        for field in fields:
            if field == "id":
                entry[field] = i + 1
            elif field in ["username", "name", "first_name"]:
                entry[field] = f"{['John', 'Jane', 'Mike', 'Sarah', 'Alex'][i % 5]}{i+1}"
            elif field == "last_name":
                entry[field] = ["Smith", "Johnson", "Williams", "Brown", "Jones"][i % 5]
            elif field == "email":
                entry[field] = f"user{i+1}@example.com"
            elif field in ["age", "stock", "quantity"]:
                entry[field] = random.randint(18, 65) if field == "age" else random.randint(1, 100)
            elif field in ["price", "total_price", "salary"]:
                entry[field] = round(random.uniform(10.99, 999.99), 2)
            elif field in ["city", "country"]:
                cities = ["New York", "London", "Tokyo", "Paris", "Sydney"]
                countries = ["USA", "UK", "Japan", "France", "Australia"]
                entry[field] = cities[i % 5] if field == "city" else countries[i % 5]
            elif field in ["category", "department"]:
                categories = ["Electronics", "Books", "Clothing", "Home", "Sports"]
                entry[field] = categories[i % 5]
            elif field in ["description", "position"]:
                descriptions = ["High quality product", "Bestselling item", "Premium choice", "Customer favorite", "Top rated"]
                entry[field] = descriptions[i % 5]
            elif field in ["status"]:
                entry[field] = ["pending", "completed", "shipped", "delivered"][i % 4]
            elif field in ["rating"]:
                entry[field] = round(random.uniform(3.0, 5.0), 1)
            else:
                entry[field] = f"sample_{field}_{i+1}"
        
        mock_data.append(entry)
    
    # Format output based on requested format
    if output_format.lower() == "json":
        return json.dumps(mock_data, indent=2)
    elif output_format.lower() == "csv":
        if not mock_data:
            return ""
        headers = ",".join(fields)
        rows = []
        for entry in mock_data:
            row = ",".join(str(entry.get(field, "")) for field in fields)
            rows.append(row)
        return headers + "\n" + "\n".join(rows)
    else:
        return json.dumps(mock_data, indent=2)


@tool
def handle_standard_faq(question: str, category: str = None) -> str:
    """
    Handles general questions, provides information, answers FAQs, gives explanations, 
    opinions, reviews, definitions, comparisons, and discussions. Use for ALL questions 
    about careers, roles, technologies, concepts, reviews, opinions, descriptions, definitions. 
    Triggered by: 'what is', 'tell me about', 'explain', 'describe', 'compare', 'review of', 
    'thoughts on', 'opinion about', career questions, informational queries, and any 
    non-procedural questions that don't require step-by-step instructions.
    """
    # This is a comprehensive FAQ handler that would typically connect to a knowledge base
    # For now, we'll provide a structured response format
    
    response = f"## Question: {question}\n\n"
    
    if category:
        response += f"**Category:** {category}\n\n"
    
    # Add a note that this would be connected to the vector database for context
    response += "I'll search my knowledge base and provide you with a comprehensive answer based on the available information.\n\n"
    response += "*Note: This response will be enhanced with context from the vector database and previous conversations.*"
    
    return response


@tool
def recommend_movies(
    description: str,
    category: str = None,
    similar_movie: str = None,
    limit: int = 5
) -> str:
    """
    Provides movie recommendations based on user preferences. Use when users ask for 
    movie suggestions, recommendations by genre/category, or movies similar to a 
    description they provide. Triggered by phrases like: 'recommend movies', 'suggest films', 
    'what movies should I watch', 'movies like', 'good [genre] movies', 'films about', 
    'movie recommendations', 'recommend action movie', 'suggest comedy films'.
    """
    # Sample movie data (in a real implementation, this would connect to a movie database)
    movies_db = {
        "action": [
            {"title": "Mad Max: Fury Road", "year": 2015, "rating": 8.1},
            {"title": "John Wick", "year": 2014, "rating": 7.4},
            {"title": "The Dark Knight", "year": 2008, "rating": 9.0},
            {"title": "Mission: Impossible", "year": 1996, "rating": 7.1},
            {"title": "Die Hard", "year": 1988, "rating": 8.2}
        ],
        "comedy": [
            {"title": "The Grand Budapest Hotel", "year": 2014, "rating": 8.1},
            {"title": "Superbad", "year": 2007, "rating": 7.6},
            {"title": "Anchorman", "year": 2004, "rating": 7.2},
            {"title": "The Hangover", "year": 2009, "rating": 7.7},
            {"title": "Groundhog Day", "year": 1993, "rating": 8.0}
        ],
        "drama": [
            {"title": "The Shawshank Redemption", "year": 1994, "rating": 9.3},
            {"title": "Forrest Gump", "year": 1994, "rating": 8.8},
            {"title": "The Godfather", "year": 1972, "rating": 9.2},
            {"title": "Schindler's List", "year": 1993, "rating": 9.0},
            {"title": "12 Years a Slave", "year": 2013, "rating": 8.1}
        ]
    }
    
    response = f"## Movie Recommendations\n\n"
    response += f"**Based on:** {description}\n"
    
    if category:
        response += f"**Genre:** {category.title()}\n"
    if similar_movie:
        response += f"**Similar to:** {similar_movie}\n"
    
    response += f"**Number of recommendations:** {limit}\n\n"
    
    # Get movies based on category or default to action
    selected_category = category.lower() if category and category.lower() in movies_db else "action"
    movies = movies_db[selected_category][:limit]
    
    response += "### Recommended Movies:\n"
    for i, movie in enumerate(movies, 1):
        response += f"{i}. **{movie['title']}** ({movie['year']}) - Rating: {movie['rating']}/10\n"
    
    response += f"\n*These are {selected_category} movies. Let me know if you'd like recommendations from a different genre!*"
    
    return response


# Define the available tools
AVAILABLE_TOOLS = [
    generate_guide_template,
    generate_mock_data,
    handle_standard_faq,
    recommend_movies,
]

# Tool mapping for easy access
TOOL_MAP = {tool.name: tool for tool in AVAILABLE_TOOLS}
