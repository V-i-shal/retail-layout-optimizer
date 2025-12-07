"""Load CSV data into MySQL database."""
import pandas as pd
from pathlib import Path
import logging
from typing import Optional

from app.db import session_scope
from app.models import Movement, Product
from app.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_paths_df(df: pd.DataFrame) -> bool:
    """Validate customer paths DataFrame schema.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        bool: True if valid, raises ValueError otherwise
    """
    required_cols = ['session_id', 'step_order', 'section_id', 'timestamp']
    
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    # Check data types
    if not pd.api.types.is_string_dtype(df['session_id']):
        raise ValueError("session_id must be string type")
    
    if not pd.api.types.is_integer_dtype(df['step_order']):
        raise ValueError("step_order must be integer type")
    
    logger.info(f"✓ Paths DataFrame validated: {len(df)} rows")
    return True


def validate_products_df(df: pd.DataFrame) -> bool:
    """Validate products DataFrame schema.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        bool: True if valid, raises ValueError otherwise
    """
    required_cols = ['name', 'category', 'current_section_id']
    
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    logger.info(f"✓ Products DataFrame validated: {len(df)} rows")
    return True


def load_paths_to_db(
    csv_path: Optional[Path] = None,
    df: Optional[pd.DataFrame] = None,
    clear_existing: bool = False
) -> int:
    """Load customer paths from CSV to database.
    
    Args:
        csv_path: Path to CSV file (default: data/sample_paths.csv)
        df: DataFrame to load (if provided, csv_path is ignored)
        clear_existing: If True, delete existing movement records
    
    Returns:
        int: Number of records inserted
    """
    if df is None:
        if csv_path is None:
            csv_path = Config.DATA_DIR / 'sample_paths.csv'
        
        logger.info(f"Loading paths from {csv_path}...")
        df = pd.read_csv(csv_path)
    
    # Validate
    validate_paths_df(df)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    with session_scope() as session:
        # Clear existing if requested
        if clear_existing:
            deleted = session.query(Movement).delete()
            logger.info(f"Deleted {deleted} existing movement records")
        
        # Insert records in batches
        batch_size = 1000
        records_inserted = 0
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            movements = [
                Movement(
                    session_id=row['session_id'],
                    step_order=row['step_order'],
                    section_id=row['section_id'],
                    ts=row['timestamp']
                )
                for _, row in batch.iterrows()
            ]
            
            session.bulk_save_objects(movements)
            records_inserted += len(movements)
            
            if (i // batch_size + 1) % 5 == 0:
                logger.info(f"  Inserted {records_inserted}/{len(df)} records...")
        
        session.commit()
    
    logger.info(f"✓ Loaded {records_inserted} movement records to database")
    return records_inserted


def load_products_to_db(
    csv_path: Optional[Path] = None,
    df: Optional[pd.DataFrame] = None,
    clear_existing: bool = False
) -> int:
    """Load products from CSV to database.
    
    Args:
        csv_path: Path to CSV file (default: data/sample_products.csv)
        df: DataFrame to load (if provided, csv_path is ignored)
        clear_existing: If True, delete existing product records
    
    Returns:
        int: Number of records inserted
    """
    if df is None:
        if csv_path is None:
            csv_path = Config.DATA_DIR / 'sample_products.csv'
        
        logger.info(f"Loading products from {csv_path}...")
        df = pd.read_csv(csv_path)
    
    # Validate
    validate_products_df(df)
    
    with session_scope() as session:
        # Clear existing if requested
        if clear_existing:
            deleted = session.query(Product).delete()
            logger.info(f"Deleted {deleted} existing product records")
        
        # Insert records
        products = [
            Product(
                name=row['name'],
                category=row['category'],
                current_section_id=row['current_section_id']
            )
            for _, row in df.iterrows()
        ]
        
        session.bulk_save_objects(products)
        session.commit()
    
    logger.info(f"✓ Loaded {len(products)} products to database")
    return len(products)


def ingest_all(clear_existing: bool = False):
    """Load all CSV data to database.
    
    Args:
        clear_existing: If True, clear existing data before loading
    """
    logger.info("Starting data ingestion...")
    
    # Load paths
    n_paths = load_paths_to_db(clear_existing=clear_existing)
    
    # Load products
    n_products = load_products_to_db(clear_existing=clear_existing)
    
    logger.info("✓ Data ingestion complete!")
    logger.info(f"  - Movements: {n_paths}")
    logger.info(f"  - Products: {n_products}")


if __name__ == '__main__':
    ingest_all(clear_existing=True)