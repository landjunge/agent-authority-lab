# Real-Case-Transferstudie v1 — Archiv

Fertige, abgeschlossene Batterie. Nichts Neues entwickeln. Nicht „verbessern“, nicht die fünf roten Tests grün machen.

## Zweck

Zehn dokumentierte reale Vorfälle bzw. gegen reale Produkte gezeigte Ketten sind **partiell** in die Fake-API des Labs abgebildet. Getestet wird die Sicherheitssemantik des Monitors, nicht die Originalprodukte.

Extern durchgeführt (OpenAI Codex) gegen Commit `cb2dc55a33672812f8730f28aecb7d42ec4bf927`.

## Was wo liegt

| Datei | Rolle |
|---|---|
| `agent-authority-lab-realcase-tests-v1.zip` | Original-Freeze (9 Dateien) |
| `grok-realcase-einchecken.txt` | Prompt, mit dem der Freeze ins Repo kam |
| [REAL-CASE-TRANSFER-STUDY-v1.md](../../REAL-CASE-TRANSFER-STUDY-v1.md) | Bericht (`report-source.md` aus dem ZIP) |
| [tests/realcase/](../../../tests/realcase/) | Ausgepackter Freeze, lauffähig im Repo |

SHA-256:

```
bbfdf305cccd40ac81919edc8a4bb7477efd9228b95c1c916af700958d7c099b  agent-authority-lab-realcase-tests-v1.zip
d783b8b738ba56a4ecad725bc3bb406bdc3a0092db7e59c401eb74a38f0c79fe  grok-realcase-einchecken.txt
```

`tests/realcase/MANIFEST.sha256` gilt für die fünf Kerndateien im Freeze. Die wurden beim Import nicht geändert.

## Nutzung

Orakel (müssen grün sein):

```bash
.venv/bin/pytest tests/realcase/test_oracles.py --tb=no
```

Sicherheitserwartungen (5 rot ist der Befund):

```bash
.venv/bin/pytest tests/realcase/test_security_expectations.py --tb=no
```

Erwartet: `10 passed` bzw. `5 failed, 5 passed`. RC-01–RC-05 sind gemessene Lücken. Die Default-Suite nimmt sie per Marker `realcase_known_gap` raus (`tests/realcase/conftest.py`).

## Nicht tun

`lab/` ändern, Assertions umdrehen, Manifest neu hashen, I10/Experiment 04 daraus starten.
