import os
import socket
import logging
from contextlib import contextmanager
from typing import Optional, Generator
import oracledb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OracleConnectionPool:

    _instance: Optional['OracleConnectionPool'] = None
    _pool: Optional[oracledb.ConnectionPool] = None

    def __new__(cls):
        """Singleton pattern to ensure only one pool instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize connection pool if not already initialized"""
        if OracleConnectionPool._pool is None:
            self._initialize_pool()

    @staticmethod
    def _get_config() -> dict:
        """
        Retrieve database configuration from environment variables.
        
        Required Environment Variables (from .env):
        - DB_DSN: Database connection string (format: host:port/service_name)
        - DB_USER: Database username
        - DB_PASSWORD: Database password
        
        Returns:
            dict: Database configuration
        """
        # Load environment variables
        db_dsn = os.getenv('DB_DSN')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')

        # Validate required configuration
        required_vars = {'DB_DSN': db_dsn, 'DB_USER': db_user, 'DB_PASSWORD': db_password}
        missing = [k for k, v in required_vars.items() if not v]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        # Parse DSN format: "host:port/service_name"
        try:
            if ':' in db_dsn and '/' in db_dsn:
                host_port, service_name = db_dsn.split('/', 1)
                host, port = host_port.rsplit(':', 1)
                port = int(port)
            else:
                raise ValueError("DSN format should be 'host:port/service_name'")
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid DB_DSN format. Expected 'host:port/service_name', got '{db_dsn}': {str(e)}")

        host = host.strip()
        service_name = service_name.strip()

        if host.lower() == 'db':
            try:
                socket.getaddrinfo(host, None)
            except OSError:
                fallback_host = os.getenv('DB_DSN_LOCAL_HOST', '127.0.0.1')
                logger.warning(
                    f"Host '{host}' is not resolvable from this environment. "
                    f"Falling back to '{fallback_host}' for local host access."
                )
                host = fallback_host

        config = {
            'host': host,
            'port': port,
            'service_name': service_name,
            'user': db_user,
            'password': db_password,
        }

        logger.info(f"Database config loaded: {config['host']}:{config['port']}/{config['service_name']}")
        return config

    def _initialize_pool(self) -> None:
        """
        Initialize the Oracle connection pool with production settings.
        
        Pool Configuration:
        - min: Minimum connections in pool
        - max: Maximum connections in pool
        - increment: Connections to create when pool needs more
        - timeout: Connection request timeout (seconds)
        - session_timeout: Idle session timeout (seconds)
        - max_lifetime_session: Maximum session lifetime (seconds)
        - threaded: Enable threaded mode for multi-threaded applications
        """
        try:
            config = self._get_config()
            
            # Build connection string
            dsn = oracledb.makedsn(
                host=config['host'],
                port=config['port'],
                service_name=config['service_name']
            )

            # Create connection pool with production settings
            OracleConnectionPool._pool = oracledb.create_pool(
                user=config['user'],
                password=config['password'],
                dsn=dsn,
                min=5,                          # Minimum 5 connections
                max=20,                         # Maximum 20 connections
                increment=2,                    # Create 2 connections at a time
                max_lifetime_session=3600,      # 1-hour max session lifetime
                wait_timeout=10,                # Wait up to 10 seconds if no conn available
            )

            logger.info(
                f"Oracle connection pool initialized: "
                f"host={config['host']}, port={config['port']}, "
                f"service={config['service_name']}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Oracle connection pool: {str(e)}")
            raise

    @contextmanager
    def get_connection(self) -> Generator:
        """
        Context manager to get a connection from the pool.
        
        Usage:
            with pool.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM table")
        
        Yields:
            Connection: Oracle database connection
            
        Raises:
            Exception: If connection cannot be acquired
        """
        connection = None
        try:
            if OracleConnectionPool._pool is None:
                raise RuntimeError("Connection pool not initialized")

            connection = OracleConnectionPool._pool.acquire()
            logger.debug("Connection acquired from pool")
            yield connection

        except oracledb.DatabaseError as e:
            logger.error(f"Database error occurred: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting connection: {str(e)}")
            raise
        finally:
            if connection is not None:
                try:
                    connection.close()
                    logger.debug("Connection returned to pool")
                except Exception as e:
                    logger.warning(f"Error closing connection: {str(e)}")

    @staticmethod
    def execute_query(query: str, params: tuple = None) -> list:
        """
        Execute a SELECT query and return all results.
        
        Args:
            query (str): SQL SELECT query
            params (tuple): Query parameters for parameterized queries
            
        Returns:
            list: List of tuples containing query results
        """
        pool = OracleConnectionPool()
        try:
            with pool.get_connection() as connection:
                cursor = connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    @staticmethod
    def execute_update(query: str, params: tuple = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query (str): SQL DML query
            params (tuple): Query parameters for parameterized queries
            
        Returns:
            int: Number of rows affected
        """
        pool = OracleConnectionPool()
        try:
            with pool.get_connection() as connection:
                cursor = connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                rows_affected = cursor.rowcount
                connection.commit()
                logger.info(f"Query executed successfully, rows affected: {rows_affected}")
                return rows_affected
        except Exception as e:
            logger.error(f"Update execution failed: {str(e)}")
            raise

    @staticmethod
    def execute_many(query: str, params_list: list) -> int:
        """
        Execute bulk insert/update operations.
        
        Args:
            query (str): SQL DML query
            params_list (list): List of parameter tuples
            
        Returns:
            int: Number of rows affected
        """
        pool = OracleConnectionPool()
        try:
            with pool.get_connection() as connection:
                cursor = connection.cursor()
                cursor.executemany(query, params_list)
                rows_affected = cursor.rowcount
                connection.commit()
                logger.info(f"Bulk operation completed, rows affected: {rows_affected}")
                return rows_affected
        except Exception as e:
            logger.error(f"Bulk execution failed: {str(e)}")
            raise

    def close_pool(self) -> None:
        """
        Close all connections in the pool gracefully.
        Call during application shutdown.
        """
        try:
            if OracleConnectionPool._pool is not None:
                OracleConnectionPool._pool.close()
                OracleConnectionPool._pool = None
                logger.info("Connection pool closed successfully")
        except Exception as e:
            logger.error(f"Error closing connection pool: {str(e)}")
            raise

    def get_pool_stats(self) -> dict:
        """
        Get connection pool statistics for monitoring.
        
        Returns:
            dict: Pool statistics including opened, in-use, and busy connections
        """
        if OracleConnectionPool._pool is None:
            return {}

        try:
            return {
                'opened': OracleConnectionPool._pool.opened(),
                'in_use': OracleConnectionPool._pool.busy(),
                'available': OracleConnectionPool._pool.opened() - OracleConnectionPool._pool.busy(),
                'max_connections': OracleConnectionPool._pool.max,
                'min_connections': OracleConnectionPool._pool.min,
            }
        except Exception as e:
            logger.error(f"Error getting pool stats: {str(e)}")
            return {}


# Convenience function for singleton access
def get_db_pool() -> OracleConnectionPool:
    """Get or create the global database connection pool"""
    return OracleConnectionPool()


# Application lifecycle hooks for FastAPI
async def init_db():
    """Initialize database pool (call on application startup)"""
    try:
        get_db_pool()
        logger.info("Database pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {str(e)}")
        raise


async def close_db():
    """Close database pool (call on application shutdown)"""
    try:
        pool = get_db_pool()
        pool.close_pool()
        logger.info("Database pool closed successfully")
    except Exception as e:
        logger.error(f"Failed to close database pool: {str(e)}")


def fetch_data(cursor, obj_name: str, args: list, is_func: bool = False):
    """Utility to execute Oracle Procedures/Functions and return dict lists."""
    if is_func:
        res_cursor = cursor.callfunc(obj_name, oracledb.CURSOR, args)
    else:
        p_cursor = cursor.var(oracledb.CURSOR)
        call_args = args + [p_cursor]
        cursor.callproc(obj_name, call_args)
        res_cursor = p_cursor.getvalue()
    
    if not res_cursor:
        return []
        
    try:
        cols = [col[0].lower() for col in res_cursor.description]
        return [dict(zip(cols, row)) for row in res_cursor.fetchall()]
    finally:
        if res_cursor:
            res_cursor.close()