from flask import Flask, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from nlp.responder import obtener_datos_financieros
from nlp.processor import procesar_texto
from data.financial_api import (
    obtener_top5_criptos,
    obtener_listado_criptos,
    obtener_tasas_plazofijo,
    obtener_top5_acciones,
    obtener_listado_acciones,
    obtener_cuentas_remuneradas,
    obtener_cotizaciones_dolar,
    obtener_riesgo_pais,
    obtener_riesgo_pais_historico,
    obtener_indice_inflacion,
    obtener_indice_inflacion_interanual
)

# CONFIGURACIÓN DE FLASK Y BASE DE DATOS
app = Flask(__name__, template_folder="../frontend", static_folder="../frontend")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/chatbot_finanzas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización del ORM
db = SQLAlchemy(app)


# MODELOS DE BASE DE DATOS
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    chat_id = db.Column(db.String(50), unique=True)
    preferencias = db.Column(db.String(200))
    creado_en = db.Column(db.DateTime, default=datetime.now)

class Mensaje(db.Model):
    __tablename__ = 'mensajes'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    texto = db.Column(db.Text)
    respuesta = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.now)


# RUTA PRINCIPAL
@app.route("/")
def home():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html"))
    with open(path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return render_template_string(html_content)


# RUTA PARA RECIBIR MENSAJES DEL CHAT
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()
    mensaje_usuario = data.get("message", "").strip()

    if not mensaje_usuario:
        return jsonify({"response": "⚠️ No recibí ningún mensaje, escribí algo por favor."})

    print(f"💬 Usuario: {mensaje_usuario}")

    # Procesamiento NLP
    intencion = procesar_texto(mensaje_usuario)
    respuesta_bot = obtener_datos_financieros(intencion, mensaje_usuario)

    # Guardar en la BD
    nuevo_msg = Mensaje(texto=mensaje_usuario, respuesta=respuesta_bot)
    db.session.add(nuevo_msg)
    db.session.commit()

    return jsonify({"response": respuesta_bot})


# INICIO DEL SERVIDOR
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # crea las tablas si no existen
    print("✅ Base de datos conectada y tablas listas.")
    print("🚀 Servidor ejecutándose en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)