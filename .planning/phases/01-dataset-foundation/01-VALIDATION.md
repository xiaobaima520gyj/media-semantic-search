---
phase: 01
slug: dataset-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-15
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Python standard) |
| **Config file** | pytest.ini or pyproject.toml |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | DATA-01 | unit | `pytest tests/test_media_types.py -k test_supported_media_types -x` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | DATA-02 | unit | `pytest tests/test_validation.py -k test_description_length -x` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | DATA-03 | unit | `pytest tests/test_validation.py -k test_tags_categories -x` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 2 | DATA-04 | unit | `pytest tests/test_validation.py -k test_relative_path -x` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 2 | DATA-05 | integration | `pytest tests/test_dataset.py -k test_json_save_load -x` | ❌ W0 | ⬜ pending |
| 01-02-03 | 02 | 2 | DATA-01 | integration | `pytest tests/test_media_types.py -k test_sample_data_media_types -x` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 2 | DATA-04 | unit | `pytest tests/test_validators.py -k test_file_existence -x` | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 2 | DATA-01 | unit | `pytest tests/test_validators.py -k test_format_validation -x` | ❌ W0 | ⬜ pending |
| 01-03-03 | 03 | 2 | DATA-05 | unit | `pytest tests/test_validators.py -k test_json_validation -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_media_types.py` — stubs for DATA-01 (media types)
- [ ] `tests/test_validation.py` — stubs for DATA-02, DATA-03, DATA-04 (validation)
- [ ] `tests/test_dataset.py` — stubs for DATA-05 (JSON save/load)
- [ ] `tests/test_validators.py` — stubs for validation logic
- [ ] `tests/conftest.py` — shared fixtures
- [ ] `pytest` installation (if not present)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| None | - | - | - |

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
