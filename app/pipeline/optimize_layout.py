"""Optimize product-to-section layout using linear assignment."""
import numpy as np
from scipy.optimize import linear_sum_assignment
import logging
from typing import Dict, Tuple, List

from app.db import session_scope
from app.models import StoreSection, Product, GraphEdge, ProductCluster, Recommendation
from app.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

np.random.seed(Config.RANDOM_SEED)


def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x1 - x2) + abs(y1 - y2)


# -----------------------------------------------------------
# FIXED FUNCTION — ALL SQLAlchemy Objects → Pure Dicts
# -----------------------------------------------------------
def load_sections_and_products() -> Tuple[List, List, Dict, Dict]:
    logger.info("Loading sections and products...")

    with session_scope() as session:
        db_sections = session.query(StoreSection).all()
        db_products = session.query(Product).all()
        db_clusters = session.query(ProductCluster).all()

        # Convert sections → dicts
        sections = [
            {
                "section_id": s.section_id,
                "name": s.name,
                "x": s.x,
                "y": s.y
            }
            for s in db_sections
        ]

        # Convert products → dicts
        products = [
            {
                "product_id": p.product_id,
                "name": p.name,
                "category": p.category,
                "current_section_id": p.current_section_id
            }
            for p in db_products
        ]

        # Section coords dict
        section_coords = {s["section_id"]: (s["x"], s["y"]) for s in sections}

        # Product info dict
        product_info = {
            p["product_id"]: {
                "name": p["name"],
                "category": p["category"],
                "current_section": p["current_section_id"],
                "cluster_id": None
            }
            for p in products
        }

        # Add cluster info
        for c in db_clusters:
            if c.product_id in product_info:
                product_info[c.product_id]["cluster_id"] = c.cluster_id

        logger.info(f"✓ Loaded {len(sections)} sections and {len(products)} products")
        return sections, products, section_coords, product_info


def build_flow_matrix(products: List, product_info: Dict) -> np.ndarray:
    logger.info("Building product flow matrix...")

    n_products = len(products)
    flow = np.zeros((n_products, n_products))

    for i, p1 in enumerate(products):
        cluster1 = product_info[p1["product_id"]]["cluster_id"]
        if cluster1 is None:
            continue

        for j, p2 in enumerate(products):
            if i >= j:
                continue

            cluster2 = product_info[p2["product_id"]]["cluster_id"]
            if cluster2 is None:
                continue

            if cluster1 == cluster2:
                flow[i, j] = flow[j, i] = 10.0
            else:
                flow[i, j] = flow[j, i] = 0.1

    logger.info(f"✓ Flow matrix built: {n_products}x{n_products}")
    return flow


def build_distance_matrix(sections: List, section_coords: Dict) -> np.ndarray:
    logger.info("Building distance matrix...")

    n_sections = len(sections)
    distances = np.zeros((n_sections, n_sections))

    for i, s1 in enumerate(sections):
        x1, y1 = section_coords[s1["section_id"]]
        for j, s2 in enumerate(sections):
            x2, y2 = section_coords[s2["section_id"]]
            distances[i, j] = manhattan_distance(x1, y1, x2, y2)

    logger.info(f"✓ Distance matrix built: {n_sections}x{n_sections}")
    return distances


def build_cost_matrix(flow: np.ndarray, distances: np.ndarray, products: List, sections: List) -> np.ndarray:
    logger.info("Building cost matrix for assignment...")

    n_products = len(products)
    n_sections = len(sections)
    cost = np.zeros((n_products, n_sections))

    section_idx = {s["section_id"]: idx for idx, s in enumerate(sections)}

    for i in range(n_products):
        for j in range(n_sections):
            total_cost = 0.0

            for k in range(n_products):
                if i == k:
                    continue

                current_section = products[k]["current_section_id"]
                if current_section and current_section in section_idx:
                    k_idx = section_idx[current_section]
                    total_cost += flow[i, k] * distances[j, k_idx]

            cost[i, j] = total_cost

    logger.info(f"✓ Cost matrix built: {n_products}x{n_sections}")
    return cost


def solve_assignment(cost: np.ndarray):
    logger.info("Solving assignment problem...")
    row_ind, col_ind = linear_sum_assignment(cost)
    logger.info(f"✓ Assignment solved with total cost: {cost[row_ind, col_ind].sum():.2f}")
    return row_ind, col_ind


def generate_recommendations(products, sections, row_ind, col_ind, product_info, cost):

    logger.info("Generating recommendations...")
    recommendations = []

    for i, j in zip(row_ind, col_ind):
        product = products[i]
        section = sections[j]

        info = product_info[product["product_id"]]
        cluster_id = info["cluster_id"]

        rationale_parts = []
        rationale_parts.append(
            f"Product '{product['name']}' (Category: {product['category']})"
        )

        if cluster_id is not None:
            same_cluster = [
                p for p in products
                if product_info[p["product_id"]]["cluster_id"] == cluster_id
                and p["product_id"] != product["product_id"]
            ]

            if same_cluster:
                names = [p["name"] for p in same_cluster[:3]]
                rationale_parts.append(
                    f"clustered with {', '.join(names)}"
                    + (f" and {len(same_cluster)-3} others" if len(same_cluster) > 3 else "")
                )

        rationale_parts.append(
            f"should be placed in section '{section['name']}' ({section['section_id']})"
        )
        rationale_parts.append("to minimize customer walking distance")

        recommendations.append({
            "product_id": product["product_id"],
            "recommended_section_id": section["section_id"],
            "rationale": "; ".join(rationale_parts) + ".",
            "score": float(-cost[i, j])
        })

    logger.info(f"✓ Generated {len(recommendations)} recommendations")
    return recommendations


def save_recommendations_to_db(recommendations):
    logger.info("Saving recommendations to database...")

    with session_scope() as session:
        session.query(Recommendation).delete()

        objs = [
            Recommendation(
                product_id=r["product_id"],
                recommended_section_id=r["recommended_section_id"],
                rationale=r["rationale"],
                score=r["score"]
            )
            for r in recommendations
        ]

        session.bulk_save_objects(objs)
        session.commit()

    logger.info(f"✓ Saved {len(objs)} recommendations")
    return len(objs)


def optimize_layout():
    logger.info("Starting layout optimization...")

    sections, products, section_coords, product_info = load_sections_and_products()

    flow = build_flow_matrix(products, product_info)
    distances = build_distance_matrix(sections, section_coords)
    cost = build_cost_matrix(flow, distances, products, sections)

    row_ind, col_ind = solve_assignment(cost)

    recs = generate_recommendations(products, sections, row_ind, col_ind, product_info, cost)

    save_recommendations_to_db(recs)

    logger.info("✓ Layout optimization complete!")
    return recs


if __name__ == "__main__":
    optimize_layout()
