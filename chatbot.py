"""
Grocery Chatbot - Backend core
Provides the chat() API for the Flask server; no CLI/console prints.
"""

import os
from query_translator import QueryTranslator
from product_search import ProductSearchEngine
from conversation_memory import ConversationContext


class GroceryChatbot:
    """Main chatbot class integrating all components."""
    
    def __init__(self, api_key: str | None = None, data_directory: str = "data"):
        """
        Initialize the grocery chatbot.
        
        Args:
            api_key: Google Gemini API key (optional, will try to load from env)
            data_directory: Path to product data directory
        """
        # Get API key from parameter or environment
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY must be set in environment or passed to constructor")
        
        # Initialize components
        self.translator = QueryTranslator(api_key=api_key)
        self.search_engine = ProductSearchEngine(data_directory)
        self.context = ConversationContext()
        
        # Ready for API use (no console prints)
    
    
    def chat(self, user_input: str) -> dict:
        """
        Process a chat message and return structured response for API.
        
        Args:
            user_input: User's message
            
        Returns:
            Dictionary with message, products, and filters
        """
        try:
            # Check for special commands
            command = self.context.check_for_context_command(user_input)
            
            if command == 'reset':
                self.context.reset()
                return {
                    'message': "🔄 Context cleared! Starting fresh conversation.",
                    'products': [],
                    'filters_used': {}
                }
            
            elif command == 'vendor_context':
                # Get updated context after vendor was set
                current_context = self.context.get_context()
                
                # If there's a previous query, re-run it with new vendor context
                if current_context.get('last_query'):
                    # Merge previous query with new vendor context
                    structured_query = current_context['last_query'].copy()
                    structured_query['vendors'] = current_context.get('vendors')
                    
                    # Search with updated context
                    results = self.search_engine.search(structured_query, limit=3)
                    
                    # Format message
                    if results:
                        count = len(results)
                        context_msg = self.context.get_context_summary()
                        message = f"{context_msg}\n\n🎯 Found {count} product{'s' if count != 1 else ''} matching your search"
                    else:
                        message = "😕 No products found from this shop matching your criteria."
                    
                    self.context.add_ai_response(message)
                    
                    return {
                        'message': message,
                        'products': results,
                        'filters_used': structured_query
                    }
                else:
                    # No previous query, just acknowledge context update
                    context_msg = self.context.get_context_summary()
                    return {
                        'message': f"✅ Context updated!\n{context_msg}\n\nWhat would you like to search for?",
                        'products': [],
                        'filters_used': current_context
                    }
            
            # Get current context
            current_context = self.context.get_context()
            
            # Translate query to structured format
            structured_query = self.translator.translate_to_dict(user_input, current_context)
            
            # Update conversation context
            self.context.update_context(user_input, structured_query)
            
            # Search products (limit to 3 items for cleaner display)
            results = self.search_engine.search(structured_query, limit=3)
            
            # Format message
            if results:
                count = len(results)
                message = f"🎯 Found {count} product{'s' if count != 1 else ''} matching your search"
                
                # Add context info if active
                if self.context.has_active_context():
                    context_summary = self.context.get_context_summary()
                    message = f"{context_summary}\n\n{message}"
            else:
                message = "😕 No products found matching your criteria. Try adjusting your search!"
            
            # Save AI response to memory
            self.context.add_ai_response(message)
            
            return {
                'message': message,
                'products': results,
                'filters_used': structured_query
            }
            
        except Exception as e:
            return {
                'message': f"❌ Error processing request: {str(e)}",
                'products': [],
                'filters_used': {}
            }
    
    def reset_conversation(self):
        """Reset the conversation context."""
        self.context.reset()
