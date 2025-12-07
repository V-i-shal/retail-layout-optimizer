"""Detect communities in the section graph using modularity optimization."""
import networkx as nx
import logging
from typing import Dict, List
from collections import defaultdict

from app.db import session_scope
from app.models import GraphEdge, SectionCommunity
from app.pipeline.build_graph import build_movement_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_graph_from_db() -> nx.Graph:
    """Load graph from database as undirected graph for community detection.
    
    Returns:
        NetworkX undirected Graph
    """
    logger.info("Loading graph from database...")
    
    G = nx.Graph()  # Undirected for community detection
    
    with session_scope() as session:
        edges = session.query(GraphEdge).all()
        
        for edge in edges:
            # Add edge (combine weights if both directions exist)
            if G.has_edge(edge.src_section_id, edge.dst_section_id):
                G[edge.src_section_id][edge.dst_section_id]['weight'] += edge.weight
            else:
                G.add_edge(
                    edge.src_section_id,
                    edge.dst_section_id,
                    weight=edge.weight
                )
    
    logger.info(f"✓ Loaded graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def detect_communities_louvain(G: nx.Graph) -> Dict[str, int]:
    """Detect communities using Louvain algorithm.
    
    Args:
        G: NetworkX undirected graph
    
    Returns:
        Dictionary mapping section_id to community_id
    """
    try:
        import community as community_louvain
        logger.info("Using Louvain algorithm for community detection...")
        
        # Louvain algorithm
        partition = community_louvain.best_partition(G, weight='weight')
        
        logger.info(f"✓ Louvain found {len(set(partition.values()))} communities")
        return partition
        
    except ImportError:
        logger.warning("python-louvain not available, falling back to greedy modularity")
        return detect_communities_greedy(G)


def detect_communities_greedy(G: nx.Graph) -> Dict[str, int]:
    """Detect communities using NetworkX greedy modularity algorithm.
    
    Args:
        G: NetworkX undirected graph
    
    Returns:
        Dictionary mapping section_id to community_id
    """
    logger.info("Using greedy modularity algorithm for community detection...")
    
    # Greedy modularity communities
    communities = nx.community.greedy_modularity_communities(G, weight='weight')
    
    # Convert to partition dictionary
    partition = {}
    for community_id, community_nodes in enumerate(communities):
        for node in community_nodes:
            partition[node] = community_id
    
    logger.info(f"✓ Greedy modularity found {len(communities)} communities")
    return partition


def save_communities_to_db(partition: Dict[str, int]) -> int:
    """Save community assignments to database.
    
    Args:
        partition: Dictionary mapping section_id to community_id
    
    Returns:
        int: Number of assignments saved
    """
    logger.info("Saving community assignments to database...")
    
    with session_scope() as session:
        # Delete existing assignments
        deleted = session.query(SectionCommunity).delete()
        logger.info(f"Deleted {deleted} existing community assignments")
        
        # Insert new assignments
        assignments = [
            SectionCommunity(
                section_id=section_id,
                community_id=community_id
            )
            for section_id, community_id in partition.items()
        ]
        
        session.bulk_save_objects(assignments)
        session.commit()
    
    logger.info(f"✓ Saved {len(assignments)} community assignments")
    return len(assignments)


def get_community_statistics(partition: Dict[str, int]) -> Dict:
    """Compute community statistics.
    
    Args:
        partition: Dictionary mapping section_id to community_id
    
    Returns:
        Dictionary with statistics
    """
    # Count sections per community
    community_sizes = defaultdict(int)
    for section_id, community_id in partition.items():
        community_sizes[community_id] += 1
    
    stats = {
        'num_communities': len(community_sizes),
        'community_sizes': dict(community_sizes),
        'avg_size': sum(community_sizes.values()) / len(community_sizes) if community_sizes else 0,
        'largest_community': max(community_sizes.values()) if community_sizes else 0,
        'smallest_community': min(community_sizes.values()) if community_sizes else 0
    }
    
    return stats


def detect_section_communities(use_louvain: bool = True) -> Dict[str, int]:
    """Main function to detect section communities.
    
    Args:
        use_louvain: If True, try Louvain algorithm first
    
    Returns:
        Dictionary mapping section_id to community_id
    """
    logger.info("Starting community detection...")
    
    # Load graph
    G = load_graph_from_db()
    
    # Detect communities
    if use_louvain:
        partition = detect_communities_louvain(G)
    else:
        partition = detect_communities_greedy(G)
    
    # Save to database
    save_communities_to_db(partition)
    
    # Log statistics
    stats = get_community_statistics(partition)
    logger.info("Community statistics:")
    logger.info(f"  Number of communities: {stats['num_communities']}")
    logger.info(f"  Average community size: {stats['avg_size']:.1f}")
    logger.info(f"  Largest community: {stats['largest_community']} sections")
    logger.info(f"  Smallest community: {stats['smallest_community']} sections")
    
    # Show community breakdown
    logger.info("Community breakdown:")
    for comm_id, size in sorted(stats['community_sizes'].items()):
        members = [s for s, c in partition.items() if c == comm_id]
        logger.info(f"  Community {comm_id}: {size} sections - {', '.join(sorted(members)[:10])}")
    
    logger.info("✓ Community detection complete!")
    
    return partition


if __name__ == '__main__':
    detect_section_communities()