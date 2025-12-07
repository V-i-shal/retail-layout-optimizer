"""Pipeline orchestrator - runs all steps in sequence."""
import argparse
import logging
import time
from datetime import datetime

from app.pipeline.ingest import ingest_all
from app.pipeline.build_graph import build_movement_graph
from app.pipeline.detect_communities import detect_section_communities
from app.pipeline.product_clustering import cluster_products
from app.pipeline.optimize_layout import optimize_layout
from app.pipeline.persist import persist_all_results

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_pipeline(rebuild: bool = False, skip_ingest: bool = False):
    """Run the complete pipeline.
    
    Args:
        rebuild: If True, clear existing data before ingesting
        skip_ingest: If True, skip data ingestion step
    """
    logger.info("="*60)
    logger.info("RETAIL LAYOUT OPTIMIZER PIPELINE")
    logger.info("="*60)
    
    start_time = time.time()
    steps_completed = []
    
    try:
        # Step 1: Ingest data
        if not skip_ingest:
            logger.info("\n[1/6] INGESTING DATA...")
            step_start = time.time()
            ingest_all(clear_existing=rebuild)
            step_time = time.time() - step_start
            steps_completed.append(('Ingest Data', step_time))
        else:
            logger.info("\n[1/6] SKIPPING DATA INGESTION")
            steps_completed.append(('Ingest Data', 0))
        
        # Step 2: Build graph
        logger.info("\n[2/6] BUILDING MOVEMENT GRAPH...")
        step_start = time.time()
        build_movement_graph()
        step_time = time.time() - step_start
        steps_completed.append(('Build Graph', step_time))
        
        # Step 3: Detect communities
        logger.info("\n[3/6] DETECTING SECTION COMMUNITIES...")
        step_start = time.time()
        detect_section_communities()
        step_time = time.time() - step_start
        steps_completed.append(('Detect Communities', step_time))
        
        # Step 4: Cluster products
        logger.info("\n[4/6] CLUSTERING PRODUCTS...")
        step_start = time.time()
        cluster_products()
        step_time = time.time() - step_start
        steps_completed.append(('Cluster Products', step_time))
        
        # Step 5: Optimize layout
        logger.info("\n[5/6] OPTIMIZING LAYOUT...")
        step_start = time.time()
        optimize_layout()
        step_time = time.time() - step_start
        steps_completed.append(('Optimize Layout', step_time))
        
        # Step 6: Persist results
        logger.info("\n[6/6] PERSISTING RESULTS...")
        step_start = time.time()
        persist_all_results(notes=f"Full pipeline run at {datetime.now()}")
        step_time = time.time() - step_start
        steps_completed.append(('Persist Results', step_time))
        
        total_time = time.time() - start_time
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info("\nTiming Summary:")
        for step_name, step_time in steps_completed:
            logger.info(f"  {step_name:.<40} {step_time:.2f}s")
        logger.info(f"  {'TOTAL':.>40} {total_time:.2f}s")
        logger.info("\n✓ All results saved to database")
        logger.info("✓ Ready to start dashboard: python -m app.dashboard.server")
        
    except Exception as e:
        logger.error(f"\n✗ Pipeline failed at step: {steps_completed[-1][0] if steps_completed else 'Unknown'}")
        logger.error(f"✗ Error: {str(e)}")
        raise


def main():
    """Command-line interface for pipeline."""
    parser = argparse.ArgumentParser(
        description='Run the retail layout optimizer pipeline'
    )
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='Clear existing data before running (fresh start)'
    )
    parser.add_argument(
        '--skip-ingest',
        action='store_true',
        help='Skip data ingestion (use existing data)'
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    run_pipeline(rebuild=args.rebuild, skip_ingest=args.skip_ingest)


if __name__ == '__main__':
    main()