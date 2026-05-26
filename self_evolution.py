import os

class SelfEvolution:
    def __init__(self, core):
        self.core = core

    def analyze_self(self, file_path):
        """Lê um arquivo do próprio sistema e pede melhorias ao Gemini"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        prompt = f"Analise o código abaixo e sugira uma versão melhorada, mais eficiente ou com novas funcionalidades. Retorne APENAS o código Python completo.\n\nCÓDIGO ATUAL:\n{code}"
        
        self.core.log(f"Analisando autoevolução para: {file_path}")
        new_code = self.core.call_gemini(prompt, system_instruction="Você é um Engenheiro de Software Sênior especializado em sistemas autoevolutivos.")
        
        if "import" in new_code: # Verificação simples se retornou código
            backup_path = file_path + ".bak"
            os.rename(file_path, backup_path)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
            self.core.log(f"Evolução aplicada! Backup criado em {backup_path}")
            return True
        return False

    def research_and_expand(self, topic):
        """Pesquisa um novo tópico e cria um novo módulo funcional"""
        prompt = f"Crie um novo módulo Python chamado '{topic}.py' que integre com o Motor Digital Core para realizar a seguinte função: {topic}. Retorne apenas o código."
        new_module_code = self.core.call_gemini(prompt)
        
        file_path = os.path.join(os.path.dirname(__file__), f"{topic}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_module_code)
        self.core.log(f"Novo módulo '{topic}' criado por autoevolução.")
