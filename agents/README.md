# Pennant Agent System Prompts

This directory contains specialized system prompts for the agents working on the Pennant project. Each agent has distinct expertise, responsibilities, and operating principles optimized for their domain.

## Quick Start

### Using These Prompts

1. **Choose the appropriate agent** for your task based on the domain
2. **Load the agent's system prompt** into your AI assistant context
3. **Provide the integration contracts** as additional context if cross-agent coordination is needed
4. **Work within the agent's domain** - each agent has clear boundaries and autonomy

### Agent Selection Guide

| Task | Agent to Use |
|------|--------------|
| Building React/Next.js UI | [Frontend Agent](#frontend-agent) |
| Creating API endpoints | [Backend Agent](#backend-agent) |
| Setting up AWS resources | [Infrastructure Agent](#infrastructure-agent) |
| Configuring Raspberry Pi worker | [Hardware Agent](#hardware-agent) |
| **Reviewing all code for production** | [**Code Review & QA Agent**](#code-review--qa-agent) |

---

## Agent Overview

### Frontend Agent
**File**: [`frontend-agent.md`](./frontend-agent.md)

**Expertise**: React, Next.js, AWS Amplify, modern web development

**Responsibilities**:
- Building the message submission interface
- Displaying recent messages
- Amplify hosting and CI/CD configuration
- Responsive design and accessibility
- API integration with backend

**Key Technologies**: React, Next.js, TypeScript, AWS Amplify, CSS

**Autonomy Level**: High for UI/UX decisions, coordinates on API contracts

**Use When**: Building or modifying the web frontend

---

### Backend Agent
**File**: [`backend-agent.md`](./backend-agent.md)

**Expertise**: Python, AWS Lambda, API Gateway, DynamoDB, Chalice

**Responsibilities**:
- Defining and implementing REST API endpoints
- Database schema design and queries
- Message queue logic
- Input validation and error handling
- API documentation

**Key Technologies**: Python, Chalice, Lambda, API Gateway, DynamoDB

**Autonomy Level**: High for implementation, owns API contracts

**Use When**: Creating APIs, database operations, or backend logic

---

### Infrastructure Agent
**File**: [`infrastructure-agent.md`](./infrastructure-agent.md)

**Expertise**: AWS services, Infrastructure as Code, CI/CD, DevOps

**Responsibilities**:
- Provisioning all AWS resources
- Route 53 DNS configuration
- CI/CD pipeline setup (Amplify, CodePipeline)
- IAM roles and security policies
- Monitoring and cost optimization

**Key Technologies**: CloudFormation, SAM, Amplify, CodePipeline, Route 53, IAM

**Autonomy Level**: High for infrastructure decisions, ensures security compliance

**Use When**: Setting up AWS infrastructure, deployment pipelines, or DNS

---

### Hardware Agent
**File**: [`hardware-agent.md`](./hardware-agent.md)

**Expertise**: Raspberry Pi, embedded Linux, USB devices, system services

**Responsibilities**:
- Raspberry Pi worker script development
- USB printer integration (python-escpos)
- Systemd service configuration
- Reliable polling and error recovery
- Hardware troubleshooting

**Key Technologies**: Python, Raspberry Pi, systemd, USB/ESC-POS, Linux

**Autonomy Level**: High for Pi implementation, respects API contracts

**Use When**: Working on the Raspberry Pi printer worker

---

### Code Review & QA Agent
**File**: [`code-review-qa-agent.md`](./code-review-qa-agent.md)

**Expertise**: Full-stack review, security auditing, performance optimization, all domains

**Responsibilities**:
- Reviewing code from all agents for production readiness
- Verifying integration contract compliance
- Security vulnerability assessment
- Performance bottleneck identification
- Cross-domain integration verification
- Testing coverage assessment

**Key Technologies**: All stacks (React, Python, AWS, Linux, DynamoDB)

**Autonomy Level**: High authority to approve/reject code for production

**Use When**: Before deploying any code to production, after major features complete, or when debugging integration issues

**Special Role**: This agent reviews OUTPUT from other agents, not implements features itself

---

## Integration Contracts

**File**: [`integration-contracts.md`](./integration-contracts.md)

This critical document defines:
- **API Endpoints**: Complete specification with request/response schemas
- **Data Schemas**: Canonical data structures used across agents
- **Environment Variables**: Configuration shared between agents
- **Integration Flows**: Sequence diagrams showing how agents interact
- **Change Management**: Protocol for coordinating breaking changes

**When to Reference**:
- Starting work that touches multiple agents
- Making API contract changes
- Setting up environment variables
- Understanding data flow through the system

---

## Coordination Protocols

### When Agents Must Coordinate

#### Frontend ↔ Backend
- **API Contract Changes**: Backend must notify Frontend before changing endpoints
- **New Features**: Frontend requests new endpoints from Backend
- **Error Handling**: Agree on error code meanings

#### Backend ↔ Infrastructure
- **Resource Needs**: Backend requests DynamoDB tables, IAM permissions
- **Environment Variables**: Backend defines needs, Infrastructure provisions
- **Deployment**: Infrastructure manages deployment pipeline

#### Backend ↔ Hardware
- **API Stability**: Backend must keep printer endpoints stable
- **Error Handling**: Backend provides clear error responses for printer worker
- **New Features**: Hardware requests new printer-specific endpoints if needed

#### Infrastructure ↔ All Agents
- **URLs & Endpoints**: Infrastructure provides deployed URLs to all agents
- **Credentials**: Infrastructure manages API keys, secrets
- **Deployment**: Infrastructure owns all CI/CD pipelines

### Change Request Process

1. **Proposing Agent** identifies need for coordination
2. **Document the change** with impact analysis
3. **Notify affected agents** with timeline
4. **Wait for confirmation** from dependent agents
5. **Update integration-contracts.md** if API/data changes
6. **Implement in order**: Infrastructure → Backend → Frontend/Hardware
7. **Verify integration** after deployment

---

## Using the Code Review & QA Agent

### When to Use QA Agent

**✅ Use QA Agent when:**
- Any agent completes a major feature or component
- Before merging code to main branch
- Before deploying to production
- After integration across multiple agents
- When debugging mysterious issues
- During security assessments
- For performance optimization reviews

**Typical workflow:**
1. Development agent (Frontend/Backend/Infrastructure/Hardware) completes work
2. Developer saves work and creates recap/handoff document
3. Load QA Agent with the recap document and code files
4. QA Agent reviews against checklists and integration contracts
5. QA Agent provides prioritized issue report
6. Developer fixes critical and high-priority issues
7. QA Agent re-reviews until approved for production

### How to Use QA Agent

**Step 1: Load the QA Agent**
- Open `agents/code-review-qa-agent.md` as system prompt
- Also provide `agents/integration-contracts.md` as reference

**Step 2: Provide Context**
Give the QA Agent:
- Which agent's work you're reviewing (Frontend/Backend/Infrastructure/Hardware)
- List of files that changed
- What features were implemented
- Any recap/handoff documents

**Step 3: Request Review**
Example prompt:
> "Please review the Backend Agent's work. They implemented the 4 API endpoints for Return-to-Print.
> 
> Files to review:
> - backend/return_to_print_api/app.py
> - backend/return_to_print_api/chalicelib/db.py
> - backend/return_to_print_api/chalicelib/validators.py
> 
> Focus on:
> - Integration contract compliance
> - Security vulnerabilities
> - Error handling
> 
> Provide a full production readiness assessment."

**Step 4: Address Issues**
- Fix critical issues immediately (blockers)
- Plan high-priority issues for same sprint
- Schedule medium-priority issues for next sprint
- Nice-to-haves go in backlog

**Step 5: Re-Review (if needed)**
If critical issues were found, have QA Agent re-review after fixes.

### QA Agent Review Checklist

The QA Agent will systematically check:

**For All Code:**
- ✅ Integration contract compliance
- ✅ Security vulnerabilities (XSS, injection, secrets exposure)
- ✅ Error handling completeness
- ✅ Performance bottlenecks
- ✅ Code quality and maintainability
- ✅ Documentation and logging
- ✅ Testing coverage

**Domain-Specific:**
- **Frontend**: TypeScript types, API integration, accessibility
- **Backend**: Input validation, DynamoDB efficiency, CORS
- **Infrastructure**: IAM permissions, monitoring, cost optimization
- **Hardware**: Reliability, error recovery, systemd configuration

**Cross-Domain:**
- API contracts honored by both producer and consumer
- Data schemas consistent across all layers
- Environment variables correctly shared
- Error formats consistent

### Sample QA Agent Output

```
## Code Review Report: Backend Agent

### 🎯 Executive Summary
Backend API implementation is 80% production-ready. Core functionality works well, but 
has 2 critical security issues and 1 integration contract violation that must be fixed.

### 🚨 Critical Issues (MUST FIX)
1. **No input validation on POST /message**
   - File: app.py:45
   - Problem: Accepts empty content, over 280 chars
   - Risk: Data integrity, DynamoDB waste
   - Fix: Add validation as shown in integration contracts

2. **Wrong HTTP status code**
   - File: app.py:52  
   - Problem: Returns 200 instead of 201 for POST
   - Risk: Contract violation, frontend expects 201
   - Fix: Return Response(..., status_code=201)

### ✅ Strengths
- Clean code structure with proper separation
- Comprehensive logging
- Good error handling for DynamoDB failures

### 📊 Production Readiness: 6/10
### 🚀 Recommendation: ⚠️ APPROVED with conditions (fix critical issues)
```

---

## Best Practices

### For Agent Users

1. **Read the Full Prompt**: Each agent prompt contains critical context and principles
2. **Stay in Domain**: Don't ask Frontend Agent to configure DynamoDB
3. **Reference Contracts**: Use integration-contracts.md when working across boundaries
4. **Document Decisions**: Explain non-obvious choices in code comments
5. **Test Integrations**: Verify endpoints work after changes

### For Agent Developers

1. **Update Prompts**: Keep agent prompts current as the project evolves
2. **Maintain Contracts**: Update integration-contracts.md for all breaking changes
3. **Version Control**: Track changes to prompts in Git
4. **Clear Boundaries**: Keep agent responsibilities distinct and non-overlapping
5. **Communication**: Agents should proactively notify each other of changes

---

## Example Workflows

### Workflow 1: Adding a New Feature

**Scenario**: Add a "delete message" feature

**Steps**:
1. **Backend Agent**: Design DELETE /message/:id endpoint, update contracts
2. **Infrastructure Agent**: Verify IAM permissions allow DynamoDB DeleteItem
3. **Frontend Agent**: Add delete button UI and API integration
4. **Hardware Agent**: No changes needed (doesn't create/delete messages)

**Coordination**: Backend → Frontend coordination needed. Infrastructure and Hardware not affected.

---

### Workflow 2: Changing API URL

**Scenario**: Moving from API Gateway to custom domain (api.pennant.com)

**Steps**:
1. **Infrastructure Agent**: Provision custom domain, update Route 53, update API Gateway
2. **Infrastructure Agent**: Notify all agents of new URL and cutover date
3. **Backend Agent**: Update documentation with new base URL
4. **Frontend Agent**: Update NEXT_PUBLIC_API_BASE_URL environment variable
5. **Hardware Agent**: Update API_BASE constant in worker.py
6. **Infrastructure Agent**: Execute cutover, keep old URL active briefly

**Coordination**: Infrastructure → All agents. Breaking change requires synchronized updates.

---

### Workflow 3: Debugging Production Issue

**Scenario**: Messages not printing on Raspberry Pi

**Investigation by Agent**:
1. **Hardware Agent**: Check Pi worker logs, printer connection, network
2. **Backend Agent**: Verify /printer/next-to-print returning messages
3. **Infrastructure Agent**: Check API Gateway logs, DynamoDB metrics, network
4. **Frontend Agent**: Verify messages are being created successfully

**Coordination**: Hardware Agent leads investigation, requests diagnostics from others as needed.

---

## Updating These Prompts

### When to Update

- **Feature Addition**: New capabilities or responsibilities for an agent
- **Technology Changes**: Migrating to new framework or service
- **Best Practices**: New patterns or standards emerge
- **Lessons Learned**: Production issues reveal gaps in prompts

### How to Update

1. **Identify the Issue**: What's missing or incorrect?
2. **Determine Scope**: Which agents are affected?
3. **Draft Changes**: Update relevant prompt files
4. **Update Contracts**: If integration points change, update integration-contracts.md
5. **Test with AI**: Load updated prompt and verify behavior
6. **Document in Git**: Commit with clear message explaining change

### Version Control

All agent prompts are version controlled in Git. Use semantic commits:

```
feat(agents): add authentication guidance for backend agent
fix(agents): clarify hardware agent USB permissions setup
docs(agents): update integration contracts with new endpoint
```

---

## Getting Help

### Prompt Issues

If an agent prompt is unclear, missing information, or encouraging bad practices:
1. Document the issue with specific examples
2. Propose an improvement
3. Test the improved prompt
4. Submit as a pull request

### Integration Issues

If agents aren't coordinating properly:
1. Review integration-contracts.md
2. Check if contracts are out of date
3. Update contracts to clarify expectations
4. Ensure all agents have access to current contracts

---

## File Structure

```
agents/
├── README.md                      # This file - guide to using agent prompts
├── frontend-agent.md              # Frontend Development Agent system prompt
├── backend-agent.md               # Backend/API Development Agent system prompt
├── infrastructure-agent.md        # Infrastructure/DevOps Agent system prompt
├── hardware-agent.md              # Hardware/Embedded Systems Agent system prompt
└── integration-contracts.md       # API contracts and integration protocols
```

---

## Summary

These agent prompts enable **specialized, autonomous development** while maintaining **clear integration points**. Each agent is an expert in their domain, makes confident decisions within their scope, and coordinates with other agents at well-defined boundaries.

**Key Principles**:
- ✅ **Clear Boundaries**: Each agent owns a distinct technical domain
- ✅ **High Autonomy**: Agents make decisions independently within their domain
- ✅ **Explicit Contracts**: Integration points are documented and versioned
- ✅ **Coordinated Changes**: Breaking changes follow a clear notification process
- ✅ **Quality Standards**: Each agent has specific code quality expectations

Start by reading the prompt for your domain, reference the integration contracts when needed, and communicate proactively when crossing agent boundaries.

**Happy building! 🚀**

