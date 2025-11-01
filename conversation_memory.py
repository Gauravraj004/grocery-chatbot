"""
Conversation Memory Module
Manages conversation context using LangChain memory to remember user preferences.
"""

from typing import Dict, Any, Optional
from langchain.memory import ConversationBufferMemory


class ConversationContext:
    """Manages conversation context and memory for the chatbot."""
    
    def __init__(self):
        """Initialize conversation memory."""
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Track specific context items (now with LIST support)
        self.context: Dict[str, Any] = {
            'vendors': None,          # List of vendors
            'exclude_vendors': None,  # List of vendors to exclude
            'product_types': None,    # List of product types
            'tags': None,             # List of tags
            'price_filter': None,     # Price filter dict {operator, value}
            'sort_by': None,          # Sort preference: 'price_asc'|'price_desc'|'name'
            'keywords': None,         # List of keywords
            'brand': None,            # Brand string
            'last_query': None        # Last structured query
        }
    
    def update_context(self, user_input: str, structured_query: Dict[str, Any]):
        """
        Update context based on user input and parsed query.
        This "dumb" version trusts the AI (QueryTranslator) to be the
        single source of truth for the entire context state.
        
        Args:
            user_input: Raw user input
            structured_query: The complete new query state from the AI
        """
        # Save the user message to LangChain's memory
        self.memory.chat_memory.add_user_message(user_input)

        # AI owns the context; we simply mirror what it returns
        self.context['vendors'] = structured_query.get('vendors')
        self.context['exclude_vendors'] = structured_query.get('exclude_vendors')
        self.context['product_types'] = structured_query.get('product_types')
        self.context['tags'] = structured_query.get('tags')
        self.context['price_filter'] = structured_query.get('price_filter')
        self.context['sort_by'] = structured_query.get('sort_by')
        self.context['keywords'] = structured_query.get('keywords')
        self.context['brand'] = structured_query.get('brand')

        # Store the complete last query for debugging or re-running
        self.context['last_query'] = structured_query
    
    def add_ai_response(self, response: str):
        """
        Add AI response to memory.
        
        Args:
            response: The chatbot's response text
        """
        self.memory.chat_memory.add_ai_message(response)
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get current conversation context.
        
        Returns:
            Dictionary with current context values
        """
        return self.context.copy()
    
    def check_for_context_command(self, user_input: str) -> Optional[str]:
        """
        Check if user is asking to reset conversation. AI handles all other context logic.
        
        Args:
            user_input: User's input text
            
        Returns:
            'reset' if user wants to reset, None otherwise
        """
        user_input_lower = user_input.lower().strip()
        
        if user_input_lower in ['reset', 'clear', 'start over', 'new search']:
            return 'reset'
        
        return None
    
    def reset(self):
        """Clear all conversation memory and context."""
        self.memory.clear()
        self.context = {
            'vendors': None,
            'exclude_vendors': None,
            'product_types': None,
            'tags': None,
            'price_filter': None,
            'sort_by': None,
            'keywords': None,
            'brand': None,
            'last_query': None
        }
    
    def get_context_summary(self) -> str:
        """
        Get a human-readable summary of current context.
        
        Returns:
            Summary string
        """
        parts = []
        
        if self.context['vendors']:
            vendor_str = ', '.join(self.context['vendors'])
            parts.append(f"Shop: {vendor_str}")
        
        if self.context['exclude_vendors']:
            exclude_str = ', '.join(self.context['exclude_vendors'])
            parts.append(f"Excluding: {exclude_str}")
        
        if self.context['product_types']:
            type_str = ', '.join(self.context['product_types'])
            parts.append(f"Type: {type_str}")
        
        if self.context['tags']:
            parts.append(f"Tags: {', '.join(self.context['tags'])}")
        
        # Price/budget summary
        pf = self.context.get('price_filter')
        sort_by = self.context.get('sort_by')
        if pf:
            op = pf.get('operator')
            val = pf.get('value')
            if op == '<':
                parts.append(f"Price: under £{val}")
            elif op == '<=':
                parts.append(f"Price: ≤ £{val}")
            elif op == '>':
                parts.append(f"Price: over £{val}")
            elif op == '>=':
                parts.append(f"Price: ≥ £{val}")
            elif op == '==':
                parts.append(f"Price: = £{val}")
        elif sort_by == 'price_desc':
            parts.append("Budget: expensive")
        elif sort_by == 'price_asc':
            parts.append("Budget: cheap")

        if parts:
            return "📌 Context: " + " | ".join(parts)
        else:
            return ""
    
    def has_active_context(self) -> bool:
        """
        Check if there's any active context.
        
        Returns:
            True if any context is set
        """
        return any([
            self.context['vendors'],
            self.context['exclude_vendors'],
            self.context['product_types'],
            self.context['tags'],
            self.context['price_filter'],
            self.context.get('sort_by') == 'price_desc'
        ])
