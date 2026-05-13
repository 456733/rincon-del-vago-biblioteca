from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Configuramos la conexión a SQLite con ruta absoluta al directorio actual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'biblioteca.db')
engine = create_engine(f'sqlite:///{db_path}', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Autor(Base):
    __tablename__ = 'autores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    nacionalidad = Column(String(50))
    
    # Relación: Un autor tiene muchos libros
    libros = relationship("Libro", back_populates="autor")

class Categoria(Base):
    __tablename__ = 'categorias'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)
    
    # Relación: Una categoría tiene muchos libros
    libros = relationship("Libro", back_populates="categoria")

class Libro(Base):
    __tablename__ = 'libros'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias.id')) # Relación con tabla categorias
    fecha_publicacion = Column(Date)
    autor_id = Column(Integer, ForeignKey('autores.id')) # Relación con tabla autores
    
    # Relación inversa
    autor = relationship("Autor", back_populates="libros")
    categoria = relationship("Categoria", back_populates="libros")
    
    # Relación hacia préstamos
    prestamos = relationship("Prestamo", back_populates="libro")

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))
    
    # Relación hacia préstamos
    prestamos = relationship("Prestamo", back_populates="usuario")

class Prestamo(Base):
    __tablename__ = 'prestamos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    libro_id = Column(Integer, ForeignKey('libros.id'))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    fecha_prestamo = Column(Date, nullable=False)
    fecha_devolucion = Column(Date, nullable=False) # Fecha límite
    fecha_entrega = Column(Date, nullable=True) # Cuando realmente lo devolvió
    
    # Relaciones para poder acceder al objeto Libro o Usuario desde el préstamo
    libro = relationship("Libro", back_populates="prestamos")
    usuario = relationship("Usuario", back_populates="prestamos")
