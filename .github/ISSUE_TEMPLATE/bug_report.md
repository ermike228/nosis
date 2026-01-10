---
name: 🐞 Bug Report — NOSIS Enterprise
description: Report a reproducible bug affecting NOSIS (AI Music, Voice, API, Infra, MLOps)
title: "[BUG]: <short description>"
labels: ["bug", "triage", "needs-investigation"]
assignees: []
---

## 1️⃣ Executive Summary
**Describe the bug in one or two sentences.**  
This section is used by leads and on-call engineers to immediately understand severity.

---

## 2️⃣ Business & User Impact
**How does this bug affect users or business?**
- [ ] Revenue impact
- [ ] SLA / SLO violation
- [ ] User trust degradation
- [ ] Data loss or corruption
- [ ] Compliance / legal risk
- [ ] Internal tooling only

**Impact description:**

---

## 3️⃣ Severity Classification
- [ ] SEV-0 — Production down / critical data loss
- [ ] SEV-1 — Major functionality broken
- [ ] SEV-2 — Degraded quality or performance
- [ ] SEV-3 — Minor issue / workaround exists

---

## 4️⃣ Reproduction Instructions (REQUIRED)
Provide **exact steps** so the issue can be reproduced deterministically.

1. Endpoint / Feature:
2. Input (prompt, payload, audio, config):
3. Expected behavior:
4. Actual behavior:

**Reproducibility:**
- [ ] Always
- [ ] Intermittent
- [ ] Rare / edge case

---

## 5️⃣ AI / ML Context (REQUIRED for model issues)
This section enables ML engineers to debug efficiently.

- Model type: [music | voice | hybrid]
- Model name:
- Model version / hash:
- Dataset version:
- Training stage: [pretrain | finetune | inference]
- Inference backend: [PyTorch | ONNX | TensorRT]
- Hardware: [CPU | GPU | multi-GPU]
- Random seed (if applicable):

---

## 6️⃣ Audio & Output Quality Signals (if applicable)
- [ ] Artifacts / noise
- [ ] Vocal instability
- [ ] Incorrect language or pronunciation
- [ ] Musical structure broken
- [ ] Style mismatch
- [ ] Hallucinated content

**Description:**

---

## 7️⃣ Observability & Metrics
Attach or reference monitoring data.

- Logs (link or paste):
- Trace ID:
- Error rate (%):
- Latency p50 / p95 / p99:
- GPU memory usage:
- CPU usage:

---

## 8️⃣ Environment Details
- Environment: [production | staging | local]
- OS:
- Python version:
- Docker image:
- Kubernetes namespace / pod:
- Commit SHA:

---

## 9️⃣ Security & Privacy Check
- [ ] Contains user data
- [ ] Contains licensed audio
- [ ] Potential vulnerability
- [ ] Requires restricted visibility

---

## 🔟 Temporary Mitigations / Workarounds
Describe any mitigation already attempted.

---

## 1️⃣1️⃣ Acceptance Criteria for Fix
Define what "fixed" means.

- [ ] Reproduction no longer occurs
- [ ] Tests added or updated
- [ ] No regression in latency
- [ ] No regression in output quality
- [ ] Metrics back to baseline

---

## 1️⃣2️⃣ Additional Context
Any extra information, links, dashboards, or hypotheses.
