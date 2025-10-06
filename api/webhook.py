from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Tus secretos (para el grupo PING)
TELEGRAM_TOKEN = "7959634574:AAHSjTKvWLuakrAKxU4GQ4err6xOzasy59E"
CHAT_ID = "-100096725017"  # CHAT_ID del grupo PING

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'error': 'No data'}), 400
        
        # Saca el mensaje del aviso
        mensaje = data.get('mensaje', '¡Alerta de Kemet! Algo pasó en el mercado. 🦁')
        
        # Si no hay 'mensaje', usa el texto completo
        if not mensaje:
            mensaje = str(data)
        
        # Manda el mensaje a Telegram (al grupo PING)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {
            'chat_id': CHAT_ID,
            'text': mensaje,
            'parse_mode': 'HTML'  # Para emojis y negritas
        }
        response = requests.post(url, params=params)
        
        if response.status_code == 200:
            return jsonify({'ok': True, 'mensaje_enviado': mensaje}), 200
        else:
            return jsonify({'error': f'Fallo en Telegram: {response.text}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
