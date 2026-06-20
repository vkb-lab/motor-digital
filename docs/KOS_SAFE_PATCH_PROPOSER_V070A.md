# K-OS Safe Patch Proposer v0.70A

Objetivo:
Permitir que o K-OS analise arquivos e proponha patches sem aplicar automaticamente.

Regras:
- Nao altera arquivos alvo.
- Nao aplica patch.
- Nao executa comandos.
- Nao acessa secrets.
- Nao publica.
- Nao usa IA paga.
- Toda proposta exige revisao humana.
- Aplicacao real deve ficar para uma fase futura com gate proprio.

Comando:
python scripts\run_phase70a_safe_patch_proposer.py --objective "melhorar clareza do launcher" --files README.md pages/KOS_User_Launcher.py

Saidas:
- local_runtime/kos_safe_patch_proposals/latest_safe_patch_proposal.json
- local_runtime/kos_safe_patch_proposals/diffs/*.diff
