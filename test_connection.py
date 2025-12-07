"""Quick test to verify database connection and models."""
from app.db import test_connection, engine
from app.models import StoreSection, Product
from sqlalchemy import select

print("Testing database connection...")
if test_connection():
    print("✓ Connection successful!")
    
    # Test querying sections
    from app.db import Session
    session = Session()
    
    sections = session.query(StoreSection).limit(5).all()
    print(f"\n✓ Found {len(sections)} sections (showing first 5):")
    for section in sections:
        print(f"  - {section}")
    
    session.close()
    print("\n✓ All tests passed!")
else:
    print("✗ Connection failed! Check your .env file.")