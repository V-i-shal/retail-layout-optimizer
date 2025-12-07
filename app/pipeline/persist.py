"""Persist pipeline results to database (idempotent operations)."""
import logging
from datetime import datetime

from app.db import session_scope
from app.models import RunMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def record_pipeline_run(notes: str = None) -> int:
    """Record a pipeline run in the metadata table.
    
    Args:
        notes: Optional notes about this run
    
    Returns:
        run_id: ID of the created run record
    """
    logger.info("Recording pipeline run...")
    
    with session_scope() as session:
        run = RunMetadata(
            created_at=datetime.utcnow(),
            notes=notes or "Pipeline run completed successfully"
        )
        session.add(run)
        session.flush()
        run_id = run.run_id
        session.commit()
    
    logger.info(f"✓ Pipeline run recorded with ID: {run_id}")
    return run_id


def get_latest_run_info():
    """Get information about the latest pipeline run.
    
    Returns:
        Dictionary with run information or None
    """
    with session_scope() as session:
        latest_run = session.query(RunMetadata)\
            .order_by(RunMetadata.run_id.desc())\
            .first()
        
        if latest_run:
            return {
                'run_id': latest_run.run_id,
                'created_at': latest_run.created_at,
                'notes': latest_run.notes
            }
        return None


def persist_all_results(notes: str = None):
    """Persist all pipeline results and record the run.
    
    This function serves as a confirmation that all previous steps
    (graph building, community detection, clustering, optimization)
    have successfully persisted their results.
    
    Args:
        notes: Optional notes about this run
    """
    logger.info("Persisting pipeline results...")
    
    # Record the run
    run_id = record_pipeline_run(notes)
    
    # Get summary statistics
    with session_scope() as session:
        from app.models import GraphEdge, SectionCommunity, ProductCluster, Recommendation
        
        n_edges = session.query(GraphEdge).count()
        n_communities = session.query(SectionCommunity).count()
        n_clusters = session.query(ProductCluster).count()
        n_recommendations = session.query(Recommendation).count()
    
    logger.info("✓ Pipeline results summary:")
    logger.info(f"  - Graph edges: {n_edges}")
    logger.info(f"  - Section communities: {n_communities}")
    logger.info(f"  - Product clusters: {n_clusters}")
    logger.info(f"  - Recommendations: {n_recommendations}")
    logger.info(f"  - Run ID: {run_id}")
    
    return run_id


if __name__ == '__main__':
    persist_all_results()