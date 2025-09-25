import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Union
import logging
from config import get_config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de conexiones a PostgreSQL"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self._pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Inicializa el pool de conexiones"""
        try:
            self._pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **self.config.DATABASE.connection_params
            )
            logger.info("✅ Pool de conexiones PostgreSQL inicializado")
        except Exception as e:
            logger.error(f"❌ Error inicializando pool de conexiones: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager para obtener conexión del pool"""
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en conexión de base de datos: {e}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, connection=None, dict_cursor=True):
        """Context manager para obtener cursor"""
        if connection:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = connection.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
        else:
            with self.get_connection() as conn:
                cursor_factory = RealDictCursor if dict_cursor else None
                cursor = conn.cursor(cursor_factory=cursor_factory)
                try:
                    yield cursor
                finally:
                    cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Ejecuta consulta SELECT y retorna resultados"""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cursor:
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {query} - {e}")
            raise
    
    def execute_query_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Ejecuta consulta SELECT y retorna un solo resultado"""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error ejecutando consulta única: {query} - {e}")
            raise
    
    def execute_command(self, command: str, params: tuple = None) -> int:
        """Ejecuta comando INSERT/UPDATE/DELETE y retorna filas afectadas"""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn, dict_cursor=False) as cursor:
                    cursor.execute(command, params)
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"Error ejecutando comando: {command} - {e}")
            raise
    
    def execute_command_returning(self, command: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Ejecuta comando con RETURNING y retorna el resultado"""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cursor:
                    cursor.execute(command, params)
                    conn.commit()
                    result = cursor.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error ejecutando comando returning: {command} - {e}")
            raise
    
    def execute_transaction(self, commands: List[tuple]) -> bool:
        """Ejecuta múltiples comandos en una transacción"""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn, dict_cursor=False) as cursor:
                    for command, params in commands:
                        cursor.execute(command, params)
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Error en transacción: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn, dict_cursor=False) as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Error probando conexión: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Obtiene información de la base de datos"""
        try:
            info = self.execute_query_one("""
                SELECT 
                    version() as postgres_version,
                    current_database() as database_name,
                    current_user as current_user,
                    inet_server_addr() as server_address,
                    inet_server_port() as server_port
            """)
            return info
        except Exception as e:
            logger.error(f"Error obteniendo información de BD: {e}")
            return {}
    
    def close_pool(self):
        """Cierra el pool de conexiones"""
        if self._pool:
            self._pool.closeall()
            logger.info("Pool de conexiones cerrado")

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

# Funciones de conveniencia
def execute_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """Función de conveniencia para consultas"""
    return db_manager.execute_query(query, params)

def execute_query_one(query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
    """Función de conveniencia para consulta única"""
    return db_manager.execute_query_one(query, params)

def execute_command(command: str, params: tuple = None) -> int:
    """Función de conveniencia para comandos"""
    return db_manager.execute_command(command, params)

def execute_command_returning(command: str, params: tuple = None) -> Optional[Dict[str, Any]]:
    """Función de conveniencia para comandos con returning"""
    return db_manager.execute_command_returning(command, params)

# Decorador para manejo de errores de base de datos
def handle_db_errors(func):
    """Decorador para manejo centralizado de errores de BD"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.Error as e:
            logger.error(f"Error de PostgreSQL en {func.__name__}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error general en {func.__name__}: {e}")
            raise
    return wrapper