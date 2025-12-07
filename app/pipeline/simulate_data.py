"""Generate realistic synthetic data for customer paths and products."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging

from app.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set random seed for reproducibility
np.random.seed(Config.RANDOM_SEED)


def generate_customer_paths(
    n_sessions: int = 10000,
    sections: list = None,
    output_path: Path = None
) -> pd.DataFrame:
    """Generate realistic customer movement paths.
    
    Args:
        n_sessions: Number of customer sessions to generate
        sections: List of section IDs (default: A-Z)
        output_path: Path to save CSV (default: data/sample_paths.csv)
    
    Returns:
        DataFrame with columns: session_id, step_order, section_id, timestamp
    """
    if sections is None:
        sections = [chr(65 + i) for i in range(26)]  # A-Z
    
    if output_path is None:
        output_path = Config.DATA_DIR / 'sample_paths.csv'
    
    logger.info(f"Generating {n_sessions} customer path sessions...")
    
    # Define section weights (realistic shopping patterns)
    # Entrance (A) and Checkout (M) have higher traffic
    section_weights = np.ones(len(sections))
    section_weights[0] = 3.0  # Entrance (A)
    section_weights[12] = 3.0  # Checkout (M)
    section_weights[1:5] = 2.0  # Fresh sections (B-E) higher traffic
    section_weights = section_weights / section_weights.sum()
    
    # Community structure (sections that are often visited together)
    communities = {
        'fresh': ['B', 'C', 'D', 'E', 'F', 'G'],  # Produce, bakery, dairy, frozen, meat, deli
        'pantry': ['H', 'I', 'J', 'K'],  # Beverages, snacks, canned, condiments
        'household': ['L', 'O', 'Q', 'R'],  # Household, pet, cleaning, paper
        'specialty': ['N', 'P', 'S', 'T', 'U', 'V', 'W', 'X']  # Health, baby, pharmacy, etc.
    }
    
    all_paths = []
    base_time = datetime(2024, 1, 1, 9, 0, 0)
    
    for session_idx in range(n_sessions):
        session_id = f"sess_{session_idx:06d}"
        
        # Path length: 3-15 steps (most customers visit 5-8 sections)
        path_length = int(np.random.gamma(3, 2)) + 3
        path_length = min(path_length, 15)
        
        # Start time (spread across operating hours)
        session_start = base_time + timedelta(
            days=np.random.randint(0, 30),
            hours=np.random.randint(0, 12),
            minutes=np.random.randint(0, 60)
        )
        
        # Most paths start at entrance (A)
        if np.random.random() < 0.8:
            path = ['A']
        else:
            path = [np.random.choice(sections[:10])]  # Sometimes start elsewhere
        
        # Choose a primary community for this session
        primary_community = np.random.choice(list(communities.keys()))
        community_sections = communities[primary_community]
        
        # Generate path
        current_time = session_start
        for step in range(1, path_length):
            # 70% chance to stay in primary community, 30% to explore
            if np.random.random() < 0.7 and len(community_sections) > 0:
                # Stay in community (avoid immediate repeats)
                candidates = [s for s in community_sections if s != path[-1]]
                if candidates:
                    next_section = np.random.choice(candidates)
                else:
                    next_section = np.random.choice(sections)
            else:
                # Explore other sections
                next_section = np.random.choice(sections, p=section_weights)
            
            path.append(next_section)
            
            # Time between steps: 30 seconds to 5 minutes
            current_time += timedelta(seconds=np.random.randint(30, 300))
        
        # Most paths end at checkout (M)
        if np.random.random() < 0.7 and path[-1] != 'M':
            path.append('M')
            current_time += timedelta(seconds=np.random.randint(30, 180))
        
        # Create records for this session
        for step_order, section_id in enumerate(path):
            all_paths.append({
                'session_id': session_id,
                'step_order': step_order,
                'section_id': section_id,
                'timestamp': current_time + timedelta(seconds=step_order * 60)
            })
    
    # Create DataFrame
    df = pd.DataFrame(all_paths)
    
    # Save to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    logger.info(f"✓ Generated {len(df)} movement records from {n_sessions} sessions")
    logger.info(f"✓ Saved to {output_path}")
    
    return df


def generate_products(
    n_products: int = 100,
    sections: list = None,
    output_path: Path = None
) -> pd.DataFrame:
    """Generate product catalog with categories and initial placement.
    
    Args:
        n_products: Number of products to generate
        sections: List of section IDs for placement
        output_path: Path to save CSV (default: data/sample_products.csv)
    
    Returns:
        DataFrame with columns: product_id, name, category, current_section_id
    """
    if sections is None:
        sections = [chr(65 + i) for i in range(26)]  # A-Z
    
    if output_path is None:
        output_path = Config.DATA_DIR / 'sample_products.csv'
    
    logger.info(f"Generating {n_products} products...")
    
    # Product categories and typical section mappings
    categories = {
        'Produce': ['B'],
        'Bakery': ['C'],
        'Dairy': ['D'],
        'Frozen': ['E'],
        'Meat': ['F'],
        'Deli': ['G'],
        'Beverages': ['H'],
        'Snacks': ['I'],
        'Canned Goods': ['J'],
        'Condiments': ['K'],
        'Household': ['L'],
        'Health & Beauty': ['N'],
        'Pet Supplies': ['O'],
        'Baby Products': ['P'],
        'Cleaning': ['Q'],
        'Paper Products': ['R'],
        'Pharmacy': ['S'],
        'Electronics': ['T'],
        'Books': ['U'],
        'Toys': ['V']
    }
    
    # Product name templates
    product_templates = {
        'Produce': ['Organic {}', 'Fresh {}', '{} Bundle'],
        'Bakery': ['{} Bread', '{} Pastry', '{} Cake'],
        'Dairy': ['{} Milk', '{} Cheese', '{} Yogurt'],
        'Frozen': ['Frozen {}', '{} Ice Cream', '{} Pizza'],
        'Meat': ['{} Chicken', '{} Beef', '{} Pork'],
        'Deli': ['Sliced {}', '{} Ham', '{} Turkey'],
        'Beverages': ['{} Juice', '{} Soda', '{} Water'],
        'Snacks': ['{} Chips', '{} Crackers', '{} Nuts'],
        'Canned Goods': ['Canned {}', '{} Soup', '{} Beans'],
        'Condiments': ['{} Sauce', '{} Dressing', '{} Ketchup'],
        'Household': ['{} Detergent', '{} Cleaner', '{} Soap'],
        'Health & Beauty': ['{} Shampoo', '{} Lotion', '{} Toothpaste'],
        'Pet Supplies': ['{} Dog Food', '{} Cat Food', '{} Pet Treats'],
        'Baby Products': ['{} Diapers', '{} Baby Food', '{} Wipes'],
        'Cleaning': ['{} Mop', '{} Broom', '{} Vacuum Bags'],
        'Paper Products': ['{} Towels', '{} Napkins', '{} Tissue'],
        'Pharmacy': ['{} Medicine', '{} Vitamins', '{} First Aid'],
        'Electronics': ['{} Batteries', '{} Charger', '{} Headphones'],
        'Books': ['{} Magazine', '{} Novel', '{} Cookbook'],
        'Toys': ['{} Puzzle', '{} Game', '{} Action Figure']
    }
    
    adjectives = ['Premium', 'Value', 'Family Size', 'Single Serve', 'Large', 
                  'Small', 'Economy', 'Deluxe', 'Classic', 'Special']
    
    products = []
    product_id = 1
    
    # Distribute products across categories
    products_per_category = n_products // len(categories)
    
    for category, typical_sections in categories.items():
        templates = product_templates.get(category, ['{} Item'])
        
        for _ in range(products_per_category):
            # Generate product name
            template = np.random.choice(templates)
            adjective = np.random.choice(adjectives)
            name = template.format(adjective)
            
            # Assign to typical section (with some randomness)
            if np.random.random() < 0.8 and typical_sections:
                section = np.random.choice(typical_sections)
            else:
                # Sometimes products are misplaced
                section = np.random.choice(sections[1:13])  # Avoid entrance/checkout
            
            products.append({
                'product_id': product_id,
                'name': name,
                'category': category,
                'current_section_id': section
            })
            product_id += 1
    
    # Fill remaining products if needed
    while len(products) < n_products:
        category = np.random.choice(list(categories.keys()))
        templates = product_templates.get(category, ['{} Item'])
        template = np.random.choice(templates)
        adjective = np.random.choice(adjectives)
        name = template.format(adjective)
        section = np.random.choice(sections[1:13])
        
        products.append({
            'product_id': product_id,
            'name': name,
            'category': category,
            'current_section_id': section
        })
        product_id += 1
    
    # Create DataFrame
    df = pd.DataFrame(products)
    
    # Save to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    logger.info(f"✓ Generated {len(df)} products across {len(categories)} categories")
    logger.info(f"✓ Saved to {output_path}")
    
    return df


def main():
    """Generate all sample data."""
    logger.info("Starting data simulation...")
    
    # Generate customer paths
    paths_df = generate_customer_paths(
        n_sessions=10000,
        output_path=Config.DATA_DIR / 'sample_paths.csv'
    )
    
    # Generate products
    products_df = generate_products(
        n_products=100,
        output_path=Config.DATA_DIR / 'sample_products.csv'
    )
    
    logger.info("✓ Data simulation complete!")
    logger.info(f"  - Paths: {len(paths_df)} records")
    logger.info(f"  - Products: {len(products_df)} items")


if __name__ == '__main__':
    main()