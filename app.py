from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DABATASE_URI'] = 'sqlite://electrohogar.db'
app.config['SQLALCHEMY_TRACK_MODFICATIONS'] = False
db = SQLAlchemy(app)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio
        }

class Carrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    productos = db.relationship('CarritoProducto', back_populates='carrito')
    
class CarritoProducto(db.Model):
    __tablename__ = 'carrito_producto'
    id = db.Column(db.Integer, primary_key=True)
    carrito_id = db.Column(db.Integer, db.ForeignKey('carrito.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    carrito = db.relationship('Carrito', back_populates='productos')
    producto = db.relationship('Producto')
    
@app.route('/')
def serve_html():
    return send_from_directory('.','index.html')

@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.query.all()
    return jsonify([producto.to_dict() for producto in productos])

@app.route('/api/productos/<int:producto_id>', methods=['GET'])
def obtener_productos():
    producto = Producto.query.get(producto_id)
    if producto:
        return jsonify(producto.to_dict())
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

@app.route('/api/carrito/<int:usuario_id>', methods=['GET'])
def obtener_carrito(usuario_id):
    carrito = Carrito.query.filter_by(usuario_id=usuario_id).first()
    if carrito:
        return jsonify([
            {
            'producto': cp.producto.to_dict(),
            'cantidad': cp.cantidad
                        
        }for cp in carrito.productos
                        ])
    else:
        return jsonify({'error': 'Carrito no encontrado'}), 404

@app.route('/api/carrito/<int:usuario_id>', methods=['POST'])
def agregar_al_carrito(usuario_id):
    data = request.json
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)


    if not producto_id or cantidad <= 0:
        return jsonify({'error': 'Datos inválidos'}), 400


    producto = Producto.query.get(producto_id)
    
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404


    carrito = Carrito.query.filter_by(usuario_id=usuario_id).first()
    if not carrito:
        carrito = Carrito(usuario_id=usuario_id)
        db.session.add(carrito)
    
    carrito_producto = CarritoProducto.query.filter_by(carrito_id=carrito.id, producto_id=producto_id).first()
    if carrito_producto:
        carrito_producto.cantidad += cantidad
    else:
        carrito_producto = CarritoProducto(carrito_id=carrito.id, producto_id=producto_id, cantidad=cantidad)
        db.session.add(carrito_producto)

    db.session.commit()
    return jsonify({'mensaje': 'Producto agregado al carrito'}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all
        
        if not Producto.query.first():
            productos = [
                Producto(nombre='TV LED 55"', precio=499.99),
                Producto(nombre='Refrigerador', precio=799.99),
                Producto(nombre='Lavadora', precio=399.99),
            ]
            db.session.add_all(productos)
            db.session.commit()
    app.run(debug=True)
        

