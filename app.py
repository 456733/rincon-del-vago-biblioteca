from flask import Flask, render_template, request, redirect, url_for, g
from models import SessionLocal, engine, Base
import models
from datetime import date, datetime
from sqlalchemy import func

app = Flask(__name__)

# Creamos las tablas en la base de datos si no existen
Base.metadata.create_all(engine)

# Función de utilidad para obtener la sesión de la DB usando el contexto de Flask
def get_db():
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/categorias', methods=['GET', 'POST'])
def gestionar_categorias():
    db = get_db()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        nueva_cat = models.Categoria(nombre=nombre)
        db.add(nueva_cat)
        db.commit()
        return redirect(url_for('gestionar_categorias'))
        
    lista_categorias = db.query(models.Categoria).all()
    return render_template('categorias.html', categorias=lista_categorias)

@app.route('/autores', methods=['GET', 'POST'])
def gestionar_autores():
    db = get_db()
    
    if request.method == 'POST':
        # Recibir datos del formulario HTML
        nombre = request.form['nombre']
        nacionalidad = request.form['nacionalidad']
        
        # --- EJEMPLO ORM: CREAR (INSERT) ---
        nuevo_autor = models.Autor(nombre=nombre, nacionalidad=nacionalidad)
        db.add(nuevo_autor) # Agrega el objeto a la sesión
        db.commit()         # Guarda los cambios en la base de datos
        # -----------------------------------
        
        return redirect(url_for('gestionar_autores'))
        
    # --- EJEMPLO ORM: LEER (SELECT ALL) ---
    lista_autores = db.query(models.Autor).all()
    # --------------------------------------
    
    return render_template('autores.html', autores=lista_autores)

@app.route('/libros', methods=['GET', 'POST'])
def gestionar_libros():
    db = get_db()
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        categoria_id = request.form['categoria_id']
        fecha_str = request.form['fecha_publicacion']
        autor_id = request.form['autor_id']
        
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else None
        
        # --- EJEMPLO ORM: CREAR (INSERT) CON RELACIÓN ---
        nuevo_libro = models.Libro(
            titulo=titulo, 
            categoria_id=categoria_id, 
            fecha_publicacion=fecha_obj,
            autor_id=autor_id
        )
        db.add(nuevo_libro)
        db.commit()
        # ------------------------------------------------
        
        return redirect(url_for('gestionar_libros'))
        
    # --- EJEMPLO ORM: LEER MÚLTIPLES TABLAS ---
    lista_libros = db.query(models.Libro).all()
    lista_autores = db.query(models.Autor).all() # Para el select del formulario
    lista_categorias = db.query(models.Categoria).all()
    # ------------------------------------------
    
    return render_template('libros.html', libros=lista_libros, autores=lista_autores, categorias=lista_categorias)

@app.route('/buscar_libro')
def buscar_libro():
    db = get_db()
    criterio = request.args.get('criterio', '')
    autor_id = request.args.get('autor_id', '')
    categoria_id = request.args.get('categoria_id', '')
    
    query = db.query(models.Libro)
    
    if criterio:
        query = query.filter(models.Libro.titulo.ilike(f'%{criterio}%'))
    if autor_id:
        query = query.filter(models.Libro.autor_id == int(autor_id))
    if categoria_id:
        query = query.filter(models.Libro.categoria_id == int(categoria_id))
        
    resultados = query.all() if (criterio or autor_id or categoria_id) else []
    
    autores = db.query(models.Autor).all()
    categorias = db.query(models.Categoria).all()
        
    return render_template('buscar.html', libros=resultados, criterio=criterio, 
                           autor_id=autor_id, categoria_id=categoria_id,
                           autores=autores, categorias=categorias)

@app.route('/eliminar_libro/<int:id_libro>', methods=['POST'])
def eliminar_libro(id_libro):
    db = get_db()
    
    # --- EJEMPLO ORM: ELIMINAR (DELETE) ---
    libro_a_borrar = db.query(models.Libro).filter(models.Libro.id == id_libro).first()
    if libro_a_borrar:
        db.delete(libro_a_borrar)
        db.commit()
    # --------------------------------------
    
    return redirect(url_for('gestionar_libros'))

@app.route('/prestamos', methods=['GET', 'POST'])
def gestionar_prestamos():
    db = get_db()
    
    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        libro_id = request.form['libro_id']
        fecha_prestamo_str = request.form['fecha_prestamo']
        fecha_devolucion_str = request.form['fecha_devolucion']
        fecha_prestamo_obj = datetime.strptime(fecha_prestamo_str, '%Y-%m-%d').date()
        fecha_devolucion_obj = datetime.strptime(fecha_devolucion_str, '%Y-%m-%d').date()
        
        # Si no hay usuarios, creamos uno por defecto para no romper
        if not usuario_id:
            usuario = db.query(models.Usuario).first()
            if not usuario:
                usuario = models.Usuario(nombre="Lector Genérico", email="lector@demo.com")
                db.add(usuario)
                db.commit()
            usuario_id = usuario.id
            
        nuevo_prestamo = models.Prestamo(
            libro_id=libro_id,
            usuario_id=usuario_id,
            fecha_prestamo=fecha_prestamo_obj,
            fecha_devolucion=fecha_devolucion_obj
        )
        db.add(nuevo_prestamo)
        db.commit()
        return redirect(url_for('gestionar_prestamos'))
        
    lista_prestamos = db.query(models.Prestamo).all()
    lista_libros = db.query(models.Libro).all()
    lista_usuarios = db.query(models.Usuario).all()
    return render_template('prestamos.html', prestamos=lista_prestamos, libros=lista_libros, usuarios=lista_usuarios)

@app.route('/usuarios', methods=['GET', 'POST'])
def gestionar_usuarios():
    db = get_db()
    if request.method == 'POST':
        nuevo_usuario = models.Usuario(
            nombre=request.form['nombre'],
            email=request.form['email'],
            telefono=request.form['telefono']
        )
        db.add(nuevo_usuario)
        db.commit()
        return redirect(url_for('gestionar_usuarios'))
    usuarios = db.query(models.Usuario).all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/eliminar_usuario/<int:id_usuario>', methods=['POST'])
def eliminar_usuario(id_usuario):
    db = get_db()
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario).first()
    if usuario:
        db.delete(usuario)
        db.commit()
    return redirect(url_for('gestionar_usuarios'))

@app.route('/editar_usuario/<int:id_usuario>', methods=['GET', 'POST'])
def editar_usuario(id_usuario):
    db = get_db()
    usuario = db.query(models.Usuario).filter(models.Usuario.id == id_usuario).first()
    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.email = request.form['email']
        usuario.telefono = request.form['telefono']
        db.commit()
        return redirect(url_for('gestionar_usuarios'))
    return render_template('editar.html', tipo='Usuario', obj=usuario)

@app.route('/editar_autor/<int:id_autor>', methods=['GET', 'POST'])
def editar_autor(id_autor):
    db = get_db()
    autor = db.query(models.Autor).filter(models.Autor.id == id_autor).first()
    if request.method == 'POST':
        autor.nombre = request.form['nombre']
        autor.nacionalidad = request.form['nacionalidad']
        db.commit()
        return redirect(url_for('gestionar_autores'))
    return render_template('editar.html', tipo='Autor', obj=autor)

@app.route('/eliminar_autor/<int:id_autor>', methods=['POST'])
def eliminar_autor(id_autor):
    db = get_db()
    autor = db.query(models.Autor).filter(models.Autor.id == id_autor).first()
    if autor:
        db.delete(autor)
        db.commit()
    return redirect(url_for('gestionar_autores'))

@app.route('/eliminar_categoria/<int:id_cat>', methods=['POST'])
def eliminar_categoria(id_cat):
    db = get_db()
    cat = db.query(models.Categoria).filter(models.Categoria.id == id_cat).first()
    if cat:
        db.delete(cat)
        db.commit()
    return redirect(url_for('gestionar_categorias'))

@app.route('/editar_libro/<int:id_libro>', methods=['GET', 'POST'])
def editar_libro(id_libro):
    db = get_db()
    libro = db.query(models.Libro).filter(models.Libro.id == id_libro).first()
    if request.method == 'POST':
        libro.titulo = request.form['titulo']
        libro.categoria_id = request.form['categoria_id']
        fecha_str = request.form['fecha_publicacion']
        libro.fecha_publicacion = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else None
        libro.autor_id = request.form['autor_id']
        db.commit()
        return redirect(url_for('gestionar_libros'))
    
    autores = db.query(models.Autor).all()
    categorias = db.query(models.Categoria).all()
    return render_template('editar.html', tipo='Libro', obj=libro, autores=autores, categorias=categorias)

@app.route('/devolver_prestamo/<int:id_prestamo>', methods=['POST'])
def devolver_prestamo(id_prestamo):
    db = get_db()
    prestamo = db.query(models.Prestamo).filter(models.Prestamo.id == id_prestamo).first()
    if prestamo:
        prestamo.fecha_entrega = date.today()
        db.commit()
    return redirect(url_for('gestionar_prestamos'))

@app.route('/estadisticas')
def ver_estadisticas():
    db = get_db()
    
    # 1. Autor con más libros
    # func.count(models.Libro.id) cuenta los libros. Agrupamos por autor_id.
    autor_top_query = db.query(models.Autor.nombre, func.count(models.Libro.id).label('total')) \
                        .join(models.Libro) \
                        .group_by(models.Autor.id) \
                        .order_by(func.count(models.Libro.id).desc()) \
                        .first()
                        
    # 2. Préstamos vencidos (cuya fecha de devolución ya pasó y no han sido entregados)
    prestamos_vencidos = []
    prestamos_activos = db.query(models.Prestamo).filter(models.Prestamo.fecha_entrega == None).all()
    hoy = date.today()
    for p in prestamos_activos:
        dias_retraso = (hoy - p.fecha_devolucion).days
        if dias_retraso > 0:
            # Le añadimos un atributo temporal al objeto para mostrarlo en HTML
            p.dias_retraso = dias_retraso
            prestamos_vencidos.append(p)
            
    return render_template('estadisticas.html', autor_top=autor_top_query, prestamos_vencidos=prestamos_vencidos)


if __name__ == '__main__':
    # Arrancamos en el puerto 5002 para no chocar con tu aplicación actual
    app.run(debug=True, port=5002)
