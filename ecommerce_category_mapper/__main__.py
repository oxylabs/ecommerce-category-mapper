import click
import json
import sys

from ecommerce_category_mapper.mapper import CategoryMapper


@click.command()
@click.option('--domain', required=True, help='Ecommerce domain to map')
@click.option('--api-key', required=True, help='Oxylabs AI Studio API key')
@click.option('--output', '-o', required=True, help='Output file path')
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
@click.option(
    '--render-javascript',
    is_flag=True,
    default=False,
    help='Enable JavaScript rendering for pages (default: False)',
)
def main(
    domain: str, 
    api_key: str, 
    output: str, 
    max_depth: int, 
    max_concurrent: int, 
    delay: float, 
    max_categories: int,
    verbose: bool,
    render_javascript: bool,
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
            render_javascript=render_javascript,
        )
        
        click.echo(f"Starting category mapping for {domain}...")
        
        # Map categories (sync version)
        category_map = mapper.map_categories_sync(domain)
        
        # Write output as JSON
        output_text = json.dumps(category_map.to_dict(), indent=2)
        with open(output, 'w') as f:
            f.write(output_text)
        
        click.echo(f"Results saved to {output}")
        click.echo(f"Mapping completed! Found {category_map.total_categories} categories.")
        
    except KeyboardInterrupt:
        click.echo("\nMapping interrupted by user.")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
