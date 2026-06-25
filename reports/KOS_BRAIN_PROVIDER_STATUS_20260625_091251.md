# KOS BRAIN PROVIDER STATUS

Generated: 2026-06-25T09:12:51.652797

## Decision

Selected provider: kos_internal_evolutionary
Reason: first active provider in free-first priority order
Paid provider used: False

## Priority order
- kos_internal_evolutionary
- ollama_local
- lmstudio_local
- localai_or_vllm
- gemini_free_guarded
- external_paid_locked

## Providers

### kos_internal_evolutionary

Active: True
Cost: zero

### ollama_local

Active: False
Cost: zero_after_installation
API reachable: True
Models count: 0
Models:

### lmstudio_local

Active: False
Cost: n/a
Reason: KOS_LMSTUDIO_BASE_URL not configured

### localai_or_vllm

Active: False
Cost: n/a
Reason: KOS_LOCAL_OPENAI_BASE_URL not configured

### gemini_free_guarded

Active: False
Cost: free_tier_first
API key present: True
Enabled flag: False
Daily request budget: 25
Daily token budget: 100000

### external_paid_locked

Active: False
Cost: n/a
Reason: blocked by default; requires vault, budget and Human Gate

## CTO readout

- K-OS must always consult internal intelligence first.
- Local free AI comes before cloud tokens.
- Gemini free guarded comes before paid providers.
- Paid/external providers remain locked by default.
