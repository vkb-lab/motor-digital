import os
import subprocess
import platform
import requests
import json
import time
from datetime import datetime

class MotorDigitalCore:
    def __init__(self):
        self.os_type = platform.system()
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.workspace = os.path.join(os.path.expanduser("~"), "MotorDigital_Workspace")
        
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
            self.log(f"Workspace criado em: {self.workspace}")

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def call_gemini(self, prompt, system_instruction=""):
        """Interface direta com o cérebro Gemini 1.5 Pro"""
        if not self.api_key:
            return "Erro: Chave API não configurada."
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": f"{system_instruction}\n\n{prompt}"}]
            }],
            "generationConfig": {
                "temperature": 0.9,
                "topP": 1,
                "maxOutputTokens": 2048
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"Falha na conexão neural: {str(e)}"

    def execute_system_command(self, command):
        """Executa comandos no Windows/Mac/Linux local"""
        try:
            self.log(f"Executando: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "code": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}

    def create_project_structure(self, project_name):
        """Exemplo de habilidade: criar pastas e arquivos automaticamente"""
        path = os.path.join(self.workspace, project_name)
        if not os.path.exists(path):
            os.makedirs(path)
            # Cria subpastas padrão
            os.makedirs(os.path.join(path, "docs"))
            os.makedirs(os.path.join(path, "assets"))
            os.makedirs(os.path.join(path, "scripts"))
            self.log(f"Estrutura do projeto '{project_name}' criada com sucesso.")
            return True
        return False

    def autonomous_loop(self):
        """Loop de pensamento e ação do agente"""
        self.log("Motor Digital Core Iniciado. Aguardando diretrizes...")
        # Aqui entra a lógica de 'escutar' comandos ou agir por conta própria
        pass

if __name__ == "__main__":
    agent = MotorDigitalCore()
    # Teste de inicialização
    print(f"Sistema Operacional Detectado: {agent.os_type}")
    print(f"Caminho do Workspace: {agent.workspace}")
