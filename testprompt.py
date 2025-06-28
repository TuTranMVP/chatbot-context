import os
import json
import random

try:
    import openai

    client = openai.AzureOpenAI(
        api_version="2024-07-01-preview",
        azure_endpoint="https://aiportalapi.stu-platform.live/jpe",
        api_key="sk-ht7c6K5jpVJUsJOdjTNtxA",
    )

    # Define function schemas for different template types
    functions = [
        {
            "type": "function",
            "function": {
                "name": "generate_guide_template",
                "description": "Creates step-by-step instructions and tutorials ONLY when users explicitly ask for procedural help or instructions. Must contain clear action-oriented language like 'how to', 'steps to', 'guide me through', 'tutorial for', 'instructions to', 'walk me through', 'teach me to', 'show me how', 'create a guide', 'make a tutorial'. NEVER use for: reviews, opinions, explanations, 'what is', 'tell me about', 'explain', 'describe', 'compare', 'review of', 'thoughts on', career advice, or general informational questions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the guide"
                        },
                        "category": {
                            "type": "string",
                            "description": "Category of the guide (e.g., 'technical', 'setup', 'tutorial')"
                        },
                        "difficulty_level": {
                            "type": "string",
                            "enum": ["beginner", "intermediate", "advanced"],
                            "description": "Difficulty level of the guide"
                        },
                        "prerequisites": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Prerequisites needed before following the guide"
                        },
                        "guide_steps": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Step-by-step instructions"
                        },
                        "estimated_time": {
                            "type": "string",
                            "description": "Estimated time to complete the guide"
                        },
                        "tools_required": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tools or software required"
                        }
                    },
                    "required": ["title", "category", "guide_steps"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_mock_data",
                "description": "Generates sample, test, or mock data when users request data examples, want to create fake data, need sample datasets, or ask for data generation. Automatically triggered by questions containing words like: mock data, sample data, generate data, test data, fake data, dummy data, create data, data examples, sample users, example products. Only include optional parameters if the user specifically requests them.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data_type": {
                            "type": "string",
                            "description": "Type of data to generate (e.g., 'user', 'product', 'order', 'employee', 'custom'). Extract this from the user's request context."
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["json", "csv", "xml", "sql", "yaml", "table"],
                            "description": "Output format for the mock data. Only include if user specifically requests a format, otherwise omit to use default (json)."
                        },
                        "count": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Number of mock data entries to generate. Only include if user specifies a number, otherwise omit to use default (5)."
                        },
                        "locale": {
                            "type": "string",
                            "description": "Locale for data generation (e.g., 'en-US', 'vi-VN'). Only include if user mentions a specific locale or language preference."
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific field names to include in the generated data (e.g., ['username', 'email']). Only include if user explicitly lists specific fields they want, otherwise omit to get AI-recommended fields."
                        }
                    },
                    "required": ["data_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "handle_standard_faq",
                "description": "Handles general questions, provides information, answers FAQs, gives explanations, opinions, reviews, definitions, comparisons, and discussions. Use for ALL questions about careers, roles, technologies, concepts, reviews, opinions, descriptions, definitions. Triggered by: 'what is', 'tell me about', 'explain', 'describe', 'compare', 'review of', 'thoughts on', 'opinion about', career questions, informational queries, and any non-procedural questions that don't require step-by-step instructions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The user's question"
                        },
                        "category": {
                            "type": "string",
                            "description": "Category of the question"
                        },
                        "answer": {
                            "type": "string",
                            "description": "The main answer to the question"
                        },
                        "related_topics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Related topics or questions"
                        }
                    },
                    "required": ["question", "answer"]
                }
            }
        }
    ]

    # Store conversation history and FAQ data
    messages = [{"role": "system", "content": """
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
        You can say: “I'm not able to answer that, but you can reach out to our support team for further help.”
        Always close the conversation with an offer to help with anything else.
    """}]
    faq_sessions = []

    # Function to generate a structured guide
    def generate_guide_template(title, category, guide_steps, difficulty_level="intermediate", 
                               prerequisites=None, estimated_time="", tools_required=None):
        """
        Generate a structured guide template with step-by-step instructions.
        
        Args:
            title (str): Guide title
            category (str): Guide category
            guide_steps (list): List of step-by-step instructions
            difficulty_level (str): Difficulty level (beginner/intermediate/advanced)
            prerequisites (list): Required prerequisites
            estimated_time (str): Estimated completion time
            tools_required (list): Required tools or software
            
        Returns:
            dict: Structured guide data
        """
        guide_data = {
            "type": "guide",
            "title": title,
            "category": category,
            "difficulty_level": difficulty_level,
            "prerequisites": prerequisites or [],
            "guide_steps": guide_steps,
            "estimated_time": estimated_time,
            "tools_required": tools_required or [],
        }
        
        print(f"📚 Generated guide template: '{title}' ({difficulty_level})")
        return guide_data

    # Function handle generate mock data
    def generate_mock_data(data_type, output_format=None, count=None, fields=None, locale=None):
        """
        Generate mock data with specified parameters and format options.
        Uses OpenAI API to get recommended model structure based on data type.
        
        Args:
            data_type (str): Type of data to generate
            output_format (str): Output format (json/csv/xml/sql/yaml/table)
            count (int): Number of entries (default: 5, max: 100)
            fields (list): Specific fields to include
            locale (str): Locale for data generation
            
        Returns:
            dict: Generated mock data structure
        """
        
        # Set default values for optional parameters
        if output_format is None or not output_format:
            output_format = "json"
            print("📋 Using default output format: json")
        
        if count is None or count <= 0:
            count = 5
            print("📋 Using default count: 5 entries")
        
        if locale is None or not locale:
            locale = "en-US"
            print("📋 Using default locale: en-US")
        
        # Validate count limit
        if count > 100:
            count = 100
            print("⚠️ Count limited to 100 entries for performance")
        
        # Always get AI-recommended model structure and fields from OpenAI based on data_type
        print(f"🔍 Generating mock data for type: {data_type} with count: {count}")
        print(f"🔍 Using fields: {fields}")
        
        # Use OpenAI to enhance the model and get field recommendations
        # Only get AI recommendations if fields not explicitly provided
        if not fields:  # Only get AI recommendations if fields not explicitly provided
            # Use the data_type to get model recommendations
            print(f"🤖 Getting OpenAI model recommendations for data type: '{data_type}'")
            enhanced_model, recommended_fields = _get_openai_model_recommendations(data_type)
        else:
            # User provided specific fields, use them directly
            recommended_fields = fields
            print(f"✅ Using user-specified fields: {', '.join(fields)}")
            # Create a simple model description
            enhanced_model = f"Custom {data_type} data with user-specified fields: {', '.join(fields)}"
        
        mock_data = {
            "type": "mock_data",
            "data_type": data_type,
            "data_model": enhanced_model,
            "output_format": output_format,
            "count": count,
            "fields": recommended_fields,
            "user_provided_fields": bool(fields),  # True if user provided specific fields
            "locale": locale,
            "generated_data": [],
            "ai_enhanced": bool(recommended_fields) and not bool(fields),  # True only if AI-recommended fields were used
        }
        
        # Generate data based on type and enhanced model
        mock_data["generated_data"] = _generate_data_by_type(
            data_type, enhanced_model, count, recommended_fields, locale
        )
        
        field_source = "user-specified" if fields else "AI-enhanced"
        model_info = f" (Fields: {field_source})"
        print(f"📊 Generated {count} {data_type} entries in {output_format.upper()} format{model_info}")
        return mock_data

    def _generate_data_by_type(data_type, data_model, count, fields, locale):
        """
        Internal function to generate data based on type and model.
        Prioritizes AI-enhanced field generation over hardcoded generators.
        """
        import random
        from datetime import datetime, timedelta
        
        # Always prefer AI-enhanced generation when fields are available
        if fields and len(fields) > 0:
            print(f"🎯 Using AI-recommended fields: {', '.join(fields[:5])}{'...' if len(fields) > 5 else ''}")
            return _generate_enhanced_data_with_fields(data_type, data_model, count, fields, locale)
        
        # Fallback to standard generators only if no AI fields are available
        print("⚠️ No AI fields available, using fallback generators")
        data_generators = {
            "user": _generate_user_data,
            "product": _generate_product_data,
            "order": _generate_order_data,
            "employee": _generate_employee_data,
            "custom": _generate_custom_data
        }
        
        generator = data_generators.get(data_type.lower(), _generate_custom_data)
        return generator(count, data_model, fields, locale)

    def _get_openai_model_recommendations(data_type):
        """
        Use OpenAI to get recommended model types and fields for mock data generation.
        
        Args:
            data_type (str): The type of data being generated
            
        Returns:
            tuple: (selected_model_description, recommended_fields_list)
        """
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
            
            response = client.chat.completions.create(
                model="GPT-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            recommended_models = result.get("recommended_models", [])
            default_model = result.get("default_model", {})
            
            print(f"🤖 AI found {len(recommended_models)} model options for '{data_type}':")
            for i, model in enumerate(recommended_models, 1):
                print(f"   {i}. {model.get('model_name', 'Unknown')} - {model.get('description', 'No description')}")
            
            # For now, use the default model (in future this could be user-selectable)
            selected_model = default_model
            if not selected_model and recommended_models:
                selected_model = recommended_models[0]  # Fallback to first model
            
            model_description = selected_model.get("description", f"Standard {data_type} data model")
            recommended_fields = selected_model.get("fields", [])
            
            print(f"🎯 Using model: {selected_model.get('model_name', 'Default')}")
            print(f"🎯 AI recommended {len(recommended_fields)} fields")
            
            return model_description, recommended_fields
            
        except Exception as e:
            print(f"⚠️ Could not get AI recommendations: {e}")
            # Fallback to basic fields
            basic_models = {
                "user": {
                    "description": "Standard user profile with basic account information",
                    "fields": ["id", "username", "email", "first_name", "last_name", "age", "created_at", "status"]
                },
                "product": {
                    "description": "Product catalog entry with pricing and inventory details", 
                    "fields": ["id", "name", "price", "category", "description", "stock_quantity", "rating", "created_at"]
                },
                "order": {
                    "description": "Order transaction with customer and payment information",
                    "fields": ["id", "customer_id", "total_amount", "status", "order_date", "payment_method", "shipping_address"]
                },
                "employee": {
                    "description": "Employee record with job and personal information",
                    "fields": ["id", "first_name", "last_name", "email", "department", "position", "salary", "hire_date"]
                },
                "custom": {
                    "description": "Custom data structure with flexible fields",
                    "fields": ["id", "name", "value", "type", "created_at", "status"]
                }
            }
            
            fallback = basic_models.get(data_type.lower(), basic_models["custom"])
            return fallback["description"], fallback["fields"]
    
    def _generate_enhanced_data_with_fields(data_type, data_model, count, fields, locale):
        """
        Generate enhanced data using AI-recommended fields and model structure.
        
        Args:
            data_type (str): Type of data
            data_model (str): Enhanced model description
            count (int): Number of entries to generate
            fields (list): AI-recommended field names
            locale (str): Locale for data generation
            
        Returns:
            list: Generated data entries with AI-recommended structure
        """
        import random
        from datetime import datetime, timedelta
        
        # Sample data pools for different field types
        sample_data = {
            # Names and identity
            "name": ["John Smith", "Jane Doe", "Mike Johnson", "Sarah Wilson", "David Brown"],
            "first_name": ["John", "Jane", "Mike", "Sarah", "David", "Emily", "Chris", "Lisa"],
            "last_name": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"],
            "username": ["john_smith", "jane_doe", "mike_j", "sarah_w", "david_b", "emily_c", "chris_l", "lisa_m"],
            "loginname": ["john.smith", "jane.doe", "mike.johnson", "sarah.wilson", "david.brown"],
            "email": ["user@example.com", "test@gmail.com", "sample@yahoo.com"],
            
            # Authentication and security
            "password": ["SecurePass123!", "MyPassword2024", "StrongPwd@456", "UserPass789#", "SafeLogin2024!"],
            
            # Business and commerce
            "title": ["Software Engineer", "Product Manager", "Designer", "Analyst", "Director"],
            "company": ["TechCorp", "DataSoft", "WebSolutions", "AppDev Inc", "Digital Pro"],
            "department": ["Engineering", "Marketing", "Sales", "HR", "Finance"],
            "category": ["Electronics", "Clothing", "Books", "Home", "Sports"],
            "brand": ["Brand A", "Brand B", "Premium Co", "Quality Ltd", "Best Corp"],
            "status": ["active", "inactive", "pending", "completed", "cancelled"],
            
            # Location
            "country": ["United States", "Canada", "United Kingdom", "Germany", "France"],
            "city": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "address": ["123 Main St", "456 Oak Ave", "789 Pine Rd", "321 Elm St"],
            
            # Technical
            "platform": ["web", "mobile", "desktop", "api", "cloud"],
            "technology": ["Python", "JavaScript", "Java", "React", "Node.js"],
            "version": ["1.0.0", "2.1.3", "3.2.1", "4.0.0", "5.1.2"]
        }
        
        generated_data = []
        
        for i in range(count):
            entry = {"id": i + 1}
            
            for field in fields:
                field_lower = field.lower()
                
                # Generate appropriate data based on field name patterns
                if any(keyword in field_lower for keyword in ["id", "number", "count", "quantity"]):
                    entry[field] = random.randint(1, 10000)
                        
                elif any(keyword in field_lower for keyword in ["price", "cost", "amount", "salary", "revenue"]):
                    entry[field] = round(random.uniform(10.99, 9999.99), 2)
                        
                elif any(keyword in field_lower for keyword in ["date", "time", "created", "updated"]):
                    base_date = datetime(2024, 1, 1)
                    random_days = random.randint(0, 365)
                    entry[field] = (base_date + timedelta(days=random_days)).isoformat()
                        
                elif any(keyword in field_lower for keyword in ["email", "mail"]):
                    domains = ["gmail.com", "yahoo.com", "example.com", "company.com"]
                    usernames = ["john.smith", "jane.doe", "mike.johnson", "sarah.wilson", "david.brown"]
                    entry[field] = f"{random.choice(usernames).replace('.', '')}@{random.choice(domains)}"
                
                elif any(keyword in field_lower for keyword in ["username", "user_name", "login"]):
                    base_usernames = ["john_smith", "jane_doe", "mike_j", "sarah_w", "david_b", "emily_c"]
                    entry[field] = f"{random.choice(base_usernames)}{random.randint(1, 999)}"
                
                elif any(keyword in field_lower for keyword in ["loginname", "login_name"]):
                    base_logins = ["john.smith", "jane.doe", "mike.johnson", "sarah.wilson", "david.brown"]
                    entry[field] = f"{random.choice(base_logins)}{random.randint(10, 99)}"
                
                elif any(keyword in field_lower for keyword in ["password", "pwd", "pass"]):
                    passwords = ["SecurePass123!", "MyPassword2024", "StrongPwd@456", "UserPass789#", "SafeLogin2024!"]
                    entry[field] = random.choice(passwords)
                        
                elif any(keyword in field_lower for keyword in ["phone", "mobile", "tel"]):
                    entry[field] = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                        
                elif any(keyword in field_lower for keyword in ["url", "website", "link"]):
                    entry[field] = f"https://example.com/{field_lower}{i+1}"
                    
                elif any(keyword in field_lower for keyword in ["bool", "is_", "has_", "can_", "verified", "active"]):
                    entry[field] = random.choice([True, False])
                    
                elif any(keyword in field_lower for keyword in ["rating", "score", "rank"]):
                    entry[field] = round(random.uniform(1.0, 5.0), 1)
                        
                else:
                    # Try to match with sample data or generate generic value
                    matched_samples = []
                    for key, samples in sample_data.items():
                        if key in field_lower or field_lower in key:
                            matched_samples = samples
                            break
                    
                    if matched_samples:
                        if field_lower in ["username", "loginname"]:
                            # Add random number to make usernames unique
                            base_value = random.choice(matched_samples)
                            entry[field] = f"{base_value}{random.randint(1, 999)}"
                        else:
                            entry[field] = random.choice(matched_samples)
                    else:
                        # Generate generic field value based on field name patterns
                        if field_lower in ["username", "user_name"]:
                            entry[field] = f"user_{i+1}"
                        elif field_lower in ["loginname", "login_name"]:
                            entry[field] = f"user.{i+1}"
                        elif "password" in field_lower:
                            entry[field] = "password123"
                        elif "email" in field_lower:
                            entry[field] = f"user{i+1}@example.com"
                        else:
                            entry[field] = f"sample_{field}_value_{i+1}"
            
            generated_data.append(entry)
        
        return generated_data

    def _generate_user_data(count, model, fields, locale):
        """Generate user mock data with various models."""
        import random
        
        # Different user models
        if "social" in model.lower():
            return _generate_social_user_data(count)
        elif "ecommerce" in model.lower() or "e-commerce" in model.lower():
            return _generate_ecommerce_user_data(count)
        else:
            return _generate_basic_user_data(count)

    # functions to generate data when call api fail
    def _generate_basic_user_data(count):
        """Generate basic user data."""
        import random
        
        first_names = ["John", "Jane", "Mike", "Sarah", "David", "Emily", "Chris", "Lisa", "Tom", "Anna"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "example.com"]
        
        users = []
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            users.append({
                "id": i + 1,
                "username": f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}",
                "email": f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}",
                "first_name": first_name,
                "last_name": last_name,
                "age": random.randint(18, 65),
                "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "status": random.choice(["active", "inactive", "pending"]),
                "created_at": "2024-01-01T00:00:00Z"
            })
        return users

    def _generate_social_user_data(count):
        """Generate social media user data."""
        import random
        
        usernames = ["techguru", "foodlover", "traveler", "photographer", "musician", "artist"]
        platforms = ["instagram", "twitter", "facebook", "linkedin"]
        
        users = []
        for i in range(count):
            users.append({
                "user_id": i + 1,
                "username": f"{random.choice(usernames)}{random.randint(1, 9999)}",
                "display_name": f"User {i + 1}",
                "bio": "Social media enthusiast",
                "followers": random.randint(10, 10000),
                "following": random.randint(5, 1000),
                "posts_count": random.randint(0, 500),
                "platform": random.choice(platforms),
                "verified": random.choice([True, False]),
                "joined_date": "2024-01-01"
            })
        return users

    def _generate_ecommerce_user_data(count):
        """Generate e-commerce user data."""
        import random
        
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
        states = ["NY", "CA", "IL", "TX", "AZ"]
        
        users = []
        for i in range(count):
            users.append({
                "customer_id": i + 1,
                "email": f"customer{i+1}@example.com",
                "first_name": f"Customer{i+1}",
                "last_name": "User",
                "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "address": {
                    "street": f"{random.randint(100, 9999)} Main St",
                    "city": random.choice(cities),
                    "state": random.choice(states),
                    "zip_code": f"{random.randint(10000, 99999)}"
                },
                "total_orders": random.randint(0, 50),
                "total_spent": round(random.uniform(0, 5000), 2),
                "loyalty_points": random.randint(0, 1000),
                "account_status": random.choice(["active", "inactive", "premium"])
            })
        return users

    def _generate_product_data(count, model, fields, locale):
        """Generate product mock data."""
        import random
        
        categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports", "Beauty"]
        brands = ["TechCorp", "StyleCo", "ReadMore", "HomeBasics", "SportsPro", "BeautyMax"]
        
        products = []
        for i in range(count):
            category = random.choice(categories)
            products.append({
                "product_id": i + 1,
                "name": f"Product {i + 1}",
                "category": category,
                "brand": random.choice(brands),
                "price": round(random.uniform(10.99, 999.99), 2),
                "description": f"High quality product in {category.lower()} category",
                "stock_quantity": random.randint(0, 100),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "reviews_count": random.randint(0, 500),
                "created_at": "2024-01-01T00:00:00Z"
            })
        return products

    def _generate_order_data(count, model, fields, locale):
        """Generate order mock data."""
        import random
        
        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        payment_methods = ["credit_card", "paypal", "bank_transfer", "cash_on_delivery"]
        
        orders = []
        for i in range(count):
            orders.append({
                "order_id": i + 1,
                "customer_id": random.randint(1, 100),
                "order_date": "2024-01-01T00:00:00Z",
                "status": random.choice(statuses),
                "total_amount": round(random.uniform(20.00, 500.00), 2),
                "items_count": random.randint(1, 5),
                "payment_method": random.choice(payment_methods),
                "shipping_address": "123 Main St, City, State 12345",
                "tracking_number": f"TRK{random.randint(100000, 999999)}",
                "estimated_delivery": "2024-01-08T00:00:00Z"
            })
        return orders

    def _generate_employee_data(count, model, fields, locale):
        """Generate employee mock data."""
        import random
        
        departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
        positions = ["Manager", "Developer", "Analyst", "Coordinator", "Specialist", "Director"]
        
        employees = []
        for i in range(count):
            employees.append({
                "employee_id": i + 1,
                "first_name": f"Employee{i+1}",
                "last_name": "User",
                "email": f"employee{i+1}@company.com",
                "department": random.choice(departments),
                "position": random.choice(positions),
                "salary": random.randint(40000, 120000),
                "hire_date": "2024-01-01",
                "manager_id": random.randint(1, max(1, i)) if i > 0 else None,
                "status": random.choice(["active", "inactive", "on_leave"])
            })
        return employees

    def _generate_custom_data(count, model, fields, locale):
        """Generate custom mock data."""
        custom_data = []
        for i in range(count):
            entry = {"id": i + 1}
            if fields:
                for field in fields:
                    entry[field] = f"sample_{field}_value_{i+1}"
            else:
                entry.update({
                    "name": f"Item {i+1}",
                    "description": f"Description for item {i+1}",
                    "value": f"Value_{i+1}",
                    "created_at": "2024-01-01T00:00:00Z"
                })
            custom_data.append(entry)
        return custom_data

    # Handle function call for responses
    def handle_standard_faq(question, answer, category="general", related_topics=None):
        """Handle standard FAQ responses with structured format."""
        faq_data = {
            "type": "standard",
            "question": question,
            "category": category,
            "answer": answer,
            "related_topics": related_topics or [],
        }
        
        print(f"💬 Processed FAQ: {category}")
        return faq_data

    # Process data based on function calls
    def process_function_call(function_call):
        """Process function calls and return structured responses."""
        try:
            arguments = json.loads(function_call.arguments)
            function_name = function_call.name
            
            print(f"🔧 Executing function: {function_name}")
            
            if function_name == "generate_guide_template":
                result = generate_guide_template(**arguments)
            elif function_name == "generate_mock_data":
                result = generate_mock_data(**arguments)
            elif function_name == "handle_standard_faq":
                result = handle_standard_faq(**arguments)
            else:
                print(f"❌ Unknown function: {function_name}")
                return None
                
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing function arguments: {e}")
            return None
        except Exception as e:
            print(f"❌ Error executing {function_call.name}: {e}")
            return None
    # Format the response based on the template type
    def format_response(response_data):
        """Format the response based on the template type."""
        response_type = response_data.get('type')
        
        if response_type == 'guide':
            return format_guide_response(response_data)
        elif response_type == 'mock_data':
            return format_mock_data_response(response_data)
        elif response_type == 'mock_data_clarification':
            return format_clarification_response(response_data)
        else:
            return format_standard_response(response_data)

    def format_guide_response(guide_data):
        """Format guide template response with professional structure."""
        response = f"📚 === GUIDE: {guide_data.get('title', 'Untitled')} ===\n\n"
        
        response += f"🎯 **Category:** {guide_data.get('category', 'General')}\n"
        response += f"📊 **Difficulty:** {guide_data.get('difficulty_level', 'intermediate').title()}\n"
        
        if guide_data.get('estimated_time'):
            response += f"⏱️ **Estimated Time:** {guide_data['estimated_time']}\n"
        
        response += "\n"
        
        if guide_data.get('prerequisites'):
            response += "⚠️ **Prerequisites:**\n"
            for prereq in guide_data['prerequisites']:
                response += f"• {prereq}\n"
            response += "\n"
        
        if guide_data.get('tools_required'):
            response += "🛠️ **Tools Required:**\n"
            for tool in guide_data['tools_required']:
                response += f"• {tool}\n"
            response += "\n"
        
        response += "📋 **Steps:**\n"
        for i, step in enumerate(guide_data.get('guide_steps', []), 1):
            response += f"{i}. {step}\n"
        
        return response

    def format_mock_data_response(mock_data):
        """Format mock data response with multiple output formats and AI enhancement info."""
        response = f"📊 === MOCK DATA: {mock_data.get('data_type', 'Unknown').title()} ===\n\n"
        
        response += f"🎯 **Data Type:** {mock_data.get('data_type', 'Unknown')}\n"
        response += f"📝 **Format:** {mock_data.get('output_format', 'json').upper()}\n"
        response += f"🔢 **Count:** {mock_data.get('count', 0)} entries\n"
        
        if mock_data.get('data_model'):
            response += f"🏗️ **Model:** {mock_data['data_model']}\n"
        
        # Show AI enhancement info
        if mock_data.get('ai_enhanced'):
            response += f"🤖 **AI Enhanced:** Yes (auto-generated for '{mock_data.get('data_type', 'N/A')}')\n"
            if mock_data.get('fields'):
                response += f"✨ **AI Fields:** {len(mock_data['fields'])} recommended fields\n"
        
        response += "\n💾 **Generated Data:**\n\n"
        
        # Format data based on requested format
        data = mock_data.get('generated_data', [])
        format_type = mock_data.get('output_format', 'json').lower()
        
        if format_type == 'json':
            response += "```json\n"
            response += json.dumps(data, indent=2)
            response += "\n```\n"
        elif format_type == 'csv':
            response += _format_as_csv(data)
        elif format_type == 'xml':
            response += _format_as_xml(data, mock_data.get('data_type', 'item'))
        elif format_type == 'table':
            response += _format_as_table(data)
        else:
            response += json.dumps(data, indent=2)
        
        # Show field info if AI-enhanced
        if mock_data.get('ai_enhanced') and mock_data.get('fields'):
            response += f"\n🎯 **AI-Recommended Fields Used:** {', '.join(mock_data['fields'][:10])}"
            if len(mock_data['fields']) > 10:
                response += f" and {len(mock_data['fields']) - 10} more..."
            response += "\n"
        
        return response

    def format_clarification_response(clarification_data):
        """Format clarification request for mock data."""
        response = "❓ === CLARIFICATION NEEDED ===\n\n"
        response += f"📊 **Data Type:** {clarification_data.get('data_type', 'Unknown')}\n"
        response += f"📝 **Format:** {clarification_data.get('format', 'json').upper()}\n\n"
        response += f"💬 {clarification_data.get('message', 'I need more information')}\n\n"
        
        missing_info = clarification_data.get('missing_info', {})
        for key, question in missing_info.items():
            if question:
                response += f"• {question}\n"
        
        response += "\nPlease provide the missing information so I can generate the data for you! 😊"
        return response

    def format_standard_response(faq_data):
        """Format standard FAQ response with clean structure."""
        response = "🤖 === STANDARD FAQ RESPONSE ===\n\n"
        
        response += f"❓ **Question:** {faq_data.get('question', 'N/A')}\n\n"
        response += f"💡 **Answer:**\n{faq_data.get('answer', 'No answer provided')}\n\n"
        
        response += f"📂 **Category:** {faq_data.get('category', 'general').title()}\n"
        
        if faq_data.get('related_topics'):
            response += "\n🔗 **Related Topics:**\n"
            for topic in faq_data['related_topics']:
                response += f"• {topic}\n"
            response += "\n"
        
        return response

    def _format_as_csv(data):
        """Format data as CSV string."""
        if not data:
            return "No data to display"
        
        csv_content = "```csv\n"
        
        # Header
        headers = list(data[0].keys())
        csv_content += ",".join(headers) + "\n"
        
        # Data rows
        for item in data:
            row = [str(item.get(header, "")).replace(",", ";") for header in headers]
            csv_content += ",".join(row) + "\n"
        
        csv_content += "```\n"
        return csv_content

    def _format_as_xml(data, root_name):
        """Format data as XML string."""
        if not data:
            return "No data to display"
        
        xml_content = "```xml\n"
        xml_content += f"<{root_name}s>\n"
        
        for item in data:
            xml_content += f"  <{root_name}>\n"
            for key, value in item.items():
                xml_content += f"    <{key}>{value}</{key}>\n"
            xml_content += f"  </{root_name}>\n"
        
        xml_content += f"</{root_name}s>\n```\n"
        return xml_content

    def _format_as_table(data):
        """Format data as ASCII table."""
        if not data:
            return "No data to display"
        
        headers = list(data[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = max(len(header), max(len(str(item.get(header, ""))) for item in data))
        
        table_content = "```\n"
        
        # Header row
        header_row = " | ".join(header.ljust(col_widths[header]) for header in headers)
        table_content += header_row + "\n"
        
        # Separator row
        separator = " | ".join("-" * col_widths[header] for header in headers)
        table_content += separator + "\n"
        
        # Data rows
        for item in data:
            row = " | ".join(str(item.get(header, "")).ljust(col_widths[header]) for header in headers)
            table_content += row + "\n"
        
        table_content += "```\n"
        return table_content

    #handle logic call api with user input and trigger function calling
    def process_faq_with_function_calling(user_question):
        """
        Process FAQ using function calling with full conversation history.
        
        Args:
            user_question (str): The user's question
            
        Returns:
            tuple: (readable_response, structured_response)
        """
        try:
            # Add current user question to messages
            print(f"💬 User question: {user_question}")
            messages.append({"role": "user", "content": user_question})

            # Call OpenAI with function calling and full conversation context
            response = client.chat.completions.create(
                model="GPT-4o-mini",
                messages=messages,
                temperature=0.3,
                tools=functions,
                tool_choice='auto'
            )

            # Add assistant response to history
            if response.choices[0].message.content:
                messages.append({
                    "role": "assistant", 
                    "content": response.choices[0].message.content
                })

            # Process function call if present
            if response.choices[0].message.tool_calls:
                print("🔧 Function call detected")
                function_call = response.choices[0].message.tool_calls[0].function
                structured_response = process_function_call(function_call)
                
                if structured_response:
                    # Store the structured response for future context
                    faq_sessions.append(structured_response)
                    print(f"💾 Session stored. Total interactions: {len(faq_sessions)}")
                    
                    # Generate human-readable response
                    readable_response = format_response(structured_response)
                    return readable_response, structured_response
            
            # Fallback to regular response if function calling fails
            print("⚠️ No function call detected, using direct response")
            fallback_response = response.choices[0].message.content or "I couldn't process your request properly."
            return fallback_response, None
            
        except Exception as e:
            print(f"❌ Error in process_faq_with_function_calling: {e}")
            return f"Sorry, I encountered an error: {str(e)}", None

    print("🤖 Welcome to Maya's Advanced FAQ Chatbot!")
    print("💡 I can help you with:")
    print("  📚 Step-by-step guides and tutorials")
    print("  📊 Mock data generation (various formats)")
    print("  💬 General FAQ questions")
    print("\nType 'quit' or 'exit' to end the conversation.\n")

    while True:
        user_question = input("❓ Your Question: ").strip()
        
        if user_question.lower() in ['quit', 'exit', 'bye', 'goodbye']:
            print("👋 Thank you for using Maya's FAQ Bot! Goodbye!")
            break
        
        if not user_question:
            print("Please enter a valid question.")
            continue

        print("\n🔄 Processing your question...")
        
        # Process the question with function calling
        readable_response, structured_response = process_faq_with_function_calling(user_question)
        
        print("\n" + "="*60)
        print(readable_response)
        print("="*60)

except Exception as e:
    print("Error during run script:", e)
    input("Press Enter to exit...")
    exit(1)