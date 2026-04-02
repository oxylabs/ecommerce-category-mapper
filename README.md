# Ecommerce Category Mapper

[![AI-Studio Python (1)](https://github.com/oxylabs/ecommerce-category-mapper/blob/main/Ai-Studio2.png)](https://aistudio.oxylabs.io/?utm_source=877&utm_medium=affiliate&utm_campaign=ai_studio&groupid=877&utm_content=ai-studio-js-github&transaction_id=102f49063ab94276ae8f116d224b67) 

A powerful tool for mapping ecommerce website categories using Oxylabs AI Studio tools. This package automatically discovers and maps all categories, subcategories, and their hierarchical relationships for any ecommerce website.

What problems does it solve?

- URL gathering for ecommerce product categories without writing custom code for each website.
- Creates hierarchy of products, basically mapping the website URLs.

[![](https://dcbadge.limes.pink/api/server/Pds3gBmKMH?style=for-the-badge&theme=discord)](https://discord.gg/Pds3gBmKMH) [![YouTube](https://img.shields.io/badge/YouTube-Oxylabs-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@oxylabs)

## 🚀 Key features

- **AI-Powered Discovery**: Uses AI Scraper to intelligently extract categories from any ecommerce site
- **Recursive Exploration**: Automatically explores subcategories based on LLM decisions
- **Universal Compatibility**: Works with any ecommerce website structure
- **Hierarchical Mapping**: Discovers parent-child relationships between categories
- **Breadcrumb Generation**: Automatically generates breadcrumb paths from parent-child relationships
- **Rate Limiting**: Built-in concurrent request limiting and retry mechanism
- **Async Processing**: High-performance concurrent category processing

🤖 How it works

- **AI-Scraper**: Gets all top level categories.
- **AI-Scraper**: Asynchroniously explores each top level category.
- **Final output**: Structured json with a mapped tree of products within the domain.

## ✅ Prerequisites

Before you begin, make sure you have Oxylabs AI studio API key. Obtain your API key from [Oxylabs AI Studio](https://aistudio.oxylabs.io/settings/api-key). (1000 credits free).

## Installation

- Open your terminal.
- Install the uv package manager:
  ```bash
  # macOS and Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Clone the repository:
  ```bash
  git clone https://github.com/oxylabs/ecommerce-category-mapper.git
  ```
- Navigate to the repository:
  ```bash
  cd ecommerce-category-mapper
  ```
- Install the dependencies:
  ```bash
  uv sync
  ```
- Enable the environment:
  ```bash
  source .venv/bin/activate
  ```


## Quick Start

### Command Line Usage

```bash
# Basic usage (output file is required)
python -m ecommerce_category_mapper https://example-store.com --api-key YOUR_API_KEY --output categories.json

# Advanced configuration
python -m ecommerce_category_mapper https://example-store.com --api-key YOUR_API_KEY --output categories.json --max-depth 4 --max-concurrent 8 --delay 0.5 --max-categories 200 --verbose

# With JavaScript rendering (for dynamic websites)
python -m ecommerce_category_mapper https://example-store.com --api-key YOUR_API_KEY --output categories.json --render-javascript

# Help
python -m ecommerce_category_mapper --help
```

### Python API Usage

```python
import asyncio
from ecommerce_category_mapper import CategoryMapper

async def main():
    # Initialize mapper
    mapper = CategoryMapper(
        api_key="your-api-key",
        max_depth=2,  # This will increase amount of requests (and credit cost) exponentially
        delay_between_requests=1.0,  # Delay between requests
        max_concurrent_requests=5,  # Max concurrent requests
        max_categories=100,  # Maximum categories to extract
        render_javascript=False  # Enable for dynamic websites
    )

    # Map categories (async)
    category_map = await mapper.map_categories("https://example-store.com")

    # Access results
    print(f"Found {category_map.total_categories} categories")

    # Get root categories
    root_categories = category_map.get_root_categories()

    # Export to required format
    result = category_map.to_dict()

# Run async example
asyncio.run(main())

# Or use sync version
def sync_example():
    mapper = CategoryMapper(api_key="your-api-key")
    category_map = mapper.map_categories_sync("https://example-store.com")
    return category_map

# Run sync example
sync_example()
```

## Output Format

The tool generates a structured mapping of all categories:

```json
{
  "category_map": [
    {
      "category_name": "Electronics",
      "category_breadcrumbs": ["Electronics"],
      "category_url": "https://example.com/electronics",
      "parent_category_url": null
    },
    {
      "category_name": "Smartphones",
      "category_breadcrumbs": ["Electronics", "Smartphones"],
      "category_url": "https://example.com/electronics/smartphones",
      "parent_category_url": "https://example.com/electronics"
    }
  ]
}
```

## Configuration Options

- `api_key`: Your Oxylabs AI Studio API key (required)
- `max_depth`: Maximum depth to explore subcategories (default: 2)
- `delay_between_requests`: Delay between requests in seconds (default: 1.0)
- `max_concurrent_requests`: Maximum concurrent requests (default: 5)
- `max_categories`: Maximum number of categories to extract (default: 100)
- `render_javascript`: Whether to render JavaScript on pages (default: False)

## Examples

See the `examples/` directory for more detailed usage examples:

- `simple_usage.py`: Basic usage example

## Requirements

- Python 3.11+
- Oxylabs AI Studio API key

## 📚 Learn more
For a deeper dive into features, integrations, examples, and documentation, visit the [AI Studio](https://aistudio.oxylabs.io/) website.

## 💬 Contact us
If you have questions or need support, reach out to us at support@oxylabs.io, or through live chat, accessible via [Oxylabs Dashboard](https://dashboard.oxylabs.io/en/), or join our [Discord community](https://discord.gg/Pds3gBmKMH). For enterprise-related inquiries, contact your dedicated account manager.
