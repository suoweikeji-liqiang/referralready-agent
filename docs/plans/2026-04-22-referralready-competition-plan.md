# ReferralReady Competition Readiness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an internal multi-judge scorecard, expand synthetic referral scenarios, and strengthen tests so ReferralReady can be assessed against the Agents Assemble rubric with higher confidence.

**Architecture:** The plan adds a deterministic scoring module that reads a small, curated set of repository artifacts and evaluates them with multiple judge personas plus a Stage 1 readiness gate. In parallel, the plan expands synthetic patients to create complete and incomplete examples per specialty, then hardens validation and tests around those fixtures.

**Tech Stack:** Python, pytest, JSON fixture data, Markdown project artifacts

---

### Task 1: Add failing tests for competition scorecard behavior

**Files:**
- Create: `tests/test_scorecard.py`
- Modify: `tests/test_referralready.py`

**Step 1: Write the failing test**

Add tests for:

- Stage 1 readiness identifies missing Marketplace publication evidence
- multi-judge scoring returns several judge results and an averaged summary
- score spread is reported when judges differ
- recommended next actions include Stage 1 blockers first

**Step 2: Run test to verify it fails**

Run: `pytest -q tests/test_scorecard.py`
Expected: FAIL because the scorecard module does not exist yet

**Step 3: Write minimal implementation**

Create a scorecard module with:

- artifact loading and bounded context selection
- Stage 1 readiness evaluation
- deterministic judge profiles
- average and spread aggregation

**Step 4: Run test to verify it passes**

Run: `pytest -q tests/test_scorecard.py`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_scorecard.py app/scorecard.py scripts/score_submission.py
git commit -m "feat: add internal competition scorecard"
```

### Task 2: Add failing tests for expanded synthetic scenarios

**Files:**
- Modify: `tests/test_referralready.py`
- Create: `data/synthetic_fhir/SYN-CKD-004.json`
- Create: `data/synthetic_fhir/SYN-HF-005.json`
- Create: `data/synthetic_fhir/SYN-DM-006.json`

**Step 1: Write the failing test**

Add tests for:

- a complete nephrology case yields no missing checklist items
- a complete cardiology or endocrinology case can produce a packet with no missing-information section gaps
- patient listing reflects the new fixtures

**Step 2: Run test to verify it fails**

Run: `pytest -q tests/test_referralready.py -k "complete or list_patient_ids"`
Expected: FAIL because the synthetic patients do not exist yet

**Step 3: Write minimal implementation**

Add the new patient fixtures with the exact fields needed to satisfy the relevant checklist items.

**Step 4: Run test to verify it passes**

Run: `pytest -q tests/test_referralready.py -k "complete or list_patient_ids"`
Expected: PASS

**Step 5: Commit**

```bash
git add data/synthetic_fhir/*.json tests/test_referralready.py
git commit -m "feat: expand synthetic referral scenarios"
```

### Task 3: Add failing tests for validation and edge conditions

**Files:**
- Modify: `tests/test_referralready.py`
- Modify: `app/data_store.py`
- Modify: `app/safety.py`

**Step 1: Write the failing test**

Add tests for:

- specialty aliases normalize as expected
- unknown patient and unknown specialty raise `DataNotFoundError`
- malformed patient records are rejected
- a complete case yields the "route to specialist team" coordination task

**Step 2: Run test to verify it fails**

Run: `pytest -q tests/test_referralready.py -k "alias or unknown or malformed or route"`
Expected: FAIL because validation is too weak or behavior is not implemented yet

**Step 3: Write minimal implementation**

Tighten validation and keep behavior deterministic without introducing full-schema complexity.

**Step 4: Run test to verify it passes**

Run: `pytest -q tests/test_referralready.py -k "alias or unknown or malformed or route"`
Expected: PASS

**Step 5: Commit**

```bash
git add app/data_store.py app/safety.py tests/test_referralready.py
git commit -m "test: harden validation and edge-case coverage"
```

### Task 4: Add a local scorecard runner and verify end-to-end output

**Files:**
- Create: `scripts/score_submission.py`
- Modify: `README.md`
- Modify: `docs/marketplace_setup.md`

**Step 1: Write the failing test**

Add or extend tests to verify the scorecard runner returns a readable report structure.

**Step 2: Run test to verify it fails**

Run: `pytest -q tests/test_scorecard.py -k "report"`
Expected: FAIL because the runner or formatter is missing

**Step 3: Write minimal implementation**

Add a simple CLI script that prints:

- Stage 1 readiness
- averaged criterion scores
- per-judge outputs
- top submission blockers

Update docs so contributors know how to use it.

**Step 4: Run test to verify it passes**

Run: `pytest -q tests/test_scorecard.py`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/score_submission.py README.md docs/marketplace_setup.md tests/test_scorecard.py
git commit -m "docs: add scorecard workflow"
```

### Task 5: Full verification

**Files:**
- Verify only

**Step 1: Run focused tests**

Run: `pytest -q tests/test_scorecard.py tests/test_referralready.py`
Expected: PASS

**Step 2: Run full test suite**

Run: `pytest -q`
Expected: PASS

**Step 3: Run demo and scorecard scripts**

Run:

- `python scripts/run_local_demo.py --patient SYN-CKD-001 --specialty nephrology`
- `python scripts/score_submission.py`

Expected:

- demo prints a valid referral packet
- scorecard prints Stage 1 readiness plus averaged judge scores

**Step 4: Review competition blockers**

Manually confirm the scorecard still reports any real Stage 1 gaps, especially Marketplace publication and platform discoverability.

**Step 5: Commit**

```bash
git add .
git commit -m "chore: improve competition readiness"
```
