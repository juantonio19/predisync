from flask import Flask, render_template, request, url_for, session
from flask_migrate import Migrate
from sqlalchemy import func
from werkzeug.utils import redirect
from data_service import prediccion_lineal, prediccion_bosque

from database import db
from models import *
from forms import *


app = Flask(__name__)

# configuracion de la base de datos
USER_DB = 'postgres'
PASS_DB = 'admin'
URL_DB = 'localhost'
NAME_DB = 'tienda_web'
FULL_URL_DB = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ININICAR EL OBJETO SQLALCHEMY


db.init_app(app)

# CONFIGURAR FLASK-MIGRATE

migrate = Migrate()
migrate.init_app(app, db)

# Configuracion de flask-wtf, CSRF
app.config['SECRET_KEY'] = 'LlaveSecreta'


@app.route('/')  #Pagina principal
@app.route('/index')
@app.route('/index.html')
def inicio():
    return render_template("index.html")



@app.route('/registro', methods=['GET', 'POST'])  # Registrarse en la pagina
def agregarCliente():
    if 'cliente' in session:
        return redirect(url_for('HomeClientes'))  # Comprobar si ya se inicio sesion
    else:
        cliente = Cliente() # se cera un nuevo objeto
        clienteForm = ClienteForm(obj=cliente) # se crea un nuevo formulario
        if request.method == 'POST': # si es un metodo que envvia informacion
            if clienteForm.validate_on_submit(): #valida que se llene el formulario
                clienteForm.populate_obj(cliente) # LLENA EL OBJETO CON EL FORMULARIO
                app.logger.debug(f'cliente: {cliente}')
                # Insertar nuevo registro
                db.session.add(cliente) #inserta en la db
                db.session.commit()# guarda en la db
                return redirect(url_for('inicio'))
        return render_template('RegistroUsuarios.html', forma=clienteForm)


@app.route('/login', methods=['GET', 'POST'])  # Iniciar sesion
def login():
    if 'cliente' in session:
        return redirect(url_for('HomeClientes'))  # Comprobar si ya se inicio sesion
    else:
        if request.method == 'POST':
            correo = request.form['email']
            contraseña = request.form['password']

            cliente = Cliente.query.filter_by(correo=correo).first()
            if cliente is not None and cliente.contraseña == contraseña:
                session['cliente'] = cliente.id_cliente
                return redirect(url_for('HomeClientes', cliente=cliente))
            else:
                error = 'Correo o contraseña incorrectos'
                return render_template('login.html', error=error)
        else:
            return render_template('login.html')

@app.route('/home/clientes')  # Pagina principal de clientes
def HomeClientes():
    return render_template('PaginaUsuarios.html')


@app.route('/logout')  # Cerrar  sesion clientes
def logout():
    session.pop('cliente')
    return redirect(url_for('inicio'))


@app.route('/admin', methods=['GET', 'POST'])  # Iniciar sesion para empleados
def AdminLogin():
    # if 'empleado' in session:
    #   return redirect(url_for('HomeAdmin')) # Comprobar si ya se inicio sesion
    # else:
    if request.method == 'POST':
        correo_empleado = request.form['email']
        contraseña = request.form['password']
        empleado = Empleado.query.filter_by(correo_empleado=correo_empleado).first()
        app.logger.debug(f'cliente: {empleado}')
        if empleado is not None and empleado.contraseña == contraseña:
            session['empleado'] = empleado.id_empleado
            if empleado.tipo_empleado == "admin":  # Comprovar que tipo de empleado es
                return redirect(url_for('HomeAdmin'))
        else:
            error = 'Correo o contraseña incorrectos'
            return render_template('AdminLogin.html', error=error)
    else:
        return render_template('AdminLogin.html')



@app.route('/home/admin')  # Pagina principal de Empleaddos
def HomeAdmin():
    return render_template('admin.html')


@app.route('/logoutAdmin')  # Cerrar sesion
def logout2():
    session.pop('empleado')
    return redirect(url_for('inicio'))


@app.route('/AgregarEmpleado', methods=['GET', 'POST'])  # Agregar Empleddos
def AgregarEmpleado():
    empleado = Empleado()
    empleadoForm = EmpleadoFomr(obj=empleado)
    max_id = db.session.query(db.func.max(Empleado.id_empleado)).scalar() # se obtiiene el id maximo el la BD
    if max_id:
        max_id += 1  # si existen valores  se incrementa en uno el id para que sea el nuevo maximo
    else:
        max_id = 1  # si no existen valores se inicia en 1
    if request.method == 'POST':
        if empleadoForm.validate_on_submit():
            empleadoForm.populate_obj(empleado)
            empleado.id_empleado=max_id  # se inserta el id maximo al nuevo registro
            # Insertar nuevo registro
            db.session.add(empleado) # se agrega a la db
            db.session.commit() # se guarda
            return redirect(url_for('HomeAdmin'))
    return render_template('RegistroEmpleado.html', forma=empleadoForm, max_id=max_id)


@app.route('/Agregar/producto', methods=['GET', 'POST'])  # Agregar Productos
def agregarProducto():
    producto = Producto()
    productoForm = ProductoForm(obj=producto)
    max_id = db.session.query(db.func.max(Producto.id_producto)).scalar()  # se obtiiene el id maximo el la BD
    if max_id:
        max_id += 1  # si existen valores  se incrementa en uno el id para que sea el nuevo maximo
    else:
        max_id = 1  # si no existen valores se inicia en 1
    if request.method == 'POST':
        if productoForm.validate_on_submit():
            productoForm.populate_obj(producto)
            # Insertar nuevo
            producto.id_producto=max_id
            db.session.add(producto)
            db.session.commit()
            return redirect(url_for('HomeAdmin'))
    return render_template('RegistroProducto.html', forma=productoForm, max_id=max_id)\


@app.route('/Agregar/proveedor', methods=['GET', 'POST'])  # Agregar Productos
def agregarProveedor():
    provedor = Provedor()
    proveedor_form = ProvedorForm(obj=provedor)
    max_id = db.session.query(db.func.max(Provedor.id_provedor)).scalar()  # se obtiiene el id maximo el la BD
    if max_id:
        max_id += 1  # si existen valores  se incrementa en uno el id para que sea el nuevo maximo
    else:
        max_id = 1  # si no existen valores se inicia en 1
    if request.method == 'POST':
        if proveedor_form.validate_on_submit():
            proveedor_form.populate_obj(provedor)
            # Insertar nuevo
            provedor.id_provedor=max_id
            db.session.add(provedor)
            db.session.commit()
            return redirect(url_for('HomeAdmin'))
    return render_template('RegistroProvedor.html', forma=proveedor_form, max_id=max_id)


@app.route('/consultas')  # principal de consultas
def consultas():
    return render_template('consultas.html')


# Consultas


@app.route('/Catalogo')
def Catalogo():
    producto = Producto.query.order_by('id_producto')
    return render_template('catalogo.html', producto=producto)




#Editar-Eliminar-Consultar Productos
@app.route('/consultas/Productos')  # cosultas de clientes
def consultasProducto():
    producto = Producto.query.order_by('id_producto')
    return render_template('consultas-Producto.html', producto=producto)


@app.route('/editar/producto/<int:id_producto>', methods=['GET', 'POST'])  # editar producto
def editarProducto(id_producto):
    produucto = Producto.query.get_or_404(id_producto)  # Busca el id o genera error
    productoForm = ProductoForm(obj=produucto)  # Formulario a utilizar con wtf
    if request.method == 'POST':  # Metodo
        productoForm.populate_obj(produucto)  # Se llena el formulario con los dato de la del objeto almacenado en la bd
        db.session.commit()  # Se guradan los cambios
        return redirect(url_for('consultasProducto'))
    return render_template("editarProducto.html", forma=productoForm)


@app.route('/eliminar/producto/<int:id_producto>', methods=['GET', 'POST']) #eliminar producto
def eliminarProducto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for('consultasProducto'))

@app.route('/predecir/producto/<int:id_producto>')
def prediccion_producto(id_producto):
    if 'empleado' not in session:
        return redirect(url_for('AdminLogin'))
    
    producto = Producto.query.get_or_404(id_producto)
    historial = Historial.query.filter_by(id_producto=id_producto).all()
    
    # Obtenemos ambos resultados
    res_lineal = prediccion_lineal(historial)
    res_bosque = prediccion_bosque(historial)
    
    return render_template('prediccion.html', 
                           producto=producto.nombre_producto, 
                           lineal=res_lineal, 
                           bosque=res_bosque,
                           num_ventas=len(historial))


#Editar-Eliminar-Consultar Empleados
@app.route('/consultas/empleados')
def consultasEmpleados():
    empleado = Empleado.query.order_by('id_empleado')
    return render_template('consultas-empleado.html', empleado=empleado)


@app.route('/editar/empleado/<int:id_empleado>', methods=['GET', 'POST'])  # editar empleados
def editarEmpleado(id_empleado):
    empleado = Empleado.query.get_or_404(id_empleado)  # Busca el id o genera error
    empleadoForm = EmpleadoEditFomr(obj=empleado)  # Formulario a utilizar con wtf
    if request.method == 'POST':  # Metodo
        empleadoForm.populate_obj(empleado)  # Se llena el formulario con los dato de la db
        db.session.commit()  # Se guradan los cambios
        return redirect(url_for('consultasEmpleados'))
    return render_template("editar_empleado.html", forma=empleadoForm)


@app.route('/eliminar/empleado/<int:id_empleado>', methods=['GET', 'POST'])  # eliminar empleados
def eliminarEmpleado(id_empleado):
    empleado = Empleado.query.get_or_404(id_empleado)
    db.session.delete(empleado)
    db.session.commit()
    return redirect(url_for('consultasEmpleados'))


#Editar-Eliminar-Consultar provedores
@app.route('/consultas/Proveedores')
def consultasProveedores():
    proveedor = Provedor.query.order_by('id_provedor')
    return render_template('consultas-proveedor.html', proveedor=proveedor)


@app.route('/editar/provedor/<int:id_provedor>', methods=['GET', 'POST'])  # editar empleados
def editarProveedor(id_provedor):
    provedor = Provedor.query.get_or_404(id_provedor)  # Busca el id o genera error
    provedorForm = ProvedorForm(obj=provedor)  # Formulario a utilizar con wtf
    if request.method == 'POST':  # Metodo
        provedorForm.populate_obj(provedor)  # Se llena el formulario con los dato de la db
        db.session.commit()  # Se guradan los cambios
        return redirect(url_for('consultasProveedores'))
    return render_template("editar-provedor.html", forma=provedorForm)


@app.route('/eliminar/provedor/<int:id_provedor>', methods=['GET', 'POST'])  # eliminar empleados
def eliminarProvedor(id_provedor):
    provedor = Provedor.query.get_or_404(id_provedor)
    db.session.delete(provedor)
    db.session.commit()
    return redirect(url_for('consultasProveedores'))



#Perfil
@app.route('/editar/perfil/<int:id_cliente>', methods=['GET', 'POST'])
def editarPerfil(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)
    clienteForm = ClienteForm2(obj=cliente)
    if request.method == 'POST':
        clienteForm.populate_obj(cliente)
        db.session.commit()
        return redirect(url_for('perfil'))
    return render_template("editar_perfil.html", forma=clienteForm)

@app.route('/perfil')
def perfil():
    if 'cliente' in session:
        id_cliente = session['cliente']
        cliente = Cliente.query.get_or_404(id_cliente)
        return render_template('perfil.html', cliente=cliente)


@app.route('/Catalogo/Usuario')
def CatalogoUsuarios():
    producto = Producto.query.order_by('id_producto')
    return render_template('catalogo_usuario.html', producto=producto)



@app.route("/agregar/carrito/<int:id_producto>")
def AgregarCarrito(id_producto):
    carrito = Carrito.query.filter_by(id_producto=id_producto).first()
    if carrito is not None:
        carrito.cantidad += 1
    else:
        max_id = db.session.query(db.func.max(Carrito.id_carrito)).scalar()  # se obtiiene el id maximo el la BD
        if max_id:
            max_id += 1  # si existen valores  se incrementa en uno el id para que sea el nuevo maximo
        else:
            max_id = 1  # si no existen valores se inicia en 1
        nuevo_carrito = Carrito()
        nuevo_carrito.id_producto=id_producto
        nuevo_carrito.id_carrito=max_id
        nuevo_carrito.cantidad = 1
        db.session.add(nuevo_carrito)
    db.session.commit()
    return redirect(url_for("CatalogoUsuarios"))



@app.route("/miCarrito")
def VerCarrito():

    # Obtener todos los id_producto del carrito
    id_productos = [carrito.id_producto for carrito in Carrito.query.with_entities(Carrito.id_producto).all()]

    productos_en_carrito = Producto.query.filter(Producto.id_producto.in_(id_productos)).all()

    cantidades_en_carrito = {}
    for carrito in Carrito.query.all():
        cantidades_en_carrito[carrito.id_producto] = carrito.cantidad

    total = 0
    for producto in productos_en_carrito:
        cantidad = cantidades_en_carrito[producto.id_producto]
        subtotal = cantidad * producto.precio
        total += subtotal

    # Renderizar el archivo HTML y pasar los productos, cantidades y total al template
    return render_template('MiCarrito.html', productos=productos_en_carrito, cantidades=cantidades_en_carrito, total=total)



@app.route("/eliminar/carrito/<int:id_producto>")
def EliminarCarrito(id_producto):
    carrito = Carrito.query.filter_by(id_producto=id_producto).first()

    if carrito is not None:
        if carrito.cantidad > 1:
            # El producto tiene una cantidad mayor a 1, disminuir cantidad
            carrito.cantidad -= 1
        else:
            # El producto tiene una cantidad de 1, eliminar registro
            db.session.delete(carrito)

        db.session.commit()
    return redirect(url_for("VerCarrito"))



@app.route("/Comprar")
def Comprar():
    carrito = Carrito.query.order_by('id_producto')
    id_cliente = session['cliente']
    lista_historial = []
    for carritos in carrito:
        historial = Historial()
        historial.id_producto = carritos.id_producto
        historial.id_cliente = id_cliente
        historial.cantidad = carritos.cantidad
        lista_historial.append(historial)
    db.session.add_all(lista_historial)
    carrito2 = Carrito.query.all()
    # Eliminar cada objeto de la tabla
    for item in carrito2:
        db.session.delete(item)
    db.session.commit()
    return  redirect(url_for("HomeClientes"))



@app.route("/historial")
def VerHistorial():
    id_cliente = session['cliente']
    historial = Historial.query.filter(Historial.id_cliente == id_cliente).all()
    ids = []
    cantidades_en_carrito = {}
    for h in historial:
        ids.append(h.id_producto)
        app.logger.debug(f'Listado Personas: {ids}')
        cantidades_en_carrito[h.id_producto] = h.cantidad
    productos = db.session.query(Producto).filter(Producto.id_producto.in_(ids)).all()
    return render_template('historial.html', producto=productos, cantidades=cantidades_en_carrito)