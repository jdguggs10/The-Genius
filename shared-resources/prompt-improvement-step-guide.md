# Implementing Prompt‑Engineering Improvements for Your Responses‑API Chatbot
_A step‑by‑step, production‑grade playbook_

---

> **Why this guide?**  
> Your bot already works, but we’re tightening the bolts so it stays _fast_, _cheap_, and _predictable_ as you scale. Follow the checklist in order—each layer builds on the last.

## Table of Contents
1. [Treat Prompts as Code](#1-treat-prompts-as-code)
2. [Slim the System Prompt](#2-slim-the-system-prompt)
3. [Introduce Guardrails & Scratchpad Roles](#3-introduce-guardrails--scratchpad-roles)
4. [Codify Web‑Search Discipline](#4-codify-web-search-discipline)
5. [Calibrate Confidence Scoring](#5-calibrate-confidence-scoring)
6. [Schema‑First Response Validation](#6-schema-first-response-validation)
7. [Automate Date Anchoring](#7-automate-date-anchoring)
8. [Token‑Thrift Techniques](#8-token-thrift-techniques)
9. [Continuous Monitoring & Regression Tests](#9-continuous-monitoring--regression-tests)

---

## 0. Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| **Git** | version control for prompts | `brew install git` |
| **Node 18 +** | backend examples (TypeScript) | `brew install node` |
| **Python 3.11 +** | validation & analytics examples | `brew install python` |
| **jq** | shell JSON manipulation | `brew install jq` |
| **GitHub Actions** | CI runner (free tier works) | none |

Make sure your prompt files live under `prompts/` in your repo.

---

## 1. Treat Prompts as Code

### 1.1 Semantic Versioning for Prompt Files
1. Decide initial version for each file—`1.0.0` if it’s already in prod.  
2. Rename files:  
   ```bash
   git mv prompts/base-instructions.md prompts/base-instructions@1.0.0.md
   ```  
3. When you make a **backwards‑compatible tweak**, bump the **PATCH**: `1.0.1`.  
   Breaking changes ⇒ bump **MINOR**; total rewrites ⇒ bump **MAJOR**.

### 1.2 Pull‑Request Linting
Add `.github/workflows/prompt-lint.yml`:

```yaml
name: Prompt Lint
on: [pull_request]
jobs:
  markdown-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install deps
        run: npm i -g markdownlint-cli
      - name: Lint markdown
        run: markdownlint "prompts/**/*.md"
```

Include checks for:
- No rogue emojis  
- Title ≤ 60 chars  
- Correct version suffix (`@x.y.z.md`)

### 1.3 Snapshot Unit Tests
**Jest (TypeScript)**

```ts
import { readFileSync } from 'fs';
test('base system prompt contains POLICY header', () => {
  const txt = readFileSync('prompts/base-instructions@1.0.0.md', 'utf8');
  expect(txt).toMatch(/## POLICY/);
});
```

Run in CI—fail fast if someone deletes critical lines.

---

## 2. Slim the System Prompt

### Goal
Isolate *immutable* policy from *mutable* workflow instructions.

### Steps
1. Open your existing system prompt. Highlight every sentence starting with “If the user…”.  
2. Cut those lines into a new **assistant** message template injected per request.  
3. Keep only timeless laws (e.g., “Respond in JSON”).  
4. Re‑benchmark token count: aim for < 2 k tokens after pruning.

**Before / After Example**

| Layer | Before | After |
|-------|--------|-------|
| System |  ✅ policy<br>⚠️ when‑to‑search | ✅ policy only |
| Assistant (runtime) | — | “Search unless criteria X fails.” |

---

## 3. Introduce Guardrails & Scratchpad Roles

### 3.1 Guardrails Role
A second **system** message whose entire content is something like:

```
You must emit valid JSON matching schema `response.schema.json`.
Never reveal chain‑of‑thought. If unsure, ask clarifying questions.
```

Place it **after** the main system prompt so policy wins over knowledge.

### 3.2 Assistant Scratchpad
Before calling the LLM tool, inject:

```
<assistant role="tool">
Use internal reasoning here.  
Steps you will take: 1) search 2) analyze 3) answer.  
Return NOTHING to the user from this block.
</assistant>
```

Because the Responses API hides assistant‑role messages by default, the user never sees raw reasoning.

---

## 4. Codify Web‑Search Discipline

### 4.1 Define the Rule
```text
IF (query_is_time_sensitive OR entity_recently_active ≤ 7 days)
THEN search()
ELSE skip_search()
```

### 4.2 Automate with a Function Call
In your request payload:

```jsonc
{
  "tool": "search",
  "policy": "mandatory",
  "inputs": { "recency_days": 7 }
}
```

Now the model *never* spends tokens deciding whether to search—backend handles it.

### 4.3 Edge‑Case Overrides
Expose a user slash‑command `/nosrch` to bypass search for debugging.

---

## 5. Calibrate Confidence Scoring

### 5.1 Log Ground Truth
Store (response, `confidence_score`, outcome) triples in your DB.

### 5.2 Weekly Brier Score Pipeline (Python)

```python
import pandas as pd; from sklearn.metrics import brier_score_loss
df = pd.read_sql('SELECT conf, outcome FROM logs')
print('Brier:', brier_score_loss(df['outcome'], df['conf']))
```

If **Brier > 0.25**, tighten rubric: require stricter language for 0.9 band.

### 5.3 Auto‑tune Phrases
Store confidence→phrase map in a JSON file. Pipeline updates phrases when bands shift.

---

## 6. Schema‑First Response Validation

### 6.1 Generate JSON Schema
```bash
npx quicktype --lang schema   --out schemas/response.schema.json   --src-lang schema prompts/response-format.md
```

### 6.2 Validate Streaming Chunks (Node)

```ts
import Ajv from 'ajv';
const ajv = new Ajv();
const validate = ajv.compile(schema);

for await (const chunk of stream) {
  if (!validate(chunk)) {
     controller.abort(); // retry once
  }
}
```

Return synthetic apology if second attempt fails.

---

## 7. Automate Date Anchoring

### 7.1 Middleware Prepend
TypeScript Express snippet:

```ts
app.post('/chat', async (req, res) => {
  const datedUserMsg =
    `Current Date: ${new Date().toISOString().slice(0,10)}\n\n`
    + req.body.message;
  // …call OpenAI with datedUserMsg
});
```

### 7.2 Regression Test
Snapshot test must assert the prefix exists.

---

## 8. Token‑Thrift Techniques

| Tactic | How‑to |
|--------|--------|
| **Embed static data** | Store park factors table in `vector-db`, reference via ID. |
| **Drop ALL‑CAPS** | Use `###` markdown headings. |
| **Enumerations → IDs** | Replace 500‑token list with “MetricSet: `baseball_core_v1`”. |

Run `scripts/token-estimator.js` weekly to track average per‑turn cost.

---

## 9. Continuous Monitoring & Regression Tests

1. **CI matrix:** lint ➜ unit tests ➜ snapshot tests ➜ end‑to‑end test hitting staging model.  
2. **Dashboards:** track latency, token usage, search frequency, and JSON‑error rate.  
3. **Alerting:** page you if malformed JSON > 1 % over rolling 10 m.

---

## Next Steps

- [ ] Implement Section 1 today—gives the biggest stability win.  
- [ ] Allocate half‑day for Section 6 (schema); it catches 95 % of runtime errors.  
- [ ] Schedule weekly 30‑min prompt‑health review.  

**You’re done!** Your chatbot now operates with the same rigor you apply to production code. Enjoy lower bills and happier users.

