"""Cluster products based on co-occurrence in customer sessions."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from collections import defaultdict
import logging
from typing import Tuple, Dict

from app.db import session_scope
from app.models import Movement, Product, ProductCluster
from app.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set random seed
np.random.seed(Config.RANDOM_SEED)


def build_product_cooccurrence_matrix() -> Tuple[np.ndarray, list]:
    """Build product co-occurrence matrix from customer sessions.
    
    Simulates transactions by taking last 3 sections visited as a 'basket'.
    
    Returns:
        Tuple of (co-occurrence matrix, product_ids list)
    """
    logger.info("Building product co-occurrence matrix...")
    
    with session_scope() as session:
        # Get all movements
        movements = session.query(Movement).order_by(
            Movement.session_id,
            Movement.step_order
        ).all()
        
        # Get all products
        products = session.query(Product).all()
        product_by_section = defaultdict(list)
        for product in products:
            if product.current_section_id:
                product_by_section[product.current_section_id].append(product.product_id)
        
        logger.info(f"Processing {len(movements)} movements for {len(products)} products...")
        
        # Build sessions (section sequences)
        sessions = defaultdict(list)
        for movement in movements:
            sessions[movement.session_id].append(movement.section_id)
        
        # Create baskets (simulate purchases from last N sections visited)
        baskets = []
        for session_id, section_path in sessions.items():
            # Take last 3-5 sections as a basket
            basket_size = min(len(section_path), np.random.randint(3, 6))
            basket_sections = section_path[-basket_size:]
            
            # Get products from these sections
            basket_products = set()
            for section in basket_sections:
                if section in product_by_section:
                    # Take 1-3 random products from each section
                    section_products = product_by_section[section]
                    n_items = min(len(section_products), np.random.randint(1, 4))
                    sampled = np.random.choice(section_products, size=n_items, replace=False)
                    basket_products.update(sampled)
            
            if basket_products:
                baskets.append(list(basket_products))
        
        logger.info(f"Generated {len(baskets)} simulated baskets")
        
        # Build co-occurrence matrix
        product_ids = [p.product_id for p in products]
        n_products = len(product_ids)
        cooccurrence = np.zeros((n_products, n_products))
        
        product_idx = {pid: idx for idx, pid in enumerate(product_ids)}
        
        for basket in baskets:
            # For each pair of products in basket, increment co-occurrence
            for i, p1 in enumerate(basket):
                for p2 in basket[i+1:]:
                    if p1 in product_idx and p2 in product_idx:
                        idx1, idx2 = product_idx[p1], product_idx[p2]
                        cooccurrence[idx1, idx2] += 1
                        cooccurrence[idx2, idx1] += 1
        
        logger.info(f"✓ Co-occurrence matrix built: {n_products}x{n_products}")
        
        return cooccurrence, product_ids


def find_optimal_k(X: np.ndarray, k_range: range = range(3, 11)) -> int:
    """Find optimal number of clusters using silhouette score.
    
    Args:
        X: Feature matrix
        k_range: Range of k values to try
    
    Returns:
        Optimal k value
    """
    logger.info(f"Finding optimal k in range {k_range.start}-{k_range.stop-1}...")
    
    best_score = -1
    best_k = k_range.start
    
    for k in k_range:
        if k >= len(X):
            continue
        
        kmeans = KMeans(n_clusters=k, random_state=Config.RANDOM_SEED, n_init=10)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        
        logger.info(f"  k={k}: silhouette score = {score:.4f}")
        
        if score > best_score:
            best_score = score
            best_k = k
    
    logger.info(f"✓ Optimal k = {best_k} (score: {best_score:.4f})")
    return best_k


def cluster_products_kmeans(
    cooccurrence: np.ndarray,
    product_ids: list,
    k: int = None
) -> Dict[int, int]:
    """Cluster products using KMeans.
    
    Args:
        cooccurrence: Co-occurrence matrix
        product_ids: List of product IDs
        k: Number of clusters (if None, auto-select)
    
    Returns:
        Dictionary mapping product_id to cluster_id
    """
    logger.info("Clustering products with KMeans...")
    
    # Find optimal k if not provided
    if k is None:
        k = find_optimal_k(cooccurrence, range(3, 11))
    
    # Cluster
    kmeans = KMeans(n_clusters=k, random_state=Config.RANDOM_SEED, n_init=10)
    labels = kmeans.fit_predict(cooccurrence)
    
    # Create mapping
    clustering = {product_ids[i]: int(labels[i]) for i in range(len(product_ids))}
    
    logger.info(f"✓ Clustered {len(product_ids)} products into {k} clusters")
    
    return clustering


def save_clusters_to_db(clustering: Dict[int, int]) -> int:
    """Save product clusters to database.
    
    Args:
        clustering: Dictionary mapping product_id to cluster_id
    
    Returns:
        int: Number of assignments saved
    """
    logger.info("Saving product clusters to database...")
    
    with session_scope() as session:
        # Delete existing clusters
        deleted = session.query(ProductCluster).delete()
        logger.info(f"Deleted {deleted} existing product clusters")
        
        # Insert new clusters
        clusters = [
            ProductCluster(
                product_id=product_id,
                cluster_id=cluster_id
            )
            for product_id, cluster_id in clustering.items()
        ]
        
        session.bulk_save_objects(clusters)
        session.commit()
    
    logger.info(f"✓ Saved {len(clusters)} product cluster assignments")
    return len(clusters)


def get_cluster_statistics(clustering: Dict[int, int]) -> Dict:
    """Compute cluster statistics.
    
    Args:
        clustering: Dictionary mapping product_id to cluster_id
    
    Returns:
        Dictionary with statistics
    """
    # Count products per cluster
    cluster_sizes = defaultdict(int)
    for product_id, cluster_id in clustering.items():
        cluster_sizes[cluster_id] += 1
    
    stats = {
        'num_clusters': len(cluster_sizes),
        'cluster_sizes': dict(cluster_sizes),
        'avg_size': sum(cluster_sizes.values()) / len(cluster_sizes) if cluster_sizes else 0,
        'largest_cluster': max(cluster_sizes.values()) if cluster_sizes else 0,
        'smallest_cluster': min(cluster_sizes.values()) if cluster_sizes else 0
    }
    
    return stats


def cluster_products(k: int = None) -> Dict[int, int]:
    """Main function to cluster products.
    
    Args:
        k: Number of clusters (if None, auto-select)
    
    Returns:
        Dictionary mapping product_id to cluster_id
    """
    logger.info("Starting product clustering...")
    
    # Build co-occurrence matrix
    cooccurrence, product_ids = build_product_cooccurrence_matrix()
    
    # Cluster products
    clustering = cluster_products_kmeans(cooccurrence, product_ids, k=k)
    
    # Save to database
    save_clusters_to_db(clustering)
    
    # Log statistics
    stats = get_cluster_statistics(clustering)
    logger.info("Cluster statistics:")
    logger.info(f"  Number of clusters: {stats['num_clusters']}")
    logger.info(f"  Average cluster size: {stats['avg_size']:.1f}")
    logger.info(f"  Largest cluster: {stats['largest_cluster']} products")
    logger.info(f"  Smallest cluster: {stats['smallest_cluster']} products")
    
    logger.info(f"  Cluster sizes: {stats['cluster_sizes']}")
    
    logger.info("✓ Product clustering complete!")
    
    return clustering


if __name__ == '__main__':
    cluster_products()