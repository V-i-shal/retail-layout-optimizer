# Windows 11 Setup Guide - Retail Layout Optimizer

Complete step-by-step guide for running this project on Windows 11 with PowerShell.

## 📋 Quick Reference Commands

### One-Time Setup

```powershell
# 1. Navigate to project
cd C:\Users\visha\Documents\Projects\retail-layout-optimizer

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Generate and load data (first time only)
python -m app.pipeline.simulate_data
python -m app.pipeline.run_all --rebuild

# 4. Start dashboard
python -m app.dashboard.server
```

### Daily Usage

```powershell
# Start working session
cd C:\Users\visha\Documents\Projects\retail-layout-optimizer
.\venv\Scripts\Activate.ps1

# Run pipeline (if needed)
python -m app.pipeline.run_all --skip-ingest

# Start dashboard
python -m app.dashboard.server

# In browser: http://localhost:5000
```

## 🔄 Complete Workflow

### Fresh Start (Reset Everything)

```powershell
# 1. Drop and recreate database
mysql -u root -p -e "DROP DATABASE IF EXISTS retail_optimizer; CREATE DATABASE retail_optimizer;"

# 2. Load schema
mysql -u root -p retail_optimizer < sql\schema.sql
mysql -u root -p retail_optimizer < sql\seed.sql

# 3. Generate new data
python -m app.pipeline.simulate_data

# 4. Run full pipeline
python -m app.pipeline.run_all --rebuild

# 5. Launch dashboard
python -m app.dashboard.server
```

### Update Data Only

```powershell
# Generate new customer paths
python -m app.pipeline.simulate_data

# Reload and reprocess
python -m app.pipeline.run_all --rebuild
```

### Rerun Analysis (Keep Data)

```powershell
# Reprocess existing data
python -m app.pipeline.run_all --skip-ingest
```

## 🛠 VS Code Integration

### Open Project in VS Code

```powershell
# From project root
code .
```

### Run/Debug in VS Code

1. **Run Pipeline**: Press `F5` → Select "Python: Run Pipeline"
2. **Run Dashboard**: Press `F5` → Select "Flask: Dashboard Server"
3. **Run Tests**: Press `F5` → Select "Pytest: Run Tests"
4. **Current File**: Press `F5` → Select "Python: Current File"

### Useful VS Code Shortcuts

- `Ctrl + Shift + P` - Command palette
- `Ctrl + J` - Toggle terminal
- `Ctrl + B` - Toggle sidebar
- `F5` - Start debugging
- `Shift + F5` - Stop debugging
- `Ctrl + Shift + F5` - Restart debugging

## 📊 Verify Installation

### Check Database

```powershell
# Connect to MySQL
mysql -u root -p retail_optimizer

# Run queries
SELECT COUNT(*) FROM store_section;  -- Should be 26
SELECT COUNT(*) FROM product;        -- Should be 100
SELECT COUNT(*) FROM movement;       -- Should be ~91000
SELECT COUNT(*) FROM graph_edge;     -- Should be ~650
SELECT COUNT(*) FROM recommendation; -- Should be 26

# Exit
EXIT;
```

### Test Python Modules

```powershell
# Test database connection
python test_connection.py

# Test API endpoints
python -c "import requests; print(requests.get('http://localhost:5000/api/health').json())"

# Run all tests
pytest tests/ -v
```

## 🐛 Common Issues & Fixes

### Issue: Virtual Environment Not Activating

```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try activating again
.\venv\Scripts\Activate.ps1
```

### Issue: MySQL Connection Refused

```powershell
# Check MySQL service status (Windows Services)
# Or restart MySQL from command line
net stop MySQL80
net start MySQL80

# Verify credentials in .env file
```

### Issue: Port 5000 Already in Use

```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with actual number)
taskkill /PID <PID> /F

# Or run on different port
python -m flask run --port 5001
```

### Issue: Module Not Found

```powershell
# Ensure you're in project root
cd C:\Users\visha\Documents\Projects\retail-layout-optimizer

# Verify virtual environment is active (should see (venv) in prompt)
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Dashboard Shows No Data

```powershell
# Run the pipeline first
python -m app.pipeline.run_all --skip-ingest

# Check database has data
mysql -u root -p retail_optimizer -e "SELECT COUNT(*) FROM recommendation;"

# Restart dashboard
python -m app.dashboard.server
```

## 📦 Project Management

### Update Dependencies

```powershell
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade flask

# Generate new requirements file
pip freeze > requirements.txt
```

### Backup Database

```powershell
# Backup to file
mysqldump -u root -p retail_optimizer > backup.sql

# Restore from backup
mysql -u root -p retail_optimizer < backup.sql
```

### Export Results

```powershell
# Export recommendations to CSV
mysql -u root -p retail_optimizer -e "SELECT * FROM recommendation" > recommendations.csv

# Export graph edges
mysql -u root -p retail_optimizer -e "SELECT * FROM graph_edge" > graph_edges.csv
```

## 🚀 Performance Tips

### Speed Up Pipeline

```powershell
# Use skip-ingest for faster reruns
python -m app.pipeline.run_all --skip-ingest

# Run only specific steps
python -m app.pipeline.optimize_layout
```

### Optimize Database

```sql
-- Connect to MySQL
mysql -u root -p retail_optimizer

-- Analyze tables
ANALYZE TABLE movement, graph_edge, recommendation;

-- Check indexes
SHOW INDEX FROM movement;
```

## 📁 File Locations

### Configuration
- **Environment**: `C:\Users\visha\Documents\Projects\retail-layout-optimizer\.env`
- **VS Code Settings**: `.vscode\settings.json`

### Data
- **Customer Paths**: `data\sample_paths.csv`
- **Products**: `data\sample_products.csv`

### Database
- **Schema**: `sql\schema.sql`
- **Seed Data**: `sql\seed.sql`

### Logs
- Flask logs: Console output
- Pipeline logs: Console output with timestamps

## 🔐 Security Notes

### Production Deployment

If deploying to production:

1. **Change SECRET_KEY** in `.env`
2. **Use strong MySQL password**
3. **Set FLASK_DEBUG=False**
4. **Enable HTTPS**
5. **Add authentication to dashboard**
6. **Restrict database access**

### Environment Variables

Never commit `.env` file to git! It contains:
- Database passwords
- Secret keys
- Configuration specific to your machine

## 📚 Learning Resources

### Python & Flask
- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Tutorial: https://docs.sqlalchemy.org/

### Data Science
- NetworkX Guide: https://networkx.org/documentation/
- Scikit-learn User Guide: https://scikit-learn.org/stable/user_guide.html
- Pandas Documentation: https://pandas.pydata.org/docs/

### Optimization
- SciPy Optimize: https://docs.scipy.org/doc/scipy/reference/optimize.html
- Linear Assignment: https://en.wikipedia.org/wiki/Hungarian_algorithm

## 🎯 Next Steps

### Enhance the Project

1. **Add Authentication**: Implement user login for dashboard
2. **Real-time Updates**: Use WebSockets for live data
3. **More Visualizations**: Add 3D plots, animated transitions
4. **Advanced Algorithms**: Try different clustering methods
5. **API Extensions**: Add POST endpoints for data updates
6. **Export Features**: Generate PDF reports
7. **Docker Setup**: Create Dockerfile for easy deployment

### Portfolio Presentation

1. **Demo Video**: Record dashboard walkthrough
2. **Blog Post**: Write about technical decisions
3. **GitHub**: Push to repository with detailed README
4. **Documentation**: Add API documentation with Swagger
5. **Presentation**: Create slides explaining the system

## 📞 Support

If you encounter issues:

1. Check [Troubleshooting](#-common-issues--fixes) section
2. Review main [README.md](README.md)
3. Check error messages in console
4. Verify all prerequisites installed
5. Ensure `.env` file configured correctly

---

**Happy Coding! 🚀**