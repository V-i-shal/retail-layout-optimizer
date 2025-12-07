"""Build weighted movement graph from customer paths."""
import networkx as nx
import pandas as pd
from collections import defaultdict
import logging
from typing import Tuple, Dict

from app.db import session_scope
from app.models import Movement, GraphEdge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_transitions_from_db() -> pd.DataFrame:
    """Compute section-to-section transitions from movement data.
    
    Returns:
        DataFrame with columns: src_section_id, dst_section_id, count
    """
    logger.info("Computing transitions from movement data...")
    
    with session_scope() as session:
        # Get all movements ordered by session and step
        movements = session.query(Movement).order_by(
            Movement.session_id,
            Movement.step_order
        ).all()
        
        logger.info(f"Processing {len(movements)} movement records...")
        
        # Count transitions
        transitions = defaultdict(int)
        current_session = None
        prev_section = None
        
        for movement in movements:
            if movement.session_id != current_session:
                # New session started
                current_session = movement.session_id
                prev_section = movement.section_id
            else:
                # Transition from prev_section to current section
                if prev_section != movement.section_id:  # Ignore self-loops
                    edge = (prev_section, movement.section_id)
                    transitions[edge] += 1
                prev_section = movement.section_id
        
        logger.info(f"Found {len(transitions)} unique transitions")
        
        # Convert to DataFrame
        transition_data = [
            {
                'src_section_id': src,
                'dst_section_id': dst,
                'count': count
            }
            for (src, dst), count in transitions.items()
        ]
        
        df = pd.DataFrame(transition_data)
        return df


def build_networkx_graph(transitions_df: pd.DataFrame) -> nx.DiGraph:
    """Build NetworkX directed graph from transitions.
    
    Args:
        transitions_df: DataFrame with src_section_id, dst_section_id, count
    
    Returns:
        NetworkX DiGraph with edge weights
    """
    logger.info("Building NetworkX graph...")
    
    G = nx.DiGraph()
    
    # Add edges with weights
    for _, row in transitions_df.iterrows():
        G.add_edge(
            row['src_section_id'],
            row['dst_section_id'],
            weight=row['count']
        )
    
    logger.info(f"✓ Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    return G


def save_graph_to_db(transitions_df: pd.DataFrame) -> int:
    """Save graph edges to database.
    
    Args:
        transitions_df: DataFrame with src_section_id, dst_section_id, count
    
    Returns:
        int: Number of edges saved
    """
    logger.info("Saving graph edges to database...")
    
    with session_scope() as session:
        # Delete existing edges
        deleted = session.query(GraphEdge).delete()
        logger.info(f"Deleted {deleted} existing edges")
        
        # Insert new edges
        edges = [
            GraphEdge(
                src_section_id=row['src_section_id'],
                dst_section_id=row['dst_section_id'],
                weight=float(row['count'])
            )
            for _, row in transitions_df.iterrows()
        ]
        
        session.bulk_save_objects(edges)
        session.commit()
    
    logger.info(f"✓ Saved {len(edges)} edges to database")
    return len(edges)


def get_graph_statistics(G: nx.DiGraph) -> Dict:
    """Compute basic graph statistics.
    
    Args:
        G: NetworkX graph
    
    Returns:
        Dictionary with statistics
    """
    stats = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0,
        'density': nx.density(G),
    }
    
    # Top 5 most connected nodes
    degree_dict = dict(G.degree())
    top_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    stats['top_nodes'] = top_nodes
    
    return stats


def build_movement_graph() -> Tuple[nx.DiGraph, pd.DataFrame]:
    """Main function to build movement graph.
    
    Returns:
        Tuple of (NetworkX graph, transitions DataFrame)
    """
    logger.info("Starting graph building process...")
    
    # Compute transitions
    transitions_df = compute_transitions_from_db()
    
    # Build NetworkX graph
    G = build_networkx_graph(transitions_df)
    
    # Save to database
    save_graph_to_db(transitions_df)
    
    # Log statistics
    stats = get_graph_statistics(G)
    logger.info("Graph statistics:")
    logger.info(f"  Nodes: {stats['nodes']}")
    logger.info(f"  Edges: {stats['edges']}")
    logger.info(f"  Average degree: {stats['avg_degree']:.2f}")
    logger.info(f"  Density: {stats['density']:.4f}")
    logger.info(f"  Top connected sections: {stats['top_nodes'][:3]}")
    
    logger.info("✓ Graph building complete!")
    
    return G, transitions_df


if __name__ == '__main__':
    build_movement_graph()      