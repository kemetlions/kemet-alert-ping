from flask import Flask, request, jsonify
import requests
import traceback

app = Flask(__name__)

# Tus secretos (para el grupo PING)
TELEGRAM_TOKEN = "7959634574:AAHSjTKvWLuakrAKxU4GQ4err6xOzasy59E"
CHAT_ID = "5870967116"  # Tu chat personal para prueba

@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        print("Request recibido – Headers:", dict(request.headers))
        data = request.get_json(force=True)
        print("Data recibida:", data)
        
        if not data:
            print("Error: No data")
            return jsonify({'error': 'No data'}), 400
        
        # Saca el mensaje del aviso
        mensaje = data.get('mensaje', '¡Alerta de Kemet! Algo pasó en el mercado. 🦁')
        print("Mensaje extraído:", mensaje)
        
        # Si no hay 'mensaje', usa el texto completo
        if not mensaje:
            mensaje = str(data)
        
        print("Enviando a Telegram – URL:", f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", "Params:", {'chat_id': CHAT_ID, 'text': mensaje, 'parse_mode': 'HTML'})
        
        # Manda el mensaje a Telegram (al grupo PING)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            'chat_id': CHAT_ID,
            'text': mensaje,
            'parse_mode': 'HTML'  # Para emojis y negritas
        }
        response = requests.post(url, params=params)
        print("Response de Telegram:", response.status_code, response.text)
        
        if response.status_code == 200:
            print("Éxito – Mensaje enviado!")
            return jsonify({'ok': True, 'mensaje_enviado': mensaje}), 200
        else:
            print("Fallo en Telegram:", response.status_code, response.text)
            return jsonify({'error': f'Fallo en Telegram: {response.text}'}), 500
            
    except Exception as e:
        error_msg = traceback.format_exc()
        print("Error en webhook:", error_msg)
        return jsonify({'error': str(e)}), 500
