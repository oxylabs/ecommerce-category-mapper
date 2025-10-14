"""
Ecommerce Category Mapper

A tool for mapping ecommerce website categories using Oxylabs AI Studio tools.
"""

from .mapper import CategoryMapper
from .models import Category, CategoryMap

__version__ = "0.1.0"
__all__ = ["CategoryMapper", "Category", "CategoryMap"]
