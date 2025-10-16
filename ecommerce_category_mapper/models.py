"""
Data models for ecommerce category mapping.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Category(BaseModel):
    """Represents a single category in the ecommerce site."""
    
    category_name: str = Field(..., description="Name of the category")
    category_breadcrumbs: List[str] = Field(..., description="Breadcrumb path to this category")
    category_url: str = Field(..., description="URL of the category page")
    parent_category_url: Optional[str] = Field(None, description="URL of the parent category, if any")
    level: int = Field(..., description="Depth level of the category (0 for root categories)")


class CategoryMap(BaseModel):
    """Complete category mapping for an ecommerce site."""
    
    domain: str = Field(..., description="Domain of the ecommerce site")
    categories: List[Category] = Field(..., description="List of all discovered categories")
    total_categories: int = Field(..., description="Total number of categories found")
    
    def get_categories_by_level(self, level: int) -> list[Category]:
        """Get all categories at a specific level."""
        return [cat for cat in self.categories if cat.level == level]
    
    def get_root_categories(self) -> list[Category]:
        """Get all root categories (level 0)."""
        return self.get_categories_by_level(0)
    
    def get_children(self, parent_url: str) -> list[Category]:
        """Get all direct children of a parent category."""
        return [cat for cat in self.categories if cat.parent_category_url == parent_url]
    
    def to_dict(self) -> dict:
        """Convert to dictionary format as specified in requirements."""
        return {
            "category_map": [
                {
                    "category_name": cat.category_name,
                    "category_breadcrumbs": cat.category_breadcrumbs,
                    "category_url": cat.category_url,
                    "parent_category_url": cat.parent_category_url,
                }
                for cat in self.categories
            ]
        }
