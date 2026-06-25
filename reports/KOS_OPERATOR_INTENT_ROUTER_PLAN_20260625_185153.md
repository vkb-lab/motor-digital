# K-OS Operator Intent Router Plan

Timestamp: 20260625_185153

## Purpose

Create a local, deterministic intent router that classifies operator requests into known K-OS work surfaces without executing actions.

## Files Created

- `scripts/kos_operator_intent_router.py`
- `tests/test_kos_operator_intent_router.py`

## Guardrails

- Classification only.
- No command execution.
- No API access.
- No secret access.
- No browser or runtime access.

## Validation

Run:

```powershell
python -m pytest tests/test_kos_operator_intent_router.py -q
```

