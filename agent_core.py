import os
import subprocess
import platform
import requests
import json
import google.generativeai as genai
import pygetwindow as gw
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
        """Interface via SDK Oficial com Auto-Correção Neural"""
        if not self.api_key:
            return "Erro: Chave API não configurada."
        
        # Lista de modelos por ordem de estabilidade
        models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        last_error = ""
        for model_name in models_to_try:
            try:
                self.log(f"Tentando conexão neural via: {model_name}")
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(model_name)
                # O SDK novo prefere o contexto dentro do prompt se o system_instruction falhar em alguns modelos
                full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                response = model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                last_error = str(e)
                self.log(f"Falha no modelo {model_name}: {last_error}")
                continue
        
        return f"Exauridas todas as rotas neurais. Último erro: {last_error}"

    def list_open_windows(self):
        """Habilidade de 'ver' o que está aberto no Windows"""
        windows = gw.getAllTitles()
        active_windows = [w for w in windows if w.strip()]
        self.log(f"Janelas detectadas: {len(active_windows)}")
        return active_windows

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

    def open_browser(self, url):
        """Abre uma URL no navegador padrão do Windows"""
        import webbrowser
        self.log(f"Abrindo navegador em: {url}")
        webbrowser.open(url)
        return f"Navegador aberto em {url}"

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
