import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """Configuración de base de datos PostgreSQL"""
    host: str
    port: int
    database: str
    username: str
    password: str
    
    @property
    def connection_url(self) -> str:
        """URL de conexión para PostgreSQL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def connection_params(self) -> dict:
        """Parámetros de conexión como diccionario"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.username,
            'password': self.password
        }

@dataclass 
class AppConfig:
    """Configuración general de la aplicación"""
    debug: bool = False
    testing: bool = False
    secret_key: str = "dev-secret-key"
    log_level: str = "INFO"
    
class Config:
    """Configuración base"""
    
    # Configuración de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
    
    # Configuración de Base de Datos
    DATABASE = DatabaseConfig(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 5432)),
        database=os.environ.get('DB_NAME', 'seguridad_db'),
        username=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'password')
    )
    
    # Configuración de Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOGS_DIR = os.environ.get('LOGS_DIR', '/var/logs/seguridad')
    
    # Configuración de JWT (si necesitas autenticación)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))
    
    # Configuración de Redis (si lo usas para cache/sessions)
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    
    # Configuración de CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Configuración de Rate Limiting
    RATE_LIMIT_STORAGE_URL = os.environ.get('RATE_LIMIT_STORAGE_URL', 'memory://')
    
    @classmethod
    def validate_config(cls) -> list:
        """Valida la configuración y retorna lista de errores"""
        errors = []
        
        # Validar configuración de base de datos
        if not cls.DATABASE.host:
            errors.append("DB_HOST no puede estar vacío")
        if not cls.DATABASE.database:
            errors.append("DB_NAME no puede estar vacío")
        if not cls.DATABASE.username:
            errors.append("DB_USER no puede estar vacío")
        if not cls.DATABASE.password:
            errors.append("DB_PASSWORD no puede estar vacío")
            
        # Validar puerto
        if not (1 <= cls.DATABASE.port <= 65535):
            errors.append("DB_PORT debe estar entre 1 y 65535")
            
        return errors

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def validate_config(cls) -> list:
        """Validaciones adicionales para producción"""
        errors = super().validate_config()
        
        # En producción, secret key no puede ser la default
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            errors.append("SECRET_KEY debe ser cambiado en producción")
            
        return errors

class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    
    # Base de datos de testing
    DATABASE = DatabaseConfig(
        host=os.environ.get('TEST_DB_HOST', 'localhost'),
        port=int(os.environ.get('TEST_DB_PORT', 5432)),
        database=os.environ.get('TEST_DB_NAME', 'seguridad_test_db'),
        username=os.environ.get('TEST_DB_USER', 'postgres'),
        password=os.environ.get('TEST_DB_PASSWORD', 'password')
    )

# Diccionario de configuraciones disponibles
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config() -> Config:
    """Obtiene la configuración basada en la variable de entorno"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)

def validate_environment():
    """Valida que todas las variables de entorno necesarias estén configuradas"""
    config = get_config()
    errors = config.validate_config()
    
    if errors:
        print("❌ Errores de configuración encontrados:")
        for error in errors:
            print(f"  - {error}")
        print("\n💡 Asegúrate de configurar las variables de entorno correctamente")
        return False
    
    print("✅ Configuración validada correctamente")
    return True