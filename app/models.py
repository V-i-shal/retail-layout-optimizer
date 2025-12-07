"""SQLAlchemy ORM models for the retail layout optimizer."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base


class StoreSection(Base):
    """Store section with grid coordinates."""
    
    __tablename__ = 'store_section'
    
    section_id = Column(String(10), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    
    # Relationships
    products = relationship('Product', back_populates='current_section')
    movements = relationship('Movement', back_populates='section')
    outgoing_edges = relationship(
        'GraphEdge',
        foreign_keys='GraphEdge.src_section_id',
        back_populates='source_section'
    )
    incoming_edges = relationship(
        'GraphEdge',
        foreign_keys='GraphEdge.dst_section_id',
        back_populates='destination_section'
    )
    community = relationship('SectionCommunity', back_populates='section', uselist=False)
    recommendations = relationship('Recommendation', back_populates='recommended_section')
    
    def __repr__(self):
        return f"<StoreSection(id='{self.section_id}', name='{self.name}', pos=({self.x},{self.y}))>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'section_id': self.section_id,
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'community_id': self.community.community_id if self.community else None
        }


class Product(Base):
    """Product with category and current location."""
    
    __tablename__ = 'product'
    
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    current_section_id = Column(String(10), ForeignKey('store_section.section_id'))
    
    # Relationships
    current_section = relationship('StoreSection', back_populates='products')
    cluster = relationship('ProductCluster', back_populates='product', uselist=False)
    recommendation = relationship('Recommendation', back_populates='product', uselist=False)
    
    def __repr__(self):
        return f"<Product(id={self.product_id}, name='{self.name}', category='{self.category}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'current_section_id': self.current_section_id,
            'cluster_id': self.cluster.cluster_id if self.cluster else None
        }


class Movement(Base):
    """Customer movement record (one step in a path)."""
    
    __tablename__ = 'movement'
    
    path_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), nullable=False)
    step_order = Column(Integer, nullable=False)
    section_id = Column(String(10), ForeignKey('store_section.section_id'), nullable=False)
    ts = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    section = relationship('StoreSection', back_populates='movements')
    
    def __repr__(self):
        return f"<Movement(session='{self.session_id}', step={self.step_order}, section='{self.section_id}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'path_id': self.path_id,
            'session_id': self.session_id,
            'step_order': self.step_order,
            'section_id': self.section_id,
            'timestamp': self.ts.isoformat() if self.ts else None
        }


class GraphEdge(Base):
    """Weighted edge between sections (transition frequency)."""
    
    __tablename__ = 'graph_edge'
    
    src_section_id = Column(String(10), ForeignKey('store_section.section_id'), primary_key=True)
    dst_section_id = Column(String(10), ForeignKey('store_section.section_id'), primary_key=True)
    weight = Column(Float, nullable=False, default=0.0)
    
    # Relationships
    source_section = relationship(
        'StoreSection',
        foreign_keys=[src_section_id],
        back_populates='outgoing_edges'
    )
    destination_section = relationship(
        'StoreSection',
        foreign_keys=[dst_section_id],
        back_populates='incoming_edges'
    )
    
    def __repr__(self):
        return f"<GraphEdge({self.src_section_id} -> {self.dst_section_id}, weight={self.weight:.2f})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'source': self.src_section_id,
            'target': self.dst_section_id,
            'weight': self.weight
        }


class SectionCommunity(Base):
    """Community assignment for sections (graph clustering result)."""
    
    __tablename__ = 'section_community'
    
    section_id = Column(String(10), ForeignKey('store_section.section_id'), primary_key=True)
    community_id = Column(Integer, nullable=False)
    
    # Relationships
    section = relationship('StoreSection', back_populates='community')
    
    def __repr__(self):
        return f"<SectionCommunity(section='{self.section_id}', community={self.community_id})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'section_id': self.section_id,
            'community_id': self.community_id
        }


class ProductCluster(Base):
    """Cluster assignment for products (ML clustering result)."""
    
    __tablename__ = 'product_cluster'
    
    product_id = Column(Integer, ForeignKey('product.product_id'), primary_key=True)
    cluster_id = Column(Integer, nullable=False)
    
    # Relationships
    product = relationship('Product', back_populates='cluster')
    
    def __repr__(self):
        return f"<ProductCluster(product_id={self.product_id}, cluster={self.cluster_id})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'product_id': self.product_id,
            'cluster_id': self.cluster_id
        }


class Recommendation(Base):
    """Product placement recommendation from optimization."""
    
    __tablename__ = 'recommendation'
    
    product_id = Column(Integer, ForeignKey('product.product_id'), primary_key=True)
    recommended_section_id = Column(String(10), ForeignKey('store_section.section_id'), nullable=False)
    rationale = Column(Text)
    score = Column(Float, nullable=False, default=0.0)
    
    # Relationships
    product = relationship('Product', back_populates='recommendation')
    recommended_section = relationship('StoreSection', back_populates='recommendations')
    
    def __repr__(self):
        return f"<Recommendation(product_id={self.product_id}, section='{self.recommended_section_id}', score={self.score:.2f})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'recommended_section_id': self.recommended_section_id,
            'section_name': self.recommended_section.name if self.recommended_section else None,
            'rationale': self.rationale,
            'score': self.score
        }


class RunMetadata(Base):
    """Pipeline run tracking."""
    
    __tablename__ = 'run_metadata'
    
    run_id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text)
    
    def __repr__(self):
        return f"<RunMetadata(id={self.run_id}, created_at={self.created_at})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'run_id': self.run_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes
        }