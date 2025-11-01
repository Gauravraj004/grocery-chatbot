"""
AI Query Translator Module
Uses Google Gemini via LangChain to translate natural language queries 
into structured JSON filter objects.
"""

import json
from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class PriceFilter(BaseModel):
    """Price filter with operator and value."""
    operator: str = Field(description="Comparison operator: '<', '>', '<=', '>=', '=='")
    value: float = Field(description="Price value in GBP")


class ProductQuery(BaseModel):
    """Structured query for product search (LIST-based schema)."""
    vendors: Optional[List[str]] = Field(
        default=None,
        description="List of vendor/shop names: ['ASDA', 'Subway', 'Tesco'] or null for all"
    )
    exclude_vendors: Optional[List[str]] = Field(
        default=None,
        description="List of vendors/shops to EXCLUDE: ['ASDA', 'Subway'] or null"
    )
    product_types: Optional[List[str]] = Field(
        default=None,
        description="List of product categories: ['bagel', 'sandwich', 'drink', 'snack'] or null for all"
    )
    brand: Optional[str] = Field(
        default=None,
        description="Brand name (e.g., 'Coca-Cola', 'PepsiCo', 'Subway'), or null"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="List of dietary tags: ['vegan', 'gluten-free', 'low-fat', 'low-calorie', 'vegetarian'] or null"
    )
    price_filter: Optional[PriceFilter] = Field(
        default=None,
        description="Price comparison filter, or null"
    )
    sort_by: Optional[str] = Field(
        default="price_asc",
        description="Sort order: 'price_asc', 'price_desc', 'name'"
    )
    keywords: Optional[List[str]] = Field(
        default=None,
        description="Product name keywords to search for (e.g., ['Coke', 'Pepsi'])"
    )


class QueryTranslator:
    """Translates natural language to structured product queries using Gemini."""
    
    def __init__(self, api_key: str):
        """Initialize the query translator with Gemini API key."""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1,  # Low temperature for consistent parsing
            max_output_tokens=512
        )
        
        self.parser = PydanticOutputParser(pydantic_object=ProductQuery)

        # System prompt with LIST-based schema instructions
        # Bestest prompt: inherit and merge previous context unless overridden
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert query parser for a grocery shopping assistant.
Your ONLY job is to take a [Previous context] and a new [User query] and return the
**COMPLETE, MERGED** JSON for the new search state. You must not forget old context
unless the user explicitly overrides it.

🎯 CRITICAL SCHEMA RULES:
- "vendors", "exclude_vendors", "product_types", "tags", "keywords" MUST BE LISTS or null.
- "from subway" -> "vendors": ["Subway"]
- "from subway or asda" -> "vendors": ["Subway", "ASDA"]
- "Coke or Pepsi" -> "keywords": ["Coke", "Pepsi"]

🎯 CRITICAL CONTEXT RULES (THE MOST IMPORTANT PART):
1.  **INHERIT:** You MUST carry over all filters from the [Previous context]
    unless the [User query] contradicts them.
2.  **OVERRIDE:** If the [User query] mentions a conflicting filter (e.g., context
    has "vendors": ["ASDA"] and user says "from Subway"), you MUST use the new
    filter ("vendors": ["Subway"]).
3.  **MUTUAL EXCLUSION:** "vendors" and "exclude_vendors" MUST NOT be set at the
    same time. If user says "not from ASDA", you MUST set "exclude_vendors": ["ASDA"]
    and "vendors": null.
4.  **RESET:** "all shops" or "any vendor" means "vendors": null and "exclude_vendors": null.
5.  **FUZZY MAPPING:** You MUST map common words to allowed product types.
    - "food" or "food items" → product_types: ["sandwich", "bagel", "snack", "salad"]
    - "beverages" or "drinks" → product_types: ["drink"]

{format_instructions}

💡 EXAMPLES OF FLAWLESS INHERITANCE:

Example 1 - (YOUR BUG FIX)
[Previous context: {{"keywords": ["Coke", "Pepsi"], "sort_by": "price_asc"}}]
User: "from subway"
→ {{"vendors": ["Subway"], "exclude_vendors": null, "product_types": ["drink"], "keywords": ["Coke", "Pepsi"], "sort_by": "price_asc"}}
(REASON: "from subway" is added to the context. "keywords" are inherited.)

Example 2 - (INHERIT)
[Previous context: {{"vendors": ["Subway"], "product_types": ["drink"]}}]
User: "show me vegan items"
→ {{"vendors": ["Subway"], "exclude_vendors": null, "product_types": ["drink"], "tags": ["vegan"], "sort_by": "price_asc"}}
(REASON: "vegan" is added. "vendors" and "product_types" are inherited.)

Example 3 - (OVERRIDE)
[Previous context: {{"vendors": ["Subway"], "keywords": ["Coke"]}}]
User: "no, from asda"
→ {{"vendors": ["ASDA"], "exclude_vendors": null, "product_types": null, "keywords": ["Coke"], "sort_by": "price_asc"}}
(REASON: "vendors" is overridden. "keywords" is inherited.)

Example 4 - (FORGETTING FILTERS)
[Previous context: {{"keywords": ["Coke"], "tags": ["vegan"]}}]
User: "show me sandwiches"
→ {{"vendors": null, "exclude_vendors": null, "product_types": ["sandwich"], "tags": null, "keywords": null, "sort_by": "price_asc"}}
(REASON: "sandwiches" is a new product type, so old "keywords" and "tags" are dropped.)

Example 5 - (NEGATIVE FILTER)
[Previous context: {{"vendors": ["ASDA", "Subway"], "keywords": ["Coke"]}}]
User: "not from asda"
→ {{"vendors": null, "exclude_vendors": ["ASDA"], "product_types": null, "keywords": ["Coke"], "sort_by": "price_asc"}}
(REASON: "exclude_vendors" overrides "vendors". "keywords" is inherited.)

Example 6 - (FUZZY MAPPING + INHERITANCE)
[Previous context: {{"vendors": ["Subway"], "product_types": ["drink"]}}]
User: "food items"
→ {{"vendors": ["Subway"], "exclude_vendors": null, "product_types": ["sandwich", "bagel", "snack", "salad"], "tags": null, "keywords": null, "sort_by": "price_asc"}}
(REASON: "food items" maps to and overrides "product_types". The "vendors" context is inherited.)

Now parse the user's query:"""),
            ("user", "{user_query}")
        ])
        
    def translate(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> ProductQuery:
        """
        SIMPLE: User input → Gemini → JSON
        
        Args:
            user_query: User's natural language input
            context: Previous conversation context (for continuity)
            
        Returns:
            ProductQuery object with structured filters
        """
        # Build context string as JSON block if we have previous conversation
        context_string = ""
        if context:
            ctx = {}
            for key in [
                'vendors', 'exclude_vendors', 'product_types', 'tags',
                'keywords', 'price_filter', 'sort_by', 'brand'
            ]:
                if key in context and context.get(key) is not None:
                    ctx[key] = context.get(key)
            if ctx:
                context_string = f"[Previous context: {json.dumps(ctx)}]\n"
        
        # Combine context + user query
        full_query = f"{context_string}User: {user_query}"
        
        # Format prompt and call Gemini
        formatted_prompt = self.prompt.format_messages(
            format_instructions=self.parser.get_format_instructions(),
            user_query=full_query
        )
        
        response = self.llm.invoke(formatted_prompt)
        
        # Parse JSON response
        try:
            query = self.parser.parse(response.content)
            return query
        except Exception:
            # Return empty query on parse error
            return ProductQuery()

    def translate_to_dict(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Translate query and return as dictionary.
        
        Args:
            user_query: User's natural language input
            context: Optional context from conversation memory
            
        Returns:
            Dictionary with filter parameters
        """
        query = self.translate(user_query, context)
        return query.model_dump(exclude_none=True)
