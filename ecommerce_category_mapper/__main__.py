import click
import json
import sys

from ecommerce_category_mapper.mapper import CategoryMapper


def _format_pretty_output(category_map) -> str:
    """Format output in a human-readable way."""
    output = []
    output.append(f"Category Map for {category_map.domain}")
    output.append("=" * 50)
    output.append(f"Total Categories: {category_map.total_categories}")
    output.append("")
    
    # Group by level
    for level in range(max(cat.level for cat in category_map.categories) + 1):
        categories_at_level = [cat for cat in category_map.categories if cat.level == level]
        if categories_at_level:
            output.append(f"Level {level} Categories:")
            for cat in categories_at_level:
                indent = "  " * level
                breadcrumb_str = " > ".join(cat.category_breadcrumbs)
                output.append(f"{indent}- {cat.category_name}")
                output.append(f"{indent}  URL: {cat.category_url}")
                output.append(f"{indent}  Breadcrumbs: {breadcrumb_str}")
                if cat.parent_category_url:
                    output.append(f"{indent}  Parent: {cat.parent_category_url}")
                output.append("")
    
    return "\n".join(output)


@click.command()
@click.option('--domain', required=True, help='Ecommerce domain to map')
@click.option('--api-key', required=True, help='Oxylabs AI Studio API key')
@click.option('--output', '-o', help='Output file path (default: stdout)')
@click.option(
    '--format', 
    'output_format', 
    type=click.Choice(['json', 'pretty']), 
    default='json', 
    help='Output format (default: json)',
)
@click.option(
    '--max-depth', 
    type=int, 
    default=2, 
    help='Maximum depth to explore subcategories (default: 2)',
)
@click.option(
    '--max-concurrent', 
    type=int, 
    default=5, 
    help='Maximum concurrent requests (default: 5)',
)
@click.option(
    '--delay', 
    type=float, 
    default=1.0, 
    help='Delay between requests in seconds (default: 1.0)',
)
@click.option(
    '--max-categories', 
    type=int, 
    default=100, 
    help='Maximum number of categories to extract (default: 100)',
)
@click.option(
    '--verbose', 
    '-v', 
    is_flag=True, 
    help='Enable verbose logging',
)
def main(
    domain: str, 
    api_key: str, 
    output: str, 
    output_format: str, 
    max_depth: int, 
    max_concurrent: int, 
    delay: float, 
    max_categories: int,
    verbose: bool,
) -> None:
    """Map ecommerce website categories using Oxylabs AI Studio tools."""
    
    # Setup logging
    import logging
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize mapper
        mapper = CategoryMapper(
            api_key=api_key,
            max_depth=max_depth,
            delay_between_requests=delay,
            max_concurrent_requests=max_concurrent,
            max_categories=max_categories,
        )
        
        click.echo(f"Starting category mapping for {domain}...")
        
        # Map categories (sync version)
        category_map = mapper.map_categories_sync(domain)
        
        # Prepare output
        if output_format == "pretty":
            output_text = _format_pretty_output(category_map)
        else:
            output_text = json.dumps(category_map.to_dict(), indent=2)
        
        # Write output
        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            click.echo(f"Results saved to {output}")
        else:
            click.echo(output_text)
            
        click.echo(f"\nMapping completed! Found {category_map.total_categories} categories.")
        
    except KeyboardInterrupt:
        click.echo("\nMapping interrupted by user.")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
