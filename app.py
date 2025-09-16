from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configurações do Mailgun
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
MAILGUN_FROM = os.getenv('MAILGUN_FROM', f'lead-capture@{MAILGUN_DOMAIN}')
MAILGUN_TO = os.getenv('MAILGUN_TO')  # Email para onde enviar os leads

@app.route('/')
def home():
    return jsonify({"message": "MightX Lead Capture API está funcionando!"})

@app.route('/capture_lead', methods=['POST'])
def capture_lead():
    try:
        # Obtém dados do formulário
        data = request.get_json()
        
        # Valida campos obrigatórios
        if not data or 'email' not in data:
            return jsonify({"error": "Email é obrigatório"}), 400
        
        # Prepara dados do lead
        name = data.get('name', 'Não informado')
        email = data.get('email')
        phone = data.get('phone', 'Não informado')
        message = data.get('message', 'Não informada')
        source = data.get('source', 'Site MightX')
        
        # Prepara o email
        subject = f"Novo lead capturado: {name}"
        text = f"""
        Novo lead capturado através do site:
        
        Nome: {name}
        Email: {email}
        Telefone: {phone}
        Mensagem: {message}
        Fonte: {source}
        
        Data/Hora: {request.headers.get('Date', 'Não disponível')}
        """
        
        # Envia email via Mailgun
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"MightX Lead Capture <{MAILGUN_FROM}>",
                "to": [MAILGUN_TO],
                "subject": subject,
                "text": text
            }
        )
        
        # Verifica se o email foi enviado com sucesso
        if response.status_code == 200:
            return jsonify({"message": "Lead capturado e email enviado com sucesso!"}), 200
        else:
            return jsonify({"error": "Falha ao enviar email", "details": response.text}), 500
            
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
