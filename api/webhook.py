from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
import traceback

app = Flask(__name__)

# Secrets como env vars (seguro – configura em Render > Environment)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '7959634574:AAHSjTKvWLuakrAKxU4GQ4err6xOzasy59E')  # Fallback local
CHAT_ID = os.environ.get('CHAT_ID', '-1002966725017')  # Fallback
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# Verifica secrets
if not TELEGRAM_TOKEN or not CHAT_ID:
    print(f"[{datetime.now()}] ❌ ERRO: TELEGRAM_TOKEN ou CHAT_ID faltando! Configure Env Vars no Render. Usando fallbacks: {TELEGRAM_TOKEN[:10]}.../{CHAT_ID}")
    raise ValueError("Secrets faltando")

@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        # Lee body como texto raw (para text/plain de TradingView)
        raw_body = request.get_data(as_text=True)
        print(f"[{datetime.now()}] POST recebido | Headers: {dict(request.headers)} | Body raw: '{raw_body[:200]}...'")
        
        # Fallback se vazio
        if not raw_body or raw_body.strip() == '':
            raw_body = "Alerta vazia de TradingView (sem mensagem)."
        
        # Usa o body como mensagem
        mensaje = raw_body
        print(f"[{datetime.now()}] Mensagem extraída: '{mensaje[:100]}...'")
        
        # Formata para Telegram (com emoji, hora e negrito)
        formatted_msg = f"🔔 *Alerta TradingView ({datetime.now().strftime('%H:%M UTC')}):*\n\n{mensaje}\n\n*De:* Lista de Selecionados | *IP:* {request.remote_addr}"
        
        print(f"[{datetime.now()}] Enviando para TG: {formatted_msg[:150]}...")
        
        # Envia como JSON para Telegram
        payload = {
            'chat_id': CHAT_ID,
            'text': formatted_msg,
            'parse_mode': 'Markdown'  # Para *negrito* e emojis
        }
        tg_response = requests.post(TELEGRAM_URL, json=payload, timeout=10)
        
        print(f"[{datetime.now()}] Resposta TG: Status {tg_response.status_code} | Texto: {tg_response.text[:200]}")
        
        if tg_response.status_code == 200:
            print(f"[{datetime.now()}] ✅ Éxito – Mensaje enviado ao grupo PING!")
            return jsonify({'ok': True, 'mensaje_enviado': mensaje[:50] + '...', 'tg_status': 200}), 200
        else:
            print(f"[{datetime.now()}] ❌ Falha no TG: {tg_response.status_code} - {tg_response.text}")
            return jsonify({'error': f'Falha no Telegram: {tg_response.text}'}), 500
            
    except Exception as e:
        error_log = traceback.format_exc()
        print(f"[{datetime.now()}] ❌ Erro no webhook: {e}\n{error_log}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def health_check():
    return f"Webhook ativo! Hora: {datetime.now().isoformat()}. TELEGRAM_TOKEN ok: {bool(TELEGRAM_TOKEN)}. Teste: Envie POST para /api/webhook com body texto."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Porta padrão do Render (logs mostram 10000)
    app.run(host='0.0.0.0', port=port, debug=False)
