# Cortex Capability Mapping Report

**Analysis Date:** 2026-02-25
**Total Agents Analyzed:** 99
**Total Cortex Agents Available:** 1,324

---

## Executive Summary

Successfully mapped all 99 Lilly Service Management AI Agents to specific Cortex capabilities, toolkits, and existing agents. Each agent now has concrete implementation recommendations based on:

- **Cortex Toolkits** (5 available)
- **Existing Cortex Agents** (1,324 shared agents)
- **AI Models** (111 inference, 13 embedding)
- **Integration Platforms** (ServiceNow, JIRA, Workday)

---

## Mapping Statistics

| Capability | Agent Count | Percentage |
|-----------|-------------|------------|
| **CORTEX SNOW TOOLKIT** | 51 | 51.5% |
| **EXISTING CORTEX AGENTS** (Specific Matches) | 50 | 50.5% |
| **TEA AUTOMATION + CORTEX** | 26 | 26.3% |
| **AI RESEARCHER (AiR)** | 26 | 26.3% |
| **CORTEX AI MODELS** | 25 | 25.3% |
| **CORTEX + MONITORING TOOLS** | 23 | 23.2% |
| **CORTEX WORKDAY TOOLKIT** | 16 | 16.2% |
| **ELIZA + Communication Integration** | 7 | 7.1% |
| **CORTEX JIRA TOOLKIT** | 6 | 6.1% |
| **ETHICS & COMPLIANCE CHAT AGENT** | 5 | 5.1% |
| **AI THINK TANK** | 3 | 3.0% |

---

## Key Cortex Capabilities Identified

### 1. Cortex Toolkits (Production Ready)
- **cortex-snow-prd**: ServiceNow integration - retrieve status, comments, create tickets
- **cortex-jira-prd**: JIRA integration - retrieve ticket status, post comments
- **cortex-workday-prd**: Employee data, org structures, reporting hierarchies
- **cortex-web-search-prd**: Web search using Bing API
- **cortex-web-scraper-prd**: HTML content extraction and scraping

### 2. Key Existing Agents
- **AI Researcher (AiR)**: Research with Quick Chat or Deep Research modes
- **AiR Planning Agent**: Planning research tasks guided by user input
- **AiR Research Report Agent**: Deep research generating comprehensive reports
- **AI Think Tank**: Multi-AI group chat for diverse perspectives
- **Eliza**: Lilly's Personal Assistant
- **Ethics & Compliance Chat**: Policy and procedures knowledge worker

### 3. AI Models Available
- **111 Inference Models**: Classification, prediction, decision-making
- **13 Embedding Models**: Semantic search, similarity matching
- **1,091 Shared Prompts**: Pre-built prompt templates
- **472 Data Configurations**: Integration configurations

### 4. Specific Cortex Agents Found
The analysis identified 50+ agents with existing Cortex agents that match their capabilities, including:
- ITSM Process Chatbot (ITSMate)
- ServiceNow Incident Extractor
- SPE Support Assistant - Automation
- AiR Planning Agent (Beta)
- AiR Research Report Agent (Beta)
- AI News Researcher
- And many more...

---

## Sample Agent Mappings

### Request Fulfillment Agent
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management
✅ **TEA AUTOMATION + CORTEX**: Integrate AI decision logic with TEA library for execution

### Knowledge Search Agent
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration
✅ **AI RESEARCHER (AiR)**: Quick Chat for searches, Deep Research for analysis
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent, AiR Research Report Agent, AI News Researcher Two

### Incident Communication Agent
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration
✅ **ELIZA + Communication Integration**: Automated notifications via Teams/Email
✅ **TEA AUTOMATION + CORTEX**: Automated execution
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot, ServiceNow Incident Extractor, SPE Support Assistant

### Major Incident Agent
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration
✅ **AI RESEARCHER (AiR)**: Comprehensive analysis with citations
✅ **AI THINK TANK**: Multi-AI perspectives for complex issues

### Compliance Monitoring Agent
✅ **ETHICS & COMPLIANCE CHAT AGENT**: Policy and procedures monitoring
✅ **CORTEX + MONITORING TOOLS**: Splunk/Dynatrace/Prometheus API integrations

---

## Implementation Approach

### Phase 1: Leverage Existing Agents (Immediate)
- 50 agents have direct Cortex agent matches
- Can be adapted/configured immediately
- Minimal development effort required

### Phase 2: Use Core Toolkits (Short-term)
- 51 agents need SNOW toolkit integration
- 16 agents need Workday toolkit
- 6 agents need JIRA toolkit
- Well-documented, production-ready

### Phase 3: Build Custom Agents (Medium-term)
- Leverage 111 inference models for custom logic
- Use 1,091 shared prompts as templates
- Integrate with TEA automation library

### Phase 4: Advanced Orchestration (Long-term)
- Multi-agent collaboration using AI Think Tank pattern
- Complex workflow orchestration
- Cross-platform integrations

---

## Recommendations

1. **Start with Existing Agents**: Prioritize the 50 agents that have direct Cortex matches
2. **Leverage SNOW Toolkit**: Focus on the 51 agents needing ServiceNow integration
3. **Pilot AiR Integration**: Test AI Researcher for knowledge and analysis agents
4. **Standardize Communication**: Use Eliza pattern for all communication agents
5. **Automation Pipeline**: Connect Cortex decision logic to TEA execution library

---

## Next Steps

1. ✅ **COMPLETE**: Detailed capability mapping for all 99 agents
2. **TODO**: Prioritize agents based on business impact and implementation complexity
3. **TODO**: Create proof-of-concept for top 3-5 agents using existing Cortex capabilities
4. **TODO**: Establish Cortex agent development standards and patterns
5. **TODO**: Train teams on Cortex toolkit usage and agent configuration

---

## Conclusion

**100% of Service Management AI agents can be built using existing Cortex infrastructure.** The platform provides:
- Production-ready toolkits for core integrations
- 1,324 existing agents to learn from and adapt
- 111 AI models for custom intelligence
- Comprehensive prompt and configuration library

This analysis demonstrates that Lilly has the foundational AI infrastructure needed to implement the entire Service Management AI agent backlog.
