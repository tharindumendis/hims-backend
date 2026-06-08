from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
import os
import logging
#database connection imports
from database import init_db, close_db, get_db_pool

# routers
from routers import patients, doctors, appointments, prescriptions, inventory, analytics

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application lifespan management.
    Initializes database pool on startup and closes on shutdown.
    """
    logger.info("Starting up - initializing database pool...")
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {str(e)}")
        raise
    
    yield
    
    logger.info("Shutting down - closing database pool...")
    try:
        await close_db()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


app = FastAPI(lifespan=lifespan, title="Healthcare Inventory Management System")

app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(prescriptions.router)
app.include_router(inventory.router)
app.include_router(analytics.router)


@app.get("/")
async def root():
    return {
        "message": "Healthcare Inventory Management System Backend",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """
    Health check endpoint that verifies database connectivity.
    Returns detailed health status including database connection.
    """
    try:
        pool = get_db_pool()
        
        # Test database connection with a simple query
        result = pool.execute_query("SELECT 1 FROM dual")
        print(f"Health check query result: {result}")
        
        # Get pool statistics
        stats = pool.get_pool_stats()
        
        logger.info("Health check passed - database connection OK")
        
        return {
            "status": "healthy",
            "database": {
                "status": "connected",
                "message": "Database connection successful"
            },
            "pool": {
                "opened_connections": stats.get('opened', 0),
                "active_connections": stats.get('in_use', 0),
                "available_connections": stats.get('available', 0),
                "max_connections": stats.get('max_connections', 20),
            }
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": {
                "status": "disconnected",
                "message": f"Database connection failed: {str(e)}"
            },
            "pool": {
                "opened_connections": 0,
                "active_connections": 0,
                "available_connections": 0,
            }
        }
