-- Retail Layout Optimizer Database Schema
-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS recommendation;
DROP TABLE IF EXISTS product_cluster;
DROP TABLE IF EXISTS section_community;
DROP TABLE IF EXISTS graph_edge;
DROP TABLE IF EXISTS movement;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS store_section;
DROP TABLE IF EXISTS run_metadata;

-- Store sections with grid coordinates
CREATE TABLE store_section (
    section_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    x INT NOT NULL,
    y INT NOT NULL,
    INDEX idx_coords (x, y)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Products catalog
CREATE TABLE product (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    current_section_id VARCHAR(10),
    FOREIGN KEY (current_section_id) REFERENCES store_section(section_id) ON DELETE SET NULL,
    INDEX idx_category (category),
    INDEX idx_section (current_section_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Customer movement paths
CREATE TABLE movement (
    path_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(50) NOT NULL,
    step_order INT NOT NULL,
    section_id VARCHAR(10) NOT NULL,
    ts DATETIME NOT NULL,
    FOREIGN KEY (section_id) REFERENCES store_section(section_id) ON DELETE CASCADE,
    INDEX idx_session (session_id, step_order),
    INDEX idx_section_time (section_id, ts)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Graph edges (weighted transitions between sections)
CREATE TABLE graph_edge (
    src_section_id VARCHAR(10) NOT NULL,
    dst_section_id VARCHAR(10) NOT NULL,
    weight DOUBLE NOT NULL DEFAULT 0,
    PRIMARY KEY (src_section_id, dst_section_id),
    FOREIGN KEY (src_section_id) REFERENCES store_section(section_id) ON DELETE CASCADE,
    FOREIGN KEY (dst_section_id) REFERENCES store_section(section_id) ON DELETE CASCADE,
    INDEX idx_weight (weight DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Section communities (clustering result)
CREATE TABLE section_community (
    section_id VARCHAR(10) PRIMARY KEY,
    community_id INT NOT NULL,
    FOREIGN KEY (section_id) REFERENCES store_section(section_id) ON DELETE CASCADE,
    INDEX idx_community (community_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Product clusters (ML clustering result)
CREATE TABLE product_cluster (
    product_id INT PRIMARY KEY,
    cluster_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE,
    INDEX idx_cluster (cluster_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Layout recommendations
CREATE TABLE recommendation (
    product_id INT PRIMARY KEY,
    recommended_section_id VARCHAR(10) NOT NULL,
    rationale TEXT,
    score DOUBLE NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE,
    FOREIGN KEY (recommended_section_id) REFERENCES store_section(section_id) ON DELETE CASCADE,
    INDEX idx_score (score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Pipeline run tracking
CREATE TABLE run_metadata (
    run_id INT PRIMARY KEY AUTO_INCREMENT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;