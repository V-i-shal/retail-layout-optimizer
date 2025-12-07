# Retail Store Layout Optimizer

A comprehensive data science and optimization system that analyzes customer movement patterns in retail stores to recommend optimal product placements. Built with Python, MySQL, Flask, NetworkX, and machine learning.

## 🎯 Project Overview

This system:
- **Analyzes** customer movement sequences through store sections
- **Builds** weighted movement graphs to understand traffic patterns
- **Detects** section communities using graph algorithms (Louvain/modularity)
- **Clusters** products based on co-purchase behavior
- **Optimizes** product placement to minimize customer walking distance
- **Visualizes** results through an interactive web dashboard

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Pipeline Workflow](#pipeline-workflow)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Assumptions](#assumptions)

## ✨ Features

### Data Processing
- Synthetic data generation for 10,000+ customer sessions
- 100 products across 20 categories
- 26 store sections in a 13x2 grid layout
- Realistic movement patterns with community structure

### Graph Analysis
- Weighted directed graph of section transitions
- 650+ edges representing customer movements
- Community detection using Louvain algorithm
- Network visualization with Plotly

### Machine Learning
- Product clustering using KMeans
- Co-occurrence matrix from simulated transactions
- Silhouette score optimization for cluster count
- Typically finds 3-7 optimal clusters

### Optimization
- Linear assignment problem for product placement
- Manhattan distance metric for layout costs
- Minimizes total walking distance
- Considers product affinity and section communities

### Web Dashboard
- Interactive network graph visualization
- Product density heatmaps (current vs. recommended)
- Searchable recommendations table
- Real-time statistics

## 🛠 Technology Stack

- **Python 3.11+** - Core programming language
- **MySQL 8.0+** - Relational database
- **Flask 3.0** - Web framework
- **SQLAlchemy 2.0** - ORM
- **NetworkX 3.2** - Graph analysis
- **Scikit-learn 1.3** - Machine learning
- **SciPy 1.11** - Optimization algorithms
- **Plotly 5.18** - Interactive visualizations
- **Pandas 2.1** - Data manipulation
- **NumPy 1.26** - Numerical computing

## 📦 Prerequisites

### Required Software

1. **MySQL 8.0 or higher**
   - Download: https://dev.mysql.com/downloads/installer/
   - Install MySQL Server and set root password

2. **Python 3.11 or higher**
   - Download: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

3. **Visual Studio Code** (recommended)
   - Download: https://code.visualstudio.com/
   - Install Python extension

### Verify Installation

```powershell
# Check Python
python --version  # Should show Python 3.11+

# Check MySQL
mysql --version  # Should show MySQL 8.0+

# Check pip
pip --version
```

## 🚀 Installation

### 1. Create MySQL Database

```powershell
# Open MySQL CLI
mysql -u root -p

# Create database
CREATE DATABASE retail_optimizer;
EXIT;
```

### 2. Clone/Create Project

```powershell
# Create project folder
mkdir retail-layout-optimizer
cd retail-layout-optimizer
```

### 3. Set Up Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Install Dependencies

```powershell
# Install all packages
pip install -r requirements.txt

# Verify installation
pip list
```

### 5. Initialize Database Schema

```powershell
# Load schema
mysql -u root -p retail_optimizer < sql\schema.sql

# Load seed data (26 sections)
mysql -u root -p retail_optimizer < sql\seed.sql
```

## ⚙ Configuration

### 1. Create Environment File

Copy `.env.example` to `.env`:

```powershell
copy .env.example .env
```

### 2. Edit `.env` File

Update with your MySQL credentials:

```env
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_password_here
MYSQL_DB=retail_optimizer

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Pipeline Configuration
RANDOM_SEED=42
```

⚠️ **Replace `your_actual_password_here` with your MySQL root password!**

## 🎮 Usage

### Quick Start (First Time)

```powershell
# 1. Generate sample data
python -m app.pipeline.simulate_data

# 2. Run complete pipeline
python -m app.pipeline.run_all --rebuild

# 3. Start dashboard
python -m app.dashboard.server
```

Open browser: **http://localhost:5000**

### Individual Pipeline Steps

```powershell
# Generate synthetic data
python -m app.pipeline.simulate_data

# Ingest data to database
python -m app.pipeline.ingest

# Build movement graph
python -m app.pipeline.build_graph

# Detect communities
python -m app.pipeline.detect_communities

# Cluster products
python -m app.pipeline.product_clustering

# Optimize layout
python -m app.pipeline.optimize_layout

# Persist results
python -m app.pipeline.persist
```

### Run Complete Pipeline

```powershell
# Fresh run (clear existing data)
python -m app.pipeline.run_all --rebuild

# Use existing data (skip ingestion)
python -m app.pipeline.run_all --skip-ingest
```

### Start Dashboard

```powershell
# Development mode
python -m app.dashboard.server

# Or use VS Code debugger (F5)
# Select "Flask: Dashboard Server" configuration
```

## 📁 Project Structure

```
retail-layout-optimizer/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .env                         # Your config (git-ignored)
├── .gitignore                   # Git ignore rules
│
├── data/                        # Generated CSV files
│   ├── sample_paths.csv         # Customer movements
│   └── sample_products.csv      # Product catalog
│
├── sql/                         # Database schemas
│   ├── schema.sql               # Table definitions
│   └── seed.sql                 # Initial data
│
├── app/                         # Main application
│   ├── __init__.py
│   ├── config.py                # Configuration loader
│   ├── db.py                    # Database connection
│   ├── models.py                # SQLAlchemy ORM models
│   │
│   ├── pipeline/                # Data pipeline modules
│   │   ├── __init__.py
│   │   ├── simulate_data.py     # Generate synthetic data
│   │   ├── ingest.py            # Load data to MySQL
│   │   ├── build_graph.py       # Build movement graph
│   │   ├── detect_communities.py # Section clustering
│   │   ├── product_clustering.py # Product clustering
│   │   ├── optimize_layout.py   # Layout optimization
│   │   ├── persist.py           # Save results
│   │   └── run_all.py           # Pipeline orchestrator
│   │
│   ├── api/                     # REST API
│   │   ├── __init__.py
│   │   └── routes.py            # API endpoints
│   │
│   └── dashboard/               # Web interface
│       ├── __init__.py
│       ├── server.py            # Flask app
│       ├── templates/
│       │   ├── base.html        # Base template
│       │   └── index.html       # Dashboard page
│       └── static/
│           ├── styles.css       # Dashboard styles
│           └── app.js           # Dashboard JavaScript
│
├── tests/                       # Test suite
│   ├── test_graph.py           # Graph tests
│   ├── test_optimization.py    # Optimization tests
│   └── test_api.py             # API tests
│
└── .vscode/                     # VS Code config
    ├── settings.json            # Editor settings
    └── launch.json              # Debug configs
```

## 🔄 Pipeline Workflow

### Step-by-Step Process

1. **Data Simulation** (`simulate_data.py`)
   - Generates 10,000 customer sessions
   - Creates 100 products across 20 categories
   - Produces realistic movement patterns

2. **Data Ingestion** (`ingest.py`)
   - Loads CSV files to MySQL
   - Validates schema
   - ~91,000 movement records
   - 100 product records

3. **Graph Building** (`build_graph.py`)
   - Computes section-to-section transitions
   - Creates weighted directed graph
   - ~650 edges
   - Saves to database

4. **Community Detection** (`detect_communities.py`)
   - Runs Louvain algorithm on undirected graph
   - Finds 3-6 section communities
   - Groups related sections

5. **Product Clustering** (`product_clustering.py`)
   - Builds co-occurrence matrix
   - Runs KMeans with silhouette optimization
   - Finds 3-7 optimal clusters

6. **Layout Optimization** (`optimize_layout.py`)
   - Formulates assignment problem
   - Minimizes: Σ flow(i,j) × distance(section(i), section(j))
   - Uses Hungarian algorithm
   - Generates recommendations

7. **Persist Results** (`persist.py`)
   - Records pipeline run metadata
   - Saves all results to database

### Typical Execution Time

- **Total**: 7-10 seconds
- Data simulation: 1-2s
- Graph building: 2-3s
- Community detection: <1s
- Product clustering: 5-6s
- Layout optimization: <1s

## 📡 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### GET /api/health
Health check
```json
{
  "success": true,
  "status": "healthy"
}
```

#### GET /api/sections
Get all store sections
```json
{
  "success": true,
  "count": 26,
  "data": [
    {
      "section_id": "A",
      "name": "Entrance",
      "x": 0,
      "y": 0,
      "community_id": 3
    }
  ]
}
```

#### GET /api/graph
Get graph nodes and edges
```json
{
  "success": true,
  "data": {
    "nodes": [...],
    "edges": [
      {
        "source": "A",
        "target": "B",
        "weight": 1234.5
      }
    ]
  }
}
```

#### GET /api/recommendations
Get product recommendations

Query params:
- `limit` (int): Max results
- `sort` (string): 'score' or 'product_id'

```json
{
  "success": true,
  "count": 26,
  "data": [
    {
      "product_id": 1,
      "product_name": "Premium Milk",
      "recommended_section_id": "D",
      "section_name": "Dairy",
      "rationale": "...",
      "score": -123.45
    }
  ]
}
```

#### GET /api/products
Get all products with clusters

#### GET /api/communities
Get section communities

#### GET /api/stats
Get overall statistics

## 🧪 Testing

### Run All Tests

```powershell
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_graph.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Coverage

- **test_graph.py**: Graph building and statistics
- **test_optimization.py**: Distance calculations and assignment
- **test_api.py**: API endpoints and responses

### Using VS Code Debugger

1. Press `F5`
2. Select "Pytest: Run Tests"
3. Set breakpoints as needed

## 🔧 Troubleshooting

### Database Connection Errors

**Error**: `Can't connect to MySQL server`

**Solution**:
```powershell
# Check MySQL is running
# Windows: Open Services, find MySQL80, start it

# Verify connection
mysql -u root -p

# Check .env file has correct password
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```powershell
# Make sure you're in project root
cd retail-layout-optimizer

# Verify virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### PowerShell Execution Policy

**Error**: `cannot be loaded because running scripts is disabled`

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use

**Error**: `Address already in use: 5000`

**Solution**:
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID with actual number)
taskkill /PID <PID> /F

# Or use different port
python -m app.dashboard.server --port 5001
```

### Empty Dashboard

**Issue**: Dashboard loads but shows no data

**Solution**:
```powershell
# Make sure pipeline has been run
python -m app.pipeline.run_all --skip-ingest

# Check database has data
mysql -u root -p retail_optimizer -e "SELECT COUNT(*) FROM recommendation;"
```

## 📝 Assumptions

### Data Generation
- **Sections**: 26 sections (A-Z) in 13x2 grid layout
- **Sessions**: 10,000 customer paths
- **Products**: 100 products across 20 categories
- **Path Length**: 3-15 steps per session (avg ~7)
- **Communities**: Products naturally group into 3-6 communities

### Algorithms
- **Community Detection**: Louvain algorithm (falls back to greedy modularity if unavailable)
- **Clustering**: KMeans with k=3-10, optimized by silhouette score
- **Distance Metric**: Manhattan distance (appropriate for grid layout)
- **Optimization**: Linear sum assignment (Hungarian algorithm)

### Simplifications
- Simulated transactions from last 3-5 sections visited
- Products "purchased" from visited sections
- No time-of-day or seasonal effects
- All sections assumed equal capacity

### Database
- SQLAlchemy ORM with PyMySQL driver
- InnoDB storage engine
- UTF-8 character encoding
- Foreign key constraints enforced

## 📄 License

This project is for educational and portfolio purposes.

## 👤 Author

Built as a comprehensive Python data science project demonstrating:
- Graph theory and network analysis
- Machine learning clustering
- Mathematical optimization
- Database design and ORM
- RESTful API development
- Interactive data visualization
- Software engineering best practices

---

## 🎓 Learning Outcomes

This project demonstrates proficiency in:
- **Data Engineering**: ETL pipelines, database design
- **Graph Theory**: NetworkX, community detection
- **Machine Learning**: KMeans clustering, silhouette analysis
- **Optimization**: Linear assignment, cost minimization
- **Full-Stack Development**: Flask, REST APIs, interactive dashboards
- **Software Engineering**: Testing, documentation, version control
- **DevOps**: Virtual environments, configuration management

---

**Built with ❤️ using Python, MySQL, Flask, and NetworkX**