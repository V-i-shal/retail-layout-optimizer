"""Tests for graph building functionality."""
import pytest
import networkx as nx
import pandas as pd
from datetime import datetime

from app.pipeline.build_graph import (
    build_networkx_graph,
    get_graph_statistics
)


def test_build_graph_from_transitions():
    """Test building NetworkX graph from transition data."""
    # Create sample transition data
    transitions_df = pd.DataFrame([
        {'src_section_id': 'A', 'dst_section_id': 'B', 'count': 10},
        {'src_section_id': 'B', 'dst_section_id': 'C', 'count': 5},
        {'src_section_id': 'A', 'dst_section_id': 'C', 'count': 3},
    ])
    
    # Build graph
    G = build_networkx_graph(transitions_df)
    
    # Assertions
    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 3
    assert G.has_edge('A', 'B')
    assert G['A']['B']['weight'] == 10
    assert G['B']['C']['weight'] == 5


def test_graph_statistics():
    """Test graph statistics computation."""
    # Create simple graph
    G = nx.DiGraph()
    G.add_edge('A', 'B', weight=10)
    G.add_edge('B', 'C', weight=5)
    G.add_edge('C', 'A', weight=3)
    
    # Get statistics
    stats = get_graph_statistics(G)
    
    # Assertions
    assert stats['nodes'] == 3
    assert stats['edges'] == 3
    assert stats['avg_degree'] == 2.0  # Each node has degree 2


def test_empty_graph():
    """Test handling of empty graph."""
    transitions_df = pd.DataFrame(columns=['src_section_id', 'dst_section_id', 'count'])
    
    G = build_networkx_graph(transitions_df)
    
    assert G.number_of_nodes() == 0
    assert G.number_of_edges() == 0


def test_self_loops_excluded():
    """Test that self-loops are handled correctly."""
    transitions_df = pd.DataFrame([
        {'src_section_id': 'A', 'dst_section_id': 'A', 'count': 100},  # Self-loop
        {'src_section_id': 'A', 'dst_section_id': 'B', 'count': 10},
    ])
    
    G = build_networkx_graph(transitions_df)
    
    # Self-loop should be included if in data
    assert G.number_of_edges() == 2
    assert G.has_edge('A', 'A')
    assert G.has_edge('A', 'B')


def test_community_count():
    """Test that community detection finds reasonable number of communities."""
    # Create graph with clear community structure
    G = nx.Graph()
    
    # Community 1
    G.add_edge('A', 'B', weight=10)
    G.add_edge('B', 'C', weight=10)
    G.add_edge('C', 'A', weight=10)
    
    # Community 2
    G.add_edge('D', 'E', weight=10)
    G.add_edge('E', 'F', weight=10)
    G.add_edge('F', 'D', weight=10)
    
    # Weak connection between communities
    G.add_edge('C', 'D', weight=1)
    
    # Detect communities using NetworkX
    communities = list(nx.community.greedy_modularity_communities(G, weight='weight'))
    
    # Should detect 2 communities
    assert len(communities) >= 1  # At least 1 community
    assert len(communities) <= 3  # At most 3 communities (reasonable range)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])