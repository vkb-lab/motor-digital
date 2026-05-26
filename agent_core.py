import os
import subprocess
import platform
import requests
import json
import google.generativeai as genai
import pygetwindow as gw
import pyautogui
import time
import webbrowser
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

    def get_available_models(self):
        """Lista os modelos que a chave de API realmente tem permissão para usar"""
        try:
            genai.configure(api_key=self.api_key)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return models
        except Exception as e:
            return [f"Erro ao listar modelos: {str(e)}"]

    def call_gemini(self, prompt, system_instruction=""):
        """Interface via SDK Oficial com Autodiagnóstico e Execução de Ações"""
        if not self.api_key:
            return "Erro: Chave API não configurada."
        
        try:
            genai.configure(api_key=self.api_key)
            available = self.get_available_models()
            model_to_use = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available else available[0]
            
            model = genai.GenerativeModel(model_to_use)
            
            # Instrução de sistema reforçada para ação
            base_instruction = (
                "Você é o Motor Digital Core, um agente autônomo com acesso ao Windows. "
                "Se o usuário pedir para abrir algo, responda com '[ACTION:OPEN_URL:url]'. "
                "Se o usuário pedir para criar pastas, responda com '[ACTION:CREATE_PROJECT:nome]'. "
                "Seja direto e execute."
            )
            full_system = f"{base_instruction}\n{system_instruction}"
            
            response = model.generate_content(f"{full_system}\n\nUsuário: {prompt}")
            text = response.text
            
            # Lógica de Execução Automática de Ações
            if "[ACTION:OPEN_URL:" in text:
                url = text.split("[ACTION:OPEN_URL:")[1].split("]")[0]
                self.open_browser(url)
                return f"Ação Executada: Abrindo {url}. \n\n{text}"
            
            if "[ACTION:CREATE_PROJECT:" in text:
                name = text.split("[ACTION:CREATE_PROJECT:")[1].split("]")[0]
                self.create_project_structure(name)
                return f"Ação Executada: Projeto {name} criado. \n\n{text}"

            return text
        except Exception as e:
            return f"Falha na conexão neural (SDK): {str(e)}"

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
