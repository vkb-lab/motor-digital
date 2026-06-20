# K-OS Hupmix Real Publish Executor v0.69H

Objetivo:
Instalar o executor real Hupmix-only para publicacao Instagram via Meta Graph API.

O instalador nao publica.

Publicacao real exige:
- target hupmix
- approval ledger 69G pronto
- URL publica HTTPS da imagem
- caption valida
- token Meta local
- flag KOS_REAL_HUPMIX_PUBLISH_ENABLED=true
- parametro --execute-real-publish
- frase final YES_EXECUTE_REAL_HUPMIX_INSTAGRAM_PUBLISH_NOW

Parada Atlantida continua bloqueada.

Exemplo de dry-run:
python scripts\run_phase69h_hupmix_real_publish_executor.py --target hupmix --campaign-id "teste" --caption "caption" --image-url "https://example.com/image.jpg"

Exemplo real, somente quando o operador decidir:
$env:KOS_REAL_HUPMIX_PUBLISH_ENABLED="true"
python scripts\run_phase69h_hupmix_real_publish_executor.py --target hupmix --campaign-id "teste-real" --caption "caption" --image-url "https://URL_PUBLICA/imagem.jpg" --operator "operator" --confirmation "YES_EXECUTE_REAL_HUPMIX_INSTAGRAM_PUBLISH_NOW" --execute-real-publish
