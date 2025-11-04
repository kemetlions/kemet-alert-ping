from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
import traceback

app = Flask(__name__)

# Env vars para Telegram
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

if not BOT_TOKEN or not CHAT_ID:
    print("❌ ERRO: BOT_TOKEN ou CHAT_ID faltando! Verifique Env Vars no Render.")

@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        # Lee o body como texto raw (para text/plain de TradingView)
        raw_body = request.get_data(as_text=True)  # Decodifica UTF-8 automaticamente
        print(f"[{datetime.now()}] Body raw recebido: {raw_body[:200]}...")  # Log truncado
        
        # Se for vazio ou erro, usa fallback
        if not raw_body or raw_body.strip() == '':
            raw_body = "Alerta vazia de TradingView"
        
        # Formata para Telegram (adiciona timestamp e formatação)
        formatted_msg = f"🔔 *Alerta TradingView ({datetime.now().strftime('%H:%M UTC')}):*\n\n{raw_body}\n\n*De:* Lista de Selecionados | *IP:* {request.remote_addr}"
        
        print(f"[{datetime.now()}] Enviando para TG: {formatted_msg[:100]}...")
        
        # Envia para Telegram
        payload = {
            'chat_id': CHAT_ID,
            'text': formatted_msg,
            'parse_mode': 'Markdown'
        }
        tg_response = requests.post(TELEGRAM_URL, json=payload, timeout=10)
        
        print(f"[{datetime.now()}] Resposta TG: Status {tg_response.status_code} | Texto: {tg_response.text[:200]}")
        
        if tg_response.status_code == 200:
            print("✅ Alerta enviada com sucesso para Telegram!")
            return jsonify({"status": "OK", "message_preview": raw_body[:50] + "..."}), 200
        else:
            print(f"❌ Erro no Telegram: {tg_response.status_code} - {tg_response.text}")
            return jsonify({"error": "Falha no Telegram", "details": tg_response.text}), 500
            
    except Exception as e:
        error_log = traceback.format_exc()
        print(f"❌ Erro no webhook: {e}\n{error_log}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def health_check():
    return f"Webhook ativo! Hora: {datetime.now().isoformat()}. BOT_TOKEN ok: {bool(BOT_TOKEN)}. Teste: Envie POST para /api/webhook."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
