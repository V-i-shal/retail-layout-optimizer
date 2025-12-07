"""API routes for accessing pipeline results."""
from flask import Blueprint, jsonify, request
import logging

from app.db import session_scope
from app.models import (
    StoreSection, GraphEdge, Recommendation, 
    Product, SectionCommunity, ProductCluster
)

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@api_bp.route('/sections', methods=['GET'])
def get_sections():
    """Get all store sections with coordinates and community assignments.
    
    Returns:
        JSON array of sections
    """
    try:
        with session_scope() as session:
            sections = session.query(StoreSection).all()
            
            result = [section.to_dict() for section in sections]
            
            return jsonify({
                'success': True,
                'count': len(result),
                'data': result
            })
    except Exception as e:
        logger.error(f"Error fetching sections: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/graph', methods=['GET'])
def get_graph():
    """Get graph edges with weights.
    
    Returns:
        JSON object with nodes and edges
    """
    try:
        with session_scope() as session:
            # Get sections (nodes)
            sections = session.query(StoreSection).all()
            nodes = [section.to_dict() for section in sections]
            
            # Get edges
            edges = session.query(GraphEdge).all()
            edges_data = [edge.to_dict() for edge in edges]
            
            return jsonify({
                'success': True,
                'data': {
                    'nodes': nodes,
                    'edges': edges_data
                }
            })
    except Exception as e:
        logger.error(f"Error fetching graph: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get layout recommendations.
    
    Query params:
        limit: Maximum number of results (default: all)
        sort: Sort by 'score' or 'product_id' (default: score)
    
    Returns:
        JSON array of recommendations
    """
    try:
        limit = request.args.get('limit', type=int)
        sort_by = request.args.get('sort', 'score')
        
        with session_scope() as session:
            query = session.query(Recommendation)
            
            # Sort
            if sort_by == 'score':
                query = query.order_by(Recommendation.score.desc())
            else:
                query = query.order_by(Recommendation.product_id)
            
            # Limit
            if limit:
                query = query.limit(limit)
            
            recommendations = query.all()
            result = [rec.to_dict() for rec in recommendations]
            
            return jsonify({
                'success': True,
                'count': len(result),
                'data': result
            })
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with cluster assignments.
    
    Returns:
        JSON array of products
    """
    try:
        with session_scope() as session:
            products = session.query(Product).all()
            result = [product.to_dict() for product in products]
            
            return jsonify({
                'success': True,
                'count': len(result),
                'data': result
            })
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/communities', methods=['GET'])
def get_communities():
    """Get section community assignments.
    
    Returns:
        JSON object with community statistics
    """
    try:
        with session_scope() as session:
            communities = session.query(SectionCommunity).all()
            result = [comm.to_dict() for comm in communities]
            
            # Group by community
            by_community = {}
            for comm in result:
                cid = comm['community_id']
                if cid not in by_community:
                    by_community[cid] = []
                by_community[cid].append(comm['section_id'])
            
            return jsonify({
                'success': True,
                'count': len(result),
                'data': result,
                'by_community': by_community
            })
    except Exception as e:
        logger.error(f"Error fetching communities: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall statistics.
    
    Returns:
        JSON object with counts
    """
    try:
        with session_scope() as session:
            stats = {
                'sections': session.query(StoreSection).count(),
                'products': session.query(Product).count(),
                'graph_edges': session.query(GraphEdge).count(),
                'communities': len(set(
                    c.community_id for c in session.query(SectionCommunity).all()
                )),
                'product_clusters': len(set(
                    c.cluster_id for c in session.query(ProductCluster).all()
                )),
                'recommendations': session.query(Recommendation).count()
            }
            
            return jsonify({
                'success': True,
                'data': stats
            })
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint.
    
    Returns:
        JSON status
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'Retail Layout Optimizer API'
    })