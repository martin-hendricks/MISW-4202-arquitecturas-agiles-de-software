from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"mensaje": "Hola, soy un microservicio de Flask!"})

@app.route('/datos')
def get_data():
    data = {
        "id": 1,
        "nombre": "Producto Ejemplo",
        "precio": 99.99
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)