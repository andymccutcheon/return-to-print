# Code Review & QA Agent - Quick Usage Guide

## Purpose

The Code Review & QA Agent is your **production quality gate**. It reviews all code from the four development agents (Frontend, Backend, Infrastructure, Hardware) to ensure production readiness, security, and integration contract compliance.

## When to Use

### ✅ Required Review Points
- Before deploying ANY code to production
- After completing a major feature or component
- Before merging to `main` branch
- After integration work between multiple agents
- When preparing for a release

### 💡 Optional (but Helpful) Review Points
- During development to catch issues early
- When debugging mysterious integration issues
- For performance optimization analysis
- During security audits
- For code quality improvement suggestions

## Quick Start (5-Minute Review)

### Step 1: Gather Context (1 minute)

Collect:
- Which agent's work are you reviewing?
- What files changed?
- What was implemented?
- Any recap/handoff documents?

### Step 2: Load QA Agent (30 seconds)

Open in your AI assistant:
1. `agents/code-review-qa-agent.md` (system prompt)
2. `agents/integration-contracts.md` (reference)

### Step 3: Request Review (30 seconds)

Use this template:

```
Please review [AGENT NAME]'s work on [FEATURE].

Files changed:
- path/to/file1.ext
- path/to/file2.ext
- path/to/file3.ext

Focus areas:
- Integration contract compliance
- Security vulnerabilities
- [Any specific concerns]

Provide a production readiness assessment.
```

### Step 4: Address Issues (varies)

- Fix **critical issues** immediately (blockers)
- Plan **high-priority** for same sprint
- Schedule **medium-priority** for next sprint
- **Nice-to-haves** go in backlog

### Step 5: Get Approval (1 minute)

If QA Agent gives:
- ✅ **APPROVED**: Deploy to production
- ⚠️ **APPROVED with conditions**: Fix issues first, then deploy
- ❌ **NOT APPROVED**: Fix critical issues, then re-review

## Review Workflow by Agent

### Frontend Agent Review

**What QA Agent Checks:**
- TypeScript types match API contracts
- API calls use correct endpoints and methods
- Error handling for network failures
- Loading states during API calls
- Input validation (280 char limit)
- Accessibility (ARIA labels, keyboard nav)
- No secrets in code (API keys, etc.)

**Files to Provide:**
```
frontend/src/
├── app/          # Pages
├── components/   # React components
├── lib/api.ts    # API client
└── types/        # TypeScript types
```

**Example Request:**
```
Review Frontend Agent's message submission form.

Files:
- frontend/src/components/MessageForm.tsx
- frontend/src/lib/api.ts
- frontend/src/types/message.ts

Check:
- API integration matches contracts
- Input validation
- Error handling
- TypeScript type safety
```

---

### Backend Agent Review

**What QA Agent Checks:**
- All endpoints match integration contracts exactly
- Request/response schemas correct
- Input validation on ALL endpoints
- HTTP status codes correct (201 for POST, etc.)
- CORS enabled
- Error handling and logging
- DynamoDB operations efficient
- No secrets hardcoded

**Files to Provide:**
```
backend/return_to_print_api/
├── app.py         # Route handlers
├── chalicelib/
│   ├── db.py      # DynamoDB operations
│   ├── validators.py
│   └── models.py
└── requirements.txt
```

**Example Request:**
```
Review Backend Agent's API implementation.

Files:
- backend/return_to_print_api/app.py
- backend/return_to_print_api/chalicelib/db.py
- backend/return_to_print_api/chalicelib/validators.py

Focus:
- POST /message endpoint validation
- DynamoDB query efficiency
- Integration contract compliance
- Security (input validation, secrets)
```

---

### Infrastructure Agent Review

**What QA Agent Checks:**
- DynamoDB table schema matches requirements
- GSI configured correctly (printed + created_at)
- IAM policies follow least privilege
- No wildcards in Resource ARNs (except logs)
- Monitoring and alarms configured
- Tags present for cost tracking
- CORS enabled on API Gateway
- HTTPS enforced everywhere

**Files to Provide:**
```
infra/
├── template.yaml        # CloudFormation/SAM
├── policies/
│   ├── lambda-role.json
│   └── codebuild-role.json
└── amplify-config.yaml
```

**Example Request:**
```
Review Infrastructure Agent's AWS setup.

Resources provisioned:
- DynamoDB table: return-to-print-messages-prod
- Lambda execution role
- API Gateway
- Amplify app

Files:
- infra/template.yaml
- infra/policies/lambda-execution-policy.json

Check:
- IAM least privilege
- DynamoDB schema correctness
- Security configuration
```

---

### Hardware Agent Review

**What QA Agent Checks:**
- Correct API endpoints used (next-to-print, mark-printed)
- Handles all error cases (network, printer, API)
- Polling loop never crashes
- Proper sleep between polls
- Idempotency handling
- Systemd service configured for auto-restart
- USB permissions correct
- Logging comprehensive

**Files to Provide:**
```
pi-worker/
├── worker.py
├── test_printer.py
├── return-to-print-worker.service
└── requirements.txt
```

**Example Request:**
```
Review Hardware Agent's printer worker.

Files:
- pi-worker/worker.py
- pi-worker/return-to-print-worker.service

Check:
- API integration (next-to-print, mark-printed)
- Error handling and recovery
- Reliability (never crashes)
- Systemd configuration
```

---

## Cross-Agent Integration Review

### Full System Review

When multiple agents have completed work and you want to verify end-to-end integration:

```
Review integration between Frontend, Backend, and Hardware agents.

Context:
- Frontend submits messages via POST /message
- Backend stores in DynamoDB
- Hardware polls via GET /printer/next-to-print and marks printed

Files:
- frontend/src/lib/api.ts
- backend/return_to_print_api/app.py
- pi-worker/worker.py
- agents/integration-contracts.md

Check:
- All agents honor API contracts
- Data schemas consistent
- Error handling across boundaries
- Environment variables shared correctly
```

The QA Agent will verify:
- Frontend calls match Backend implementation
- Backend responses match Frontend expectations
- Hardware consumes correct endpoints
- Data types consistent everywhere
- Error formats propagate correctly

---

## Understanding QA Agent Reports

### Report Structure

```
## Code Review Report: [Agent Name]

### 🎯 Executive Summary
[2-3 sentences: overall assessment]

### 🚨 Critical Issues (MUST FIX)
[Blockers - cannot deploy without fixing these]

### ⚠️ High Priority Issues
[Should fix soon - not blockers but important]

### 💡 Medium Priority Issues
[Improve quality - fix in next sprint]

### ✨ Nice-to-Haves
[Optional improvements - backlog]

### ✅ Strengths
[What the code does well]

### 📋 Integration Contract Compliance
[Checklist of contract adherence]

### 🔒 Security Assessment
[Security checklist]

### ⚡ Performance Assessment
[Performance evaluation]

### 📊 Production Readiness Score: X/10

### 🚀 Recommendation
[APPROVED / APPROVED with conditions / NOT APPROVED]
```

### Issue Priority Levels

**🚨 Critical Issues**
- **Cannot deploy to production until fixed**
- Examples:
  - Security vulnerabilities (exposed secrets, XSS, injection)
  - Contract violations (wrong API response format)
  - Data integrity issues (no validation)
  - Crashes or fatal errors

**⚠️ High Priority**
- **Should fix before production, but not blockers**
- Examples:
  - Incomplete error handling
  - Performance bottlenecks
  - Missing logging
  - Code quality issues that affect maintainability

**💡 Medium Priority**
- **Fix in next sprint or iteration**
- Examples:
  - Code duplication (DRY violations)
  - Missing type hints
  - Suboptimal patterns
  - Documentation gaps

**✨ Nice-to-Haves**
- **Optional improvements for backlog**
- Examples:
  - More comprehensive tests
  - Performance micro-optimizations
  - Better variable names
  - Additional features

### Production Readiness Scores

- **9-10**: Excellent - Deploy immediately
- **7-8**: Good - Minor fixes recommended, can deploy
- **5-6**: Fair - High-priority issues should be fixed first
- **3-4**: Poor - Multiple critical issues, do not deploy
- **1-2**: Bad - Major rework needed

### Recommendations

**✅ APPROVED for production**
- No critical issues
- High-priority issues are acceptable trade-offs
- Deploy with confidence

**⚠️ APPROVED with conditions**
- Fix high-priority issues first
- Can deploy after addressing conditions
- Re-review recommended but not required

**❌ NOT APPROVED**
- Critical issues present
- Do not deploy
- Fix issues and request re-review

---

## Advanced Usage

### Focused Reviews

You can ask QA Agent to focus on specific areas:

**Security-Only Review:**
```
Review [AGENT]'s code for security vulnerabilities only.

Focus on:
- Input validation
- Secrets exposure
- Injection vulnerabilities
- XSS risks
- IAM permissions
```

**Performance-Only Review:**
```
Review [AGENT]'s code for performance issues only.

Focus on:
- Database query efficiency
- API response times
- Bundle size (frontend)
- Memory usage
- Unnecessary operations
```

**Contract Compliance Only:**
```
Review [AGENT]'s implementation against integration contracts.

Verify:
- API endpoints match exactly
- Data schemas consistent
- Error formats correct
- Environment variables used properly
```

### Re-Review After Fixes

After fixing critical issues:

```
Re-review [AGENT]'s code. I fixed the following issues:

Fixed:
- Issue #1: [description of fix]
- Issue #2: [description of fix]

Files changed:
- [list of files]

Please verify fixes and update production readiness assessment.
```

### Comparative Review

Compare implementations across agents:

```
Compare how Frontend and Hardware agents both consume the Backend API.

Check:
- Do both parse responses correctly?
- Do both handle errors the same way?
- Are there inconsistencies in API usage?
- Can we standardize patterns?
```

---

## Best Practices

### Do's ✅

- **DO** use QA Agent before every production deployment
- **DO** provide full context (files, what changed, why)
- **DO** fix critical issues immediately
- **DO** re-review after major fixes
- **DO** keep integration contracts updated
- **DO** address security issues first, then functionality

### Don'ts ❌

- **DON'T** skip QA review to "save time" (false economy)
- **DON'T** ignore critical issues ("we'll fix it later")
- **DON'T** provide only partial code (QA needs full context)
- **DON'T** argue with security findings (fix them)
- **DON'T** deploy if recommendation is "NOT APPROVED"
- **DON'T** review without integration contracts loaded

---

## Troubleshooting

### "QA Agent is too strict"

**Remember**: QA Agent's job is to protect production. If something is flagged as critical:
- It's likely a real issue
- Ask QA Agent to explain the risk
- If you disagree, ask for clarification with specific reasoning

### "QA Agent found too many issues"

**This is good!** Better to find issues before production than after. Strategy:
1. Fix all critical issues
2. Group high-priority issues by similarity
3. Fix in batches
4. Re-review after each batch

### "QA Agent didn't catch an issue"

QA Agent is thorough but not perfect. If you find an issue QA missed:
1. Fix the issue
2. Document what was missed
3. Consider updating QA Agent prompt with new checklist item

### "QA Review takes too long"

Make reviews faster:
- Review smaller changesets (don't wait for everything)
- Provide focused requests ("review security only")
- Keep integration contracts current (less context needed)
- Run QA during development (catch issues early)

---

## Summary

**The QA Agent is your safety net.** It ensures:
- ✅ Code meets production quality standards
- ✅ Security vulnerabilities are caught
- ✅ Integration contracts are honored
- ✅ Performance is acceptable
- ✅ All agents work together correctly

**Use it religiously before deploying to production.**

**Time invested in QA reviews pays off 10x in production stability.**

---

## Quick Reference

### Minimal Review Request
```
Review [AGENT] work on [FEATURE].
Files: [list]
Check contracts, security, integration.
```

### Comprehensive Review Request
```
Review [AGENT] work on [FEATURE].

Context:
[What was built and why]

Files:
[List all changed files]

Focus areas:
- Integration contract compliance
- Security
- Performance
- Error handling
- [Other concerns]

Provide full production readiness assessment.
```

### Re-Review Request
```
Re-review [AGENT] work.

Previously found issues (now fixed):
- [Issue 1 + how fixed]
- [Issue 2 + how fixed]

Files changed:
[List]

Update production readiness score.
```

---

**Your code is only as good as your reviews. Use the QA Agent.** 🛡️

