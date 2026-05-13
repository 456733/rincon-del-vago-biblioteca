-- Script SQL Generado por SQLAlchemy --

CREATE TABLE autores (
	id INTEGER NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	nacionalidad VARCHAR(50), 
	PRIMARY KEY (id)
);
------------------------------
CREATE TABLE categorias (
	id INTEGER NOT NULL, 
	nombre VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nombre)
);
------------------------------
CREATE TABLE usuarios (
	id INTEGER NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	email VARCHAR(100), 
	telefono VARCHAR(20), 
	PRIMARY KEY (id)
);
------------------------------
CREATE TABLE libros (
	id INTEGER NOT NULL, 
	titulo VARCHAR(200) NOT NULL, 
	categoria_id INTEGER, 
	fecha_publicacion DATE, 
	autor_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(categoria_id) REFERENCES categorias (id), 
	FOREIGN KEY(autor_id) REFERENCES autores (id)
);
------------------------------
CREATE TABLE prestamos (
	id INTEGER NOT NULL, 
	libro_id INTEGER, 
	usuario_id INTEGER, 
	fecha_prestamo DATE NOT NULL, 
	fecha_devolucion DATE NOT NULL, 
	fecha_entrega DATE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(libro_id) REFERENCES libros (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
);
------------------------------
