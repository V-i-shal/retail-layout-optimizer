"""Flask application for the dashboard."""
from flask import Flask, render_template
from flask_cors import CORS
import logging

from app.config import Config
from app.api.routes import api_bp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['DEBUG'] = Config.FLASK_DEBUG
    
    # Enable CORS
    CORS(app)
    
    # Register API blueprint
    app.register_blueprint(api_bp)
    
    # Dashboard routes
    @app.route('/')
    def index():
        """Render main dashboard."""
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return {'status': 'healthy', 'service': 'Retail Layout Optimizer'}
    
    logger.info("Flask application created successfully")
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    logger.info("Starting Retail Layout Optimizer Dashboard...")
    logger.info(f"Dashboard URL: http://localhost:5000")
    logger.info(f"API Base URL: http://localhost:5000/api")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.FLASK_DEBUG
    )