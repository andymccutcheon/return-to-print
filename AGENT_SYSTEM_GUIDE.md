# Pennant Agent System Guide

## Overview

The Pennant project uses **4 specialized AI agents**, each with optimized system prompts for their domain. This approach enables parallel development, deep expertise, and clear separation of concerns.

## What Was Created

### Agent System Prompts (in `agents/` directory)

1. **[Frontend Agent](agents/frontend-agent.md)** - React/Next.js/Amplify expert
2. **[Backend Agent](agents/backend-agent.md)** - Python/Lambda/API Gateway expert  
3. **[Infrastructure Agent](agents/infrastructure-agent.md)** - AWS/IaC/DevOps expert
4. **[Hardware Agent](agents/hardware-agent.md)** - Raspberry Pi/embedded systems expert

### Supporting Documentation

5. **[Integration Contracts](agents/integration-contracts.md)** - API specs and coordination protocols
6. **[Agents README](agents/README.md)** - Usage guide and best practices

## Quick Start

### Step 1: Choose Your Agent

| What are you working on? | Which agent? |
|--------------------------|--------------|
| Website UI | **Frontend Agent** |
| API endpoints | **Backend Agent** |
| AWS infrastructure | **Infrastructure Agent** |
| Raspberry Pi setup | **Hardware Agent** |

### Step 2: Load the System Prompt

Open the agent's markdown file in `agents/` and use it as the system prompt for your AI assistant (Claude, GPT-4, etc.).

### Step 3: Provide Context (if needed)

For tasks that cross agent boundaries, also load:
- `agents/integration-contracts.md` - API and data contracts
- Relevant project files from the architecture docs

### Step 4: Work Within Domain

Each agent has:
- ✅ **Deep expertise** in their technical stack
- ✅ **Clear responsibilities** and deliverables
- ✅ **Operating principles** and best practices
- ✅ **Decision autonomy** within their domain
- ✅ **Coordination protocols** for cross-agent work

## Agent Capabilities Summary

### Frontend Agent

**Powers**: Modern web development, UI/UX, AWS Amplify

**Builds**:
- Message submission form with validation
- Recent messages display
- Responsive, accessible web interface
- Amplify CI/CD configuration

**Tech Stack**: React, Next.js, TypeScript, Amplify, CSS

**Output**: Production-ready frontend in `frontend/` directory

---

### Backend Agent

**Powers**: Serverless APIs, database design, Python development

**Builds**:
- REST API with 4 endpoints (create, list, next, mark-printed)
- DynamoDB schema and queries
- Input validation and error handling
- API documentation

**Tech Stack**: Python, Chalice, Lambda, API Gateway, DynamoDB

**Output**: Production-ready API in `backend/` directory

---

### Infrastructure Agent

**Powers**: Cloud architecture, DevOps, security, cost optimization

**Builds**:
- DynamoDB tables with indexes
- IAM roles and policies
- CI/CD pipelines (Amplify + CodePipeline)
- Route 53 DNS configuration
- Monitoring and alarms

**Tech Stack**: CloudFormation, SAM, AWS CLI, Route 53, IAM

**Output**: Infrastructure as Code in `infra/` directory

---

### Hardware Agent

**Powers**: Embedded Linux, hardware integration, reliable systems

**Builds**:
- Python worker script that polls API
- USB printer integration (ESC/POS)
- Systemd service configuration
- Error recovery and retry logic

**Tech Stack**: Python, Raspberry Pi OS, systemd, python-escpos

**Output**: Production-ready worker in `pi-worker/` directory

---

## How Agents Coordinate

### Integration Points

```
┌─────────────┐       ┌─────────────┐
│  Frontend   │──────▶│   Backend   │
│    Agent    │ API   │    Agent    │
└─────────────┘       └─────────────┘
       │                      │
       │                      │
       ▼                      ▼
┌─────────────┐       ┌─────────────┐
│Infrastructure│      │  Hardware   │
│    Agent    │──────▶│    Agent    │
└─────────────┘ URLs  └─────────────┘
       │
       │ Provisions
       ▼
   All AWS Resources
```

### Communication Protocol

1. **Backend Agent** defines API contracts in `integration-contracts.md`
2. **Infrastructure Agent** provisions resources and shares URLs
3. **Frontend Agent** consumes backend API
4. **Hardware Agent** consumes backend API
5. All agents update contracts when making breaking changes

### Coordination Rules

- ✅ **Backend owns API contracts** - others consume
- ✅ **Infrastructure provisions first** - provides URLs to others
- ✅ **Breaking changes require notification** - 24-48 hour notice
- ✅ **Non-breaking changes are autonomous** - no coordination needed
- ✅ **All contracts versioned in Git** - single source of truth

## Example: Complete Feature Flow

### Adding a "Featured Message" Feature

**Requirement**: Highlight one random message on the frontend

**Agent Workflow**:

1. **Backend Agent** (Day 1):
   - Add `GET /messages/featured` endpoint
   - Update `integration-contracts.md` with new endpoint spec
   - Notify Frontend Agent: "New endpoint available"

2. **Infrastructure Agent** (Day 1):
   - No changes needed (existing permissions sufficient)
   - Verify Lambda has required DynamoDB access

3. **Frontend Agent** (Day 2):
   - Add featured message display component
   - Call new `/messages/featured` endpoint
   - Test integration with backend

4. **Hardware Agent** (Day 2):
   - No changes needed (doesn't use featured endpoint)

**Result**: Feature complete in 2 days with clear agent boundaries

## Benefits of This Approach

### For Development

- ✅ **Parallel Work**: Agents work independently, no blocking
- ✅ **Deep Expertise**: Each agent knows their stack deeply
- ✅ **Clear Ownership**: No ambiguity about who owns what
- ✅ **Faster Development**: Specialists are faster in their domain

### For Quality

- ✅ **Best Practices**: Each agent follows domain-specific standards
- ✅ **Consistent Code**: Agents enforce their own style guides
- ✅ **Better Testing**: Agents know what to test in their domain
- ✅ **Security**: Infrastructure Agent enforces security policies

### For Maintenance

- ✅ **Documented Contracts**: Integration points are explicit
- ✅ **Easier Debugging**: Clear boundaries simplify troubleshooting
- ✅ **Scalable**: Can add more agents (e.g., "Monitoring Agent")
- ✅ **Knowledge Transfer**: Prompts serve as documentation

## Getting Started Checklist

### For New Contributors

- [ ] Read `CLAUDE.md` - Project overview
- [ ] Read `all_aws_message_printer_architecture.md` - Technical architecture
- [ ] Read `agents/README.md` - Agent system guide
- [ ] Choose your domain (frontend/backend/infra/hardware)
- [ ] Load appropriate agent prompt
- [ ] Review `agents/integration-contracts.md` for cross-agent work
- [ ] Start building!

### For Project Leads

- [ ] All agents prompts created ✅
- [ ] Integration contracts documented ✅
- [ ] Repository structure defined ✅
- [ ] CI/CD pipelines planned ✅
- [ ] Ready to assign agents to tasks ✅

## Tips for Success

### Do's ✅

- **DO** let each agent work independently in their domain
- **DO** reference integration contracts for cross-agent work
- **DO** update contracts when making breaking changes
- **DO** use the agents README for guidance
- **DO** trust agents to make decisions in their expertise area

### Don'ts ❌

- **DON'T** ask Frontend Agent to configure DynamoDB
- **DON'T** ask Backend Agent to design UI layouts
- **DON'T** skip updating integration contracts
- **DON'T** make breaking changes without notification
- **DON'T** override agent expertise with generic advice

## What's Next?

### Immediate Next Steps

1. **Infrastructure Agent**: Provision AWS resources
   - Create DynamoDB table
   - Set up Route 53 hosted zone
   - Configure Amplify app
   - Set up CodePipeline

2. **Backend Agent**: Implement API
   - Create Chalice application
   - Implement 4 endpoints
   - Add validation and error handling
   - Deploy to AWS

3. **Frontend Agent**: Build web interface
   - Scaffold Next.js app
   - Create message form
   - Create message list
   - Configure Amplify deployment

4. **Hardware Agent**: Set up Raspberry Pi
   - Install dependencies
   - Configure USB printer
   - Create worker script
   - Set up systemd service

### Long-term Roadmap

- **Phase 1**: Core functionality (all agents working)
- **Phase 2**: Monitoring and logging (Infrastructure Agent)
- **Phase 3**: Authentication (Backend + Frontend + Hardware)
- **Phase 4**: Advanced features (rate limiting, moderation, analytics)

## Resources

### Documentation
- **Project Architecture**: `all_aws_message_printer_architecture.md`
- **Project Context**: `CLAUDE.md`
- **Agent Prompts**: `agents/*.md`
- **Integration Contracts**: `agents/integration-contracts.md`

### External Resources
- **AWS Chalice**: https://aws.github.io/chalice/
- **Next.js**: https://nextjs.org/docs
- **AWS Amplify**: https://docs.amplify.aws/
- **python-escpos**: https://python-escpos.readthedocs.io/

## Support

### Questions About Agents
- Review the agent's full system prompt
- Check the agents README for usage guidance
- Reference integration contracts for cross-agent work

### Questions About Architecture
- Review `all_aws_message_printer_architecture.md`
- Check `CLAUDE.md` for project context

### Updating Agent Prompts
- Submit pull requests with clear rationale
- Test changes with AI assistant before committing
- Update integration contracts if needed

---

**You now have 4 specialized agents ready to build Pennant!** 🎉

Each agent is optimized for their domain, has clear responsibilities, and knows how to coordinate with others. Start with any agent based on your current task, and let their expertise guide you to production-ready code.

**Ready to build? Pick an agent and start coding!** 🚀

