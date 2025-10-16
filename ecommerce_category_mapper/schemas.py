DESCRIPTION = """
Extract product category links from the document. Follow these rules:

1. Act as a literal string copy tool - extract exact substrings from the source document.
2. The URL MUST be copied EXACTLY from inside the parentheses () of a markdown link.
3. NEVER modify the URL - do NOT add, remove, or change any part of it.
4. Do NOT add language codes (/gb/, /en/, etc.) or domain names unless explicitly present.
5. In nested links like [![...](IMAGE_URL)](PAGE_URL), extract the PAGE_URL (not the image).
6. Extract ONLY product category links - skip products, informational pages, user pages, and promotions.
"""
CATEGORY_SCHEMA = {
  "type": "object",
  "properties": {
    "categories": {
    "type": "array",
      "description": DESCRIPTION,
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "The exact visible text associated with the category link."
          },
          "url": {
            "type": "string",
            "description": "The URL copied EXACTLY from markdown parentheses without modification. If id does not include the domain, please add it."
          },
          "breadcrumbs": {
            "type": "array",
            "description": "Breadcrumb path from root to current category, including root(very important) category and current category."
          },
          "parent_category_url": {
            "type": "string",
            "description": "URL of parent category, or null for root categories."
          }
        },
        "required": ["name", "url", "breadcrumbs", "parent_category_url"]
      }
    }
  },
  "required": ["categories"]
}