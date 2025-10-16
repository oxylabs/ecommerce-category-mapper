"""
Simple usage example for the AI Scraper-only approach.
"""

import asyncio
import json
from collections import defaultdict
from ecommerce_category_mapper import CategoryMapper


async def main():
    """Example of using the CategoryMapper."""
    
    # Initialize the mapper with your API key
    api_key = "YOUR_API_KEY_HERE"
    mapper = CategoryMapper(
        api_key=api_key,
        max_depth=2,
        delay_between_requests=1.0,
        max_concurrent_requests=3,
        max_categories=50,
        render_javascript=False  # Set to True for dynamic websites
    )
    
    # Map categories for an ecommerce site
    domain = "https://farmacialoreto.it/"
    
    try:
        # Map categories (async version)
        category_map = await mapper.map_categories(domain)
        
        # Print results
        print(f"\nFound {category_map.total_categories} categories:")
        print("=" * 50)
        
        # Show categories by level
        level_counts = defaultdict(int)
        for cat in category_map.categories:
            level_counts[cat.level] += 1
        
        for level in sorted(level_counts.keys()):
            categories_at_level = category_map.get_categories_by_level(level)
            print(f"\nLevel {level} ({level_counts[level]} categories):")
            
            for cat in categories_at_level[:5]:  # Show first 5
                breadcrumb_str = " > ".join(cat.category_breadcrumbs)
                print(f"  - {cat.category_name}")
                print(f"    Breadcrumbs: {breadcrumb_str}")
                print(f"    URL: {cat.category_url}")
                if cat.parent_category_url:
                    print(f"    Parent: {cat.parent_category_url}")
                print()
            
            if len(categories_at_level) > 5:
                print(f"  ... and {len(categories_at_level) - 5} more categories")
        
        # Get root categories only
        root_categories = category_map.get_root_categories()
        print(f"\nRoot categories ({len(root_categories)}):")
        for cat in root_categories:
            print(f"- {cat.category_name}")
        
        # Export to dictionary format
        result_dict = category_map.to_dict()
        with open("simple_category_map.json", "w") as f:
            json.dump(result_dict, f, indent=2)
        print("\nExported format preview:")
        print(f"Total categories in export: {len(result_dict['category_map'])}")
        
    except Exception as e:
        print(f"Error mapping categories: {str(e)}")


if __name__ == "__main__":
    # Run async example
    asyncio.run(main())