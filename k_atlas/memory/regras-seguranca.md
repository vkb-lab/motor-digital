# Regras de Segurança do K-Atlas Local

1. Nunca sobrescrever agent_core.py diretamente sem backup versionado.
2. Nunca aplicar código gerado por IA contendo markdown dentro de arquivos .py.
3. Toda autoevolução deve gerar arquivo de proposta antes de aplicar.
4. Backups devem ter timestamp.
5. Nunca apagar arquivos automaticamente.
6. Nunca mover arquivos do usuário sem confirmação.
7. Sempre registrar logs.
8. Sempre testar sintaxe Python antes de substituir arquivo principal.
9. Git reset só deve ser usado se houver backup.
10. O painel local deve operar como cockpit, não como executor destrutivo.
