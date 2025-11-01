"""
Product Search Engine Module
Performs accurate, rule-based filtering on product data based on structured queries.
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class ProductSearchEngine:
    """Filters and searches product data based on structured query filters."""
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize the search engine with product data.
        
        Args:
            data_directory: Path to directory containing JSON product files
        """
        self.products = []
        self.data_directory = data_directory
        self.load_all_products()
    
    def load_all_products(self):
        """Load all product JSON files from the data directory."""
        data_path = Path(self.data_directory)
        
        if not data_path.exists():
            return
        
        json_files = list(data_path.glob("*.json"))
        
        if not json_files:
            return
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    products = json.load(f)
                    self.products.extend(products)
            except Exception:
                # Silently skip files with errors
                pass
        
    # Loaded products (quiet mode for production logs)
    
    def search(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search products with flexible LIST support for vendors and product types.
        
        Args:
            query: Dictionary with filter parameters (supports lists)
            limit: Maximum number of results to return
            
        Returns:
            List of matching products with relevance information
        """
        if not self.products:
            return []
        
        # Start with all products
        filtered_products = self.products.copy()
        
        # Apply vendors filter (LIST support - match ANY vendor in list)
        if query.get('vendors'):
            vendors = query['vendors']
            filtered_products = [p for p in filtered_products if p['vendor'] in vendors]
        
        # Apply vendor exclusion filter (LIST support - exclude ALL vendors in list)
        if query.get('exclude_vendors'):
            exclude_vendors = query['exclude_vendors']
            filtered_products = [p for p in filtered_products if p['vendor'] not in exclude_vendors]
        
        # Apply product types filter (LIST support - match ANY type in list)
        if query.get('product_types'):
            product_types = query['product_types']
            filtered_products = [p for p in filtered_products if p['category'] in product_types]
        
        # Apply brand filter
        if query.get('brand'):
            brand = query['brand'].lower()
            filtered_products = [
                p for p in filtered_products 
                if brand in p['brand'].lower()
            ]
        
        # Apply tags filter (product must have ALL specified tags)
        if query.get('tags'):
            tags = query['tags']
            filtered_products = [
                p for p in filtered_products
                if all(tag in p.get('tags', []) for tag in tags)
            ]
        
        # Apply price filter
        if query.get('price_filter'):
            price_filter = query['price_filter']
            operator = price_filter['operator']
            value = price_filter['value']
            
            if operator == '<':
                filtered_products = [p for p in filtered_products if p['price'] < value]
            elif operator == '<=':
                filtered_products = [p for p in filtered_products if p['price'] <= value]
            elif operator == '>':
                filtered_products = [p for p in filtered_products if p['price'] > value]
            elif operator == '>=':
                filtered_products = [p for p in filtered_products if p['price'] >= value]
            elif operator == '==':
                filtered_products = [p for p in filtered_products if p['price'] == value]
        
        # Apply keyword search (OR logic - match any keyword)
        if query.get('keywords'):
            keywords = [kw.lower() for kw in query['keywords']]
            filtered_products = [
                p for p in filtered_products
                if any(kw in p['name'].lower() or kw in p['brand'].lower() for kw in keywords)
            ]
        
        # Sort results
        sort_by = query.get('sort_by', 'price_asc')
        
        if sort_by == 'price_asc':
            filtered_products.sort(key=lambda p: p['price'])
        elif sort_by == 'price_desc':
            filtered_products.sort(key=lambda p: p['price'], reverse=True)
        elif sort_by == 'name':
            filtered_products.sort(key=lambda p: p['name'])
        
        # Limit results
        results = filtered_products[:limit]
        
        # Add relevance information to results
        enriched_results = []
        for product in results:
            enriched = product.copy()
            
            # Generate a reason for why this product was selected
            reasons = []
            
            if query.get('vendors'):
                reasons.append(f"from {product['vendor']}")
            
            if query.get('price_filter'):
                pf = query['price_filter']
                op = pf['operator']
                val = pf['value']
                if op == '<':
                    reasons.append(f"under £{val}")
                elif op == '<=':
                    reasons.append(f"≤ £{val}")
                elif op == '>':
                    reasons.append(f"over £{val}")
                elif op == '>=':
                    reasons.append(f"≥ £{val}")
                elif op == '==':
                    reasons.append(f"= £{val}")
            
            if query.get('tags'):
                tag_str = ", ".join(query['tags'])
                reasons.append(f"{tag_str}")
            
            if sort_by == 'price_asc' and not query.get('price_filter'):
                if product == results[0]:
                    reasons.append("cheapest option")
            if sort_by == 'price_desc' and not query.get('price_filter'):
                if product == results[0]:
                    reasons.append("most expensive option")
            
            enriched['reason'] = " · ".join(reasons) if reasons else "matches your criteria"
            enriched_results.append(enriched)
        
        return enriched_results
    
    def get_vendors(self) -> List[str]:
        """Get list of unique vendors in the dataset."""
        return list(set(p['vendor'] for p in self.products))
    
    def get_categories(self) -> List[str]:
        """Get list of unique product categories."""
        return list(set(p['category'] for p in self.products))
    
    def get_all_tags(self) -> List[str]:
        """Get list of all unique tags in the dataset."""
        tags = set()
        for product in self.products:
            tags.update(product.get('tags', []))
        return list(tags)

