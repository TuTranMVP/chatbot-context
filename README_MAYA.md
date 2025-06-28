# 🤖 Maya Advanced FAQ Chatbot

Maya is an intelligent virtual assistant powered by Azure OpenAI that can help users with various tasks including answering questions, creating step-by-step guides, and generating mock data. The project includes both a command-line interface and a modern Streamlit web interface.

## ✨ Features

### 🎯 Core Capabilities
- **Smart FAQ Handling**: Answers general questions, provides explanations, and offers information on various topics
- **Step-by-Step Guide Generation**: Creates detailed tutorials and instructions for procedural tasks
- **Mock Data Generation**: Generates sample data in multiple formats (JSON, CSV, XML, SQL, YAML, Table)
- **AI-Enhanced Field Recommendations**: Uses OpenAI to suggest appropriate data fields and structures
- **Multi-Format Output**: Supports various output formats for generated data
- **Intelligent Function Calling**: Automatically determines the best response type based on user input

### 🖥️ Interface Options
- **Command-Line Interface** (`testprompt.py`): Interactive terminal-based chat
- **Streamlit Web Interface** (`streamlit_chatbot.py`): Modern web UI with enhanced visualization

### 🔧 Advanced Features
- **Context-Aware Responses**: Maintains conversation history and provides relevant follow-ups
- **Data Model Intelligence**: AI-powered recommendations for data structures and fields
- **Error Handling**: Robust fallback mechanisms for API failures
- **Customizable Templates**: Flexible guide and data generation templates

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Azure OpenAI API access
- Required Python packages (see requirements.txt)

### Installation

1. **Clone or download the project**
```bash
git clone <repository-url>
cd maya-chatbot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Azure OpenAI credentials**
   - Update the API endpoint and key in both `testprompt.py` and `streamlit_chatbot.py`
   - Replace the placeholder values with your actual Azure OpenAI credentials:
   ```python
   client = openai.AzureOpenAI(
       api_version="2024-07-01-preview",
       azure_endpoint="your-azure-endpoint",
       api_key="your-api-key",
   )
   ```

### Running the Applications

#### Option 1: Command-Line Interface
```bash
python testprompt.py
```

#### Option 2: Streamlit Web Interface
```bash
streamlit run streamlit_chatbot.py
```

## 📖 Usage Guide

### 🗣️ Conversation Types

#### 1. General FAQ Questions
Ask about concepts, technologies, careers, or request explanations:
```
"What is machine learning?"
"Tell me about software engineering careers"
"Explain the difference between AI and ML"
```

#### 2. Step-by-Step Guides
Request tutorials or instructions using action-oriented language:
```
"How to set up a Python virtual environment"
"Guide me through creating a REST API"
"Show me how to deploy a web application"
```

#### 3. Mock Data Generation
Request sample data for testing or development:
```
"Generate 10 user records"
"Create sample product data in CSV format"
"Generate employee data with specific fields"
```

### 📊 Mock Data Features

#### Output Formats
- **JSON**: Structured data objects
- **CSV**: Comma-separated values for spreadsheets
- **SQL**: Database insert statements
- **Table**: Formatted text tables

#### Advanced Options
- **Count**: Specify number of records (1-100)
- **Locale**: Regional data formatting (e.g., 'en-US', 'vi-VN')
- **Custom Fields**: Define specific data fields
- **AI Enhancement**: Automatic field recommendations based on data type

### Function Schemas
The chatbot uses three main function schemas:

1. **generate_guide_template**: For creating step-by-step instructions
2. **generate_mock_data**: For generating sample data
3. **handle_standard_faq**: For general question answering

## 💡 Examples

### Example 1: Guide Generation
**Input**: "How to create a REST API with Python Flask"

**Output**: Structured guide with:
- Title and category
- Difficulty level
- Prerequisites
- Step-by-step instructions
- Estimated completion time
- Required tools

### Example 2: Mock Data Generation
**Input**: "Generate 5 e-commerce user records in JSON format"

**Output**: 
```json
[
  {
    "id": 1,
    "username": "john_smith123",
    "email": "john.smith@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "age": 28,
    "created_at": "2024-03-15T10:30:00",
    "status": "active"
  },
  // ... more records
]
```

### Example 3: FAQ Response
**Input**: "What is the difference between AI and Machine Learning?"

**Output**: Comprehensive explanation with:
- Clear definitions
- Key differences
- Related topics
- Practical examples

## 🛠️ Development

### Code Quality
The project uses Ruff for code linting and formatting:
```bash
ruff check .
ruff format .
```

## 🚨 Important Notes

### Security
- Never commit API keys to version control
- Use environment variables for sensitive configuration
- Validate all user inputs before processing

### API Limitations
- OpenAI API has rate limits and usage costs
- Mock data generation is limited to 100 records per request
- Function calling requires compatible OpenAI models

### Error Handling
The chatbot includes robust error handling:
- Fallback data generation when AI recommendations fail
- Graceful degradation for API connection issues
- User-friendly error messages

## 📝 Dependencies

### Core Dependencies
- `openai>=1.3.0`: Azure OpenAI integration
- `streamlit`: Web interface framework
- `flask>=2.3.3`: Alternative web framework
- `python-dotenv>=1.0.0`: Environment variable management

### Development Dependencies
- `ruff>=0.1.0`: Code linting and formatting
- `requests>=2.31.0`: HTTP client library
- `jinja2>=3.1.2`: Template engine

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is part of an AI training program and is intended for educational purposes.

## 🆘 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your Azure OpenAI credentials
3. Ensure all dependencies are installed
4. Review the function schemas for proper usage

For additional help, contact the development team or refer to the Azure OpenAI documentation.

---

**Maya Advanced FAQ Chatbot** - Empowering users with intelligent assistance and dynamic content generation! 🚀
