# Lilly Service Management AI Agents Backlog

**Last Updated:** 2026-02-25
**Total Agents:** 106
**Status:** Analysis Complete with Implementation Recommendations

---

## 📋 Table of Contents

- [Executive Summary](#executive-summary)
- [Request Management (10 agents)](#request-management)
- [Incident Management (25 agents)](#incident-management)
- [Problem Management (17 agents)](#problem-management)
- [Event Management (21 agents)](#event-management)
- [Change Management (3 agents)](#change-management)
- [Knowledge Management (9 agents)](#knowledge-management)
- [SRE & Automation (12 agents)](#sre--automation)
- [Configuration Management (3 agents)](#configuration-management)
- [Governance & Compliance (6 agents)](#governance--compliance)

---

## Executive Summary

This backlog contains 106 AI agent opportunities for Lilly's Service Management operations, spanning all ITSM processes. Each agent has been analyzed with implementation recommendations based on existing Lilly capabilities including:

- **ServiceNow Platform** (Flow Designer, Event Management, CMDB, Performance Analytics)
- **Cortex AI** (decision-making, ML models, NLP)
- **TEA Automation Library** (execution playbooks)
- **ChatNow** (conversational interfaces)
- **Monitoring Tools** (Splunk, Dynatrace)
- **Nexthink** (device management)
- **Development Tools** (Azure DevOps, JIRA)

**Estimated Efficiency Gains:** 10-70% manual work eliminated per agent

---

## Request Management

### 1. Request Fulfillment Agent
**Supervisor:** Request Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 40-70%
**Build Team:** GSM/TEA

**Description:**
Execution-oriented agent responsible for orchestrating and completing approved service requests by coordinating workflows, triggering tasks, and invoking automations.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 2. Request Process Agent
**Supervisor:** Request Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 30-55%
**Build Team:** TEA

**Description:**
Intelligent workflow-orchestration agent managing end-to-end lifecycle of service requests from intake through fulfillment and closure.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 3. Request Creation Agent
**Supervisor:** Request Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-45%
**Build Team:** TEA

**Description:**
Allows employees to easily discover and complete correct catalog items conversationally through ChatNow interface.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **ELIZA + Communication Integration**: Adapt Eliza (Lilly's Personal Assistant) for automated notifications via Teams/Email  
✅ **EXISTING CORTEX AGENTS**: AI Researcher (AiR), AI Researcher (AiR), AI Think Tank  


---

### 4. Knowledge Search Agent
**Supervisor:** Request Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-45%
**Build Team:** TEA/GSM

**Description:**
Expands search for knowledge outside ServiceNow into other Lilly knowledge sources and brings results back into ServiceNow.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 5. Service Catalog Update Agent (Conversational)
**Supervisor:** Request Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-45%
**Build Team:** GSM

**Description:**
Allows authorized persons to update catalog items through conversational or easy UI means.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **EXISTING CORTEX AGENTS**: AI Researcher (AiR), AI Researcher (AiR), AI Think Tank  


**ServiceNow Catalog Builder + Now Assist for Creator:** Use Catalog Builder with AI assistance and approval workflows for authorized catalog changes.

---

### 6. Service Catalog Update Agent (Automated)
**Supervisor:** Request Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 20-45%
**Build Team:** GSM/TEA

**Description:**
Automatically updates catalog items for service owners based on form completion or conversation interface.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: AI Researcher (AiR), AI Researcher (AiR), AI Think Tank  


**ServiceNow Catalog Builder + Now Assist for Creator:** Use Catalog Builder with AI assistance and approval workflows for authorized catalog changes.

---

### 7. Request Status Agent
**Supervisor:** User Experience Manager Agent
**Type:** Human-Assisted (OOB AI Agent)
**Efficiency Gain:** 15-30%
**Build Team:** GSM
**Status:** Building during ServiceNow Workshop W/O 2/23/26

**Description:**
Enables users to efficiently check and update status of ServiceNow tickets, requests, tasks, and incidents by ticket number or description.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


**ServiceNow OOB AI Agent + ChatNow:** Use out-of-box status checking agent integrated with ChatNow for conversational updates plus SMS/email notifications.

---

### 8-10. [Additional Request Management Agents]
*See full table in original document for complete details*

---

## Incident Management

### 1. Incident Creation Agent
**Supervisor:** Incident Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 40-70%
**Build Team:** GSM/ChatNow

**Description:**
Rather than just fill out a form, the agent creates detailed incidents by asking follow-up questions to determine if resolution can be provided through self-service or automation vs. manual ticket resolution.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 2. Incident Routing Agent
**Supervisor:** Incident Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-35%
**Build Team:** TEA

**Description:**
Intelligent assignment agent routing incidents to most appropriate resolver by considering skills, historical performance, real-time capacity, and individual availability—not just static assignment groups.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 3. Incident Triage Agent
**Supervisor:** Incident Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-35%
**Build Team:** GSM/TEA

**Description:**
Based on knowledge articles and past incident data, dynamically asks appropriate follow-up questions to ensure proper assignment and resolution.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


**ChatNow + ServiceNow Virtual Agent + Knowledge:** Build conversational triage in ChatNow using Virtual Agent framework with Knowledge Base and similar incident history.

---

### 4. Incident Resolver Agent v2
**Supervisor:** Incident Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-35%
**Build Team:** Data Management/CTI-Global Data

**Description:**
Replaces current ServiceNow agent and uses multiple knowledge sources at Lilly plus previous incident data to determine appropriate resolution.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 5. Incident Communication Agent
**Supervisor:** Incident Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-35%
**Build Team:** GSM

**Description:**
Automatically generates communications to submitters that incident resolvers can send.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **ELIZA + Communication Integration**: Adapt Eliza (Lilly's Personal Assistant) for automated notifications via Teams/Email  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 6. Incident Trend Agent
**Supervisor:** Incident Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-35%
**Build Team:** TEA

**Description:**
Detects patterns within resolved incidents and suggests resolution via self-resolution or automated methods.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 7. Vendor Ticket Agent
**Supervisor:** Incident Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-35%
**Build Team:** TEA

**Description:**
Creates vendor issues and cross-references the ticket ID in Lilly incidents with bidirectional updates.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 8. Incident Risk Scoring Agent
**Supervisor:** Incident Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-35%
**Build Team:** TEA

**Description:**
Recalculates Incident Risk (impact × urgency × uncertainty) accounting for sentiments, blast radius, and historical volatility.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **EXISTING CORTEX AGENTS**: Clinical Trials Safety Analysis Agent, ITSM Process Chatbot - ITSMate, PRISM 360 Supply Risk Agent  


---

### 9. Auto PIR (Post Incident Review) Agent
**Supervisor:** Incident Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-35%
**Build Team:** TEA

**Description:**
Drafts PIRs using incident data and timelines, identifies contributing factors and gaps, pre-fills action items.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI THINK TANK**: Multi-AI group chat for diverse perspectives on complex issues  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 10. Incident Documentation Improvement Agent
**Supervisor:** Incident Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-35%
**Build Team:** ServiceNow/GSM
**Status:** Building during ServiceNow Workshop W/O 2/23/26

**Description:**
Finds incidents where documentation of issue and resolution is missing. Indicates incident, assignment group, assignee, group owner and patterns.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 11. Incident Alert Suppression Agent
**Supervisor:** Incident Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-35%
**Build Team:** TEA

**Description:**
Reviews incidents to detect incidents created from alerts with no action taken and closed in 30 seconds or less.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI THINK TANK**: Multi-AI group chat for diverse perspectives on complex issues  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 12. Incident Business Risk Translator Agent
**Supervisor:** Incident Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-35%
**Build Team:** GSM

**Description:**
Translates technical incidents into clear business-impact narratives using service criticality, financial exposure, regulatory risk, and customer impact data.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **EXISTING CORTEX AGENTS**: Clinical Trials Safety Analysis Agent, ITSM Process Chatbot - ITSMate, PRISM 360 Supply Risk Agent  


---

### 13. Service Desk Triage Agent
**Supervisor:** Incident Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-35%
**Build Team:** GSM/TEA

**Description:**
Intelligent first-line support agent performing initial diagnosis and determining if issue can be resolved at Tier 1 or requires escalation.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX AI PLATFORM**: Leverage Cortex's 111 inference models, 13 embedding models, and 1,091 shared prompts to build custom agent  


---

### 14. Proactive End User Device Resolution Agent
**Supervisor:** Incident Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-35%
**Build Team:** WPS/Nexthink Team
**Technology:** Nexthink

**Description:**
Resolves issues on end user devices based on threshold metrics using Nexthink agent before issues are reported as incidents.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  
✅ **EXISTING CORTEX AGENTS**: Clinical Trials Efficacy Analysis Agent, ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor  


**Nexthink + ServiceNow + Automated Remediation:** Leverage Nexthink device monitoring and remediation. Trigger ServiceNow workflows when thresholds breached.

---

### 15. Chat Resolution Agent
**Supervisor:** Incident Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-35%
**Build Team:** WPS/ChatNow & Nexthink Team
**Technology:** ChatNow/Nexthink

**Description:**
Resolves issues on end user devices using employee-supplied symptoms via Nexthink agent through ChatNow.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **ELIZA + Communication Integration**: Adapt Eliza (Lilly's Personal Assistant) for automated notifications via Teams/Email  
✅ **EXISTING CORTEX AGENTS**: AI Researcher (AiR), AI Researcher (AiR), AI Think Tank  


**ChatNow + Nexthink Remote Actions:** Build ChatNow interface to Nexthink remote actions for user-described symptoms with consent-based remediation.

---

### 16. Ops Investigation Agent
**Supervisor:** Incident Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-35%
**Build Team:** GSM/TEA

**Description:**
Pulls details to troubleshoot issues including logs, timetable of events, and related ITSM records including knowledge articles.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 17. Outage Agent
**Supervisor:** Incident Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-35%
**Build Team:** GSM/TEA

**Description:**
Monitors stats to declare an outage based on patterns and impact analysis.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  


---

### 18. Development Fix Recommend Agent
**Supervisor:** Incident Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-35%
**Build Team:** TEA

**Description:**
Agent that recommends solution development fixes for recurring technical incidents.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX JIRA TOOLKIT**: JIRA integration for development ticket tracking and updates  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 19. SMO Analysis Agent
**Supervisor:** Incident Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-35%
**Build Team:** TEA

**Description:**
Analyzes patterns, determines improvement opportunities, and reports operations state to Service Management Office.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  


---

### 20-25. [Additional Incident Management Agents]
*See sections below for Major Incident and additional specialized incident agents*

---

## Major Incident Management

### 1. Propose Major Incident
**Supervisor:** Incident Manager Agent
**Type:** Human-Assisted (Custom)
**Efficiency Gain:** 15-30%
**Build Team:** GSM
**Status:** Building during ServiceNow Workshop W/O 2/23/26

**Description:**
Agentic workflow looks for similar incidents and evaluates if it should be a major incident by accessing knowledge article criteria.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **AI THINK TANK**: Multi-AI group chat for diverse perspectives on complex issues  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 2. IRT Notification and Scheduler Agent
**Supervisor:** Major Incident Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-30%
**Build Team:** GSM/TEA

**Description:**
Auto-notifies Incident Response Team via Everbridge and schedules IRT meeting.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **ELIZA + Communication Integration**: Adapt Eliza (Lilly's Personal Assistant) for automated notifications via Teams/Email  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


**Everbridge API + ServiceNow + Teams Calendar:** Integrate Everbridge API for IRT notifications via ServiceNow workflows with Teams meeting auto-scheduling.

---

### 3. Major Incident Impact Agent
**Supervisor:** Major Incident Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-30%
**Build Team:** TEA

**Description:**
Looks for major incidents and recommends if IAT or IRT is warranted based on notes/chat analysis.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **ELIZA + Communication Integration**: Adapt Eliza (Lilly's Personal Assistant) for automated notifications via Teams/Email  
✅ **AI THINK TANK**: Multi-AI group chat for diverse perspectives on complex issues  
✅ **EXISTING CORTEX AGENTS**: AI Researcher (AiR), AI Researcher (AiR), AI Think Tank  


---

## Problem Management

### 1. Problem Ticket Creation Agent
**Supervisor:** Problem Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-30%
**Build Team:** GSM/TEA

**Description:**
Leverages existing agent that determines if incidents should be considered for a problem ticket and actually creates the problem with similar incidents linked.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 2. Root Cause Analysis Agent v2.0
**Supervisor:** Problem Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 10%
**Build Team:** GSM/TEA

**Description:**
Enhance existing AI agent that provides recommendations for RCA and root cause.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  


---

### 3. Known Error Management Agent
**Supervisor:** Problem Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Knowledge-driven reliability agent responsible for identifying, creating, maintaining, and operationalizing known errors and workarounds.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 4. RCA Validator Agent
**Supervisor:** Problem Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Evaluates Root Cause Analysis documentation against quality standards, completeness criteria, and best practices.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  


---

### 5. Problem Business Risk Translator Agent
**Supervisor:** Problem Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Translates technical problems into clear business-impact narratives using service criticality, financial exposure, regulatory risk, and customer impact data.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **EXISTING CORTEX AGENTS**: Clinical Trials Safety Analysis Agent, PRISM 360 Supply Risk Agent, QA Fastlane: (3/5) Pitch Deck Agent  


---

### 6. Document Assistant Agent
**Supervisor:** Problem Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-30%
**Build Team:** GSM/TEA

**Description:**
Assists with documenting problems and providing detailed descriptions.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  


---

### 7. Problem to Known Error Agent
**Supervisor:** Problem Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Automatically raises and documents a problem as a known error for all deferred defects in JIRA or HP ALM.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX JIRA TOOLKIT**: JIRA integration for development ticket tracking and updates  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


**JIRA/ALM API + ServiceNow Problem:** Build API integration between defect tracking and ServiceNow. Auto-create known error records for deferred defects with bidirectional sync.

---

### 8. Events Problem Suggestion Agent
**Supervisor:** Problem Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Looks into events and recommends creation of problem tickets for recurring event patterns.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 9. Fix Validation Assistant Agent
**Supervisor:** Problem Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Assists with validating that a fix has terminated the problem by monitoring incident recurrence.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 10. Engineering Fixes Agent
**Supervisor:** Problem Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-30%
**Build Team:** GSM/TEA

**Description:**
Suggests engineering fixes for problems requiring code or configuration changes.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  


---

### 11. Known Error To Automation Agent
**Supervisor:** Problem Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Reviews known errors for potential automations and creates automation backlog items.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI THINK TANK**: Multi-AI group chat for diverse perspectives on complex issues  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 12. Reoccurring Problem Fixer Agent
**Supervisor:** Problem Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-30%
**Build Team:** GSM/TEA

**Description:**
Looks for reoccurring problems and suggests where to focus to permanently fix the issue (multi-layered problem analysis).

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  


---

### 13. Communications Writer Agent
**Supervisor:** Problem Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-30%
**Build Team:** TEA

**Description:**
Looks at associated incidents and ensures communication is drafted and sent to update management and impacted parties.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **ELIZA + Communication Integration**: Adapt Eliza (Lilly's Personal Assistant) for automated notifications via Teams/Email  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 14. Artifact Preservation Suggestion Agent
**Supervisor:** Problem Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-30%
**Build Team:** GSM/TEA

**Description:**
Suggests what artifacts to preserve to assist with similar issues in the future.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX AI PLATFORM**: Leverage Cortex's 111 inference models, 13 embedding models, and 1,091 shared prompts to build custom agent  


---

### 15. RCA Task Generation Agent
**Supervisor:** Problem Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-30%
**Build Team:** TEA

**Description:**
Breaks down RCA work into investigative tasks for appropriate teams.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **ELIZA + Communication Integration**: Adapt Eliza (Lilly's Personal Assistant) for automated notifications via Teams/Email  


---

### 16. Problem Opportunity Monitoring Agent
**Supervisor:** Problem Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-30%
**Build Team:** TEA

**Description:**
Monitors problems that are not making progress and alerts SMO of stalled problems.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 17. Incident Trends Monitoring Agent (Problem Creation)
**Supervisor:** Problem Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-30%
**Build Team:** TEA

**Description:**
Looks at incident trends for specific CIs and determines if a proactive problem may be warranted.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

## Event Management

### 1. Self-Healing Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 25%
**Build Team:** TEA

**Description:**
Creation of playbooks from received events focuses on self-healing resolution. If implemented for 75% of alerts, expect 25% reduction in labor.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 2. Event Monitoring Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-40%
**Build Team:** TEA

**Description:**
Signal-detection and noise-reduction agent continuously observing telemetry, detecting meaningful events, and distinguishing real service impact from background noise.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 3. Event Correlation Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-40%
**Build Team:** TEA

**Description:**
Causal-analysis agent grouping related events, identifying root events, and converting alert storms into single actionable operational narratives.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 4. Event Resolution Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-40%
**Build Team:** TEA

**Description:**
Action-oriented agent driving events from detection to closure by executing predefined response actions and coordinating handoffs.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 5. Noise Reduction Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-40%
**Build Team:** TEA

**Description:**
Event-filtering agent suppressing irrelevant, duplicate, and low-value events to reduce alert fatigue.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 6. Threshold Breach Monitor Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-40%
**Build Team:** TEA

**Description:**
Agent to automatically monitor threshold breaches and suggest optimal threshold adjustments.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 7. Observability Agent
**Supervisor:** Event Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 20-40%
**Build Team:** GSM/TEA

**Description:**
Compares failure data across observability tools and provides contextual summarization of possible causes.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 8. Outage Opening/Closing Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-40%
**Build Team:** TEA

**Description:**
Allows creation of outage records in ServiceNow based on event playbooks. Feeds agents' ability to identify outages and close incidents if outage was planned.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 9. Resolution Action Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-40%
**Build Team:** TEA

**Description:**
Looks at event plan and runs resolution action or submits to Incident Management or a human.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 10. Large Issue and Events Monitoring Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-40%
**Build Team:** TEA

**Description:**
Monitors for big issues based on number of alerts triggered across several CIs. Notifies Incident Process Owner and Manager.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 11. Instant Closed Events Monitoring Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-40%
**Build Team:** TEA

**Description:**
Monitors instantly closed non-automated/non-agentic resolved events to identify automation opportunities.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 12. Incident Patterns Monitoring Agent
**Supervisor:** Event Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-40%
**Build Team:** TEA

**Description:**
Monitors incident patterns for event management opportunities and informs service owners.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 13. Events Without Actions Monitoring Agent
**Supervisor:** Event Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-40%
**Build Team:** GSM

**Description:**
Monitors for events without action and suggests improvements to service owners.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 14. Event Candidates for Monitoring Agent
**Supervisor:** Event Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-40%
**Build Team:** GSM

**Description:**
Monitors incidents reported by humans that could potentially be monitored. Suggests what could be monitored that isn't today.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 15. Monitoring and Alerting Agent
**Supervisor:** Event Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 20-40%
**Build Team:** GSM/TEA

**Description:**
Monitors and alerts for items not run by an agent or automated, and/or potentially failed.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 16-21. [Additional Event Management Agents]
*Multiple Event Correlation Agents with similar capabilities - see original table for complete details*

---

## Change Management

### 1. Change Record Assistant Agent
**Supervisor:** Change Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 40-60%
**Build Team:** TEA

**Description:**
Assists with creating change records from problems with recommended fixes based on CMDB and architectural diagrams.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  


---

### 2. Change Collision Detector Agent
**Supervisor:** Change Manager Agent
**Type:** Autonomous (OOB)
**Efficiency Gain:** 20-40%
**Build Team:** GSM

**Description:**
Identifies scheduling conflicts, dependency clashes, and risk amplification across planned changes using CMDB relationships.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **EXISTING CORTEX AGENTS**: Clinical Trials Safety Analysis Agent, PRISM 360 Supply Risk Agent, QA Fastlane: (3/5) Pitch Deck Agent  


---

### 3. Release Forecasting Agent
**Supervisor:** Release Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-40%
**Build Team:** GSM

**Description:**
Analyzes historical release data, dependency complexity, and delivery patterns to forecast release readiness and risk.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI THINK TANK**: Multi-AI group chat for diverse perspectives on complex issues  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  
✅ **EXISTING CORTEX AGENTS**: Clinical Trials Safety Analysis Agent, PRISM 360 Supply Risk Agent, QA Fastlane: (3/5) Pitch Deck Agent  


---

## Knowledge Management

### 1. Knowledge Article Recommendation Agent
**Supervisor:** Knowledge Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-35%
**Build Team:** TEA

**Description:**
Identifies incidents with no supporting knowledge and detects repeated human explanations in ticket comments. Recommends new article creation.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 2. Knowledge Relevance and Retirement Agent
**Supervisor:** Knowledge Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-35%
**Build Team:** TEA

**Description:**
Monitors usage, feedback, and incident linkage. Flags outdated or unused articles and recommends updates or retirement.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 3. Knowledge Creation Agent
**Supervisor:** Knowledge Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-35%
**Build Team:** GSM

**Description:**
Creates knowledge articles based on information in ITSM records or external sources.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 4. Knowledge Revision Agent
**Supervisor:** Knowledge Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-35%
**Build Team:** GSM

**Description:**
Recommends and allows update of existing knowledge based on ITSM record trends and alignment with external sources.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 5. External Intelligence Agent
**Supervisor:** Knowledge Manager Agent
**Type:** Autonomous (Cortex)
**Efficiency Gain:** 15-35%
**Build Team:** TEA

**Description:**
Connects to external community sources of knowledge to help with problem RCA and incident troubleshooting.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 6. Knowledge Health Agent
**Supervisor:** Knowledge Manager Agent
**Type:** Autonomous (OOB)
**Efficiency Gain:** 15-35%
**Build Team:** GSM

**Description:**
Analyzes knowledge article usage, incident linkage, and feedback to identify stale, unused, or missing knowledge.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 7. Metadata Intelligence Agent
**Supervisor:** Knowledge Manager Agent
**Type:** Autonomous (OOB)
**Efficiency Gain:** 15-35%
**Build Team:** GSM

**Description:**
Automatically assigns and maintains taxonomy, metadata, and tagging for ITSM records and knowledge articles.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: AiR Planning Agent (Beta), AiR Research Report Agent (Beta), AI News Researcher Two  


---

### 8. SLA Sentinel Agent
**Supervisor:** SLA Manager Agent
**Type:** Autonomous (OOB)
**Efficiency Gain:** 15-35%
**Build Team:** GSM

**Description:**
Predicts impending SLA breaches using historical performance and workload trends, proactively escalates risk before violations.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  
✅ **EXISTING CORTEX AGENTS**: Clinical Trials Safety Analysis Agent, PRISM 360 Supply Risk Agent, QA Fastlane: (3/5) Pitch Deck Agent  


---

### 9. Web Research and Recommendation AI Agent
**Supervisor:** Knowledge Manager Agent
**Type:** Human-Assisted (OOB AI Agent)
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Assists users in resolving issues by analyzing the problem and generating resolution steps using web search tools.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  


---

## SRE & Automation

### 1. Fix Automation Agent (SRE)
**Supervisor:** SRE Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 40-70%
**Build Team:** GSM/TEA

**Description:**
Execution-focused SRE agent responsible for safely applying automated remediations to known, recurring, or well-understood reliability issues.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 2. Fix Automation Agent (Various)
**Supervisor:** Automation Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 40-70%
**Build Team:** GSM

**Description:**
Intelligent remediation agent executing proven, low-risk corrective actions to restore service when known issues occur.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: Clinical Trials Safety Analysis Agent, PRISM 360 Supply Risk Agent, QA Fastlane: (3/5) Pitch Deck Agent  


---

### 3. Automation Analysis Agent
**Supervisor:** SRE Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 20-50%
**Build Team:** TEA

**Description:**
Looks at automation failures and performs self-healing or creates incidents to automation team with appropriate assignment.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 4. Automation Development Agent (SRE)
**Supervisor:** SRE Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-50%
**Build Team:** GSM

**Description:**
Build-focused agent responsible for designing, implementing, testing, and operationalizing automation.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX JIRA TOOLKIT**: JIRA integration for development ticket tracking and updates  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 5. Automation Development Agent (Various)
**Supervisor:** Automation Manager Agent
**Type:** Hybrid
**Efficiency Gain:** 15-30%
**Build Team:** GSM/TEA

**Description:**
Intelligent build-enablement agent turning automation opportunities into production-ready assets.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX JIRA TOOLKIT**: JIRA integration for development ticket tracking and updates  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 6. DevOps Agent (SRE)
**Supervisor:** SRE Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-50%
**Build Team:** GSM

**Description:**
Delivery-oriented agent automating, governing, and optimizing software delivery lifecycle.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX JIRA TOOLKIT**: JIRA integration for development ticket tracking and updates  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 7. DevOps Agent (Release)
**Supervisor:** Release Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-40%
**Build Team:** GSM

**Description:**
Intelligent delivery and operations agent automating code flow from development through deployment.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX JIRA TOOLKIT**: JIRA integration for development ticket tracking and updates  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 8. Validation Agent
**Supervisor:** SRE Manager Agent
**Type:** Autonomous (Cortex)
**Efficiency Gain:** 20-50%
**Build Team:** TEA

**Description:**
Control and assurance-focused agent verifying that systems and automated actions behave as intended.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 9. Testing Agent (B)
**Supervisor:** SRE Manager Agent
**Type:** Autonomous (Cortex)
**Efficiency Gain:** 20-50%
**Build Team:** TEA

**Description:**
Pre- and post-change assurance agent exercising systems under expected and failure conditions.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  


---

### 10. Testing Agent (Various)
**Supervisor:** Testing Manager Agent
**Type:** Autonomous
**Efficiency Gain:** 15-30%
**Build Team:** TEA

**Description:**
Quality-assurance agent validating automations, workflows, and agentic solutions before and after deployment.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


---

### 11. Runbook Generator Agent
**Supervisor:** SRE Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-50%
**Build Team:** GSM

**Description:**
Generates and maintains operational runbooks by synthesizing incident history and automation workflows.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  
✅ **EXISTING CORTEX AGENTS**: ITSM Process Chatbot - ITSMate, ServiceNow Incident Extractor, SPE Support Assistant - Automation  


---

### 12. SRE Agent
**Supervisor:** SRE Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-50%
**Build Team:** GSM

**Description:**
Human-assisted intelligent operations agent monitoring, analyzing, and improving service reliability using SRE principles.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

## Configuration Management

### 1. CMDB Query Agent
**Supervisor:** Configuration Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 10-25%
**Build Team:** GSM

**Description:**
Allows for query of CI records through conversational means.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **EXISTING CORTEX AGENTS**: AI Researcher (AiR), AI Researcher (AiR), AI Think Tank  


---

### 2. CI Update Agent
**Supervisor:** Configuration Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 10-25%
**Build Team:** GSM

**Description:**
Allows authorized individuals to update CI records through conversational means.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **EXISTING CORTEX AGENTS**: AI Researcher (AiR), AI Researcher (AiR), AI Think Tank  


**ServiceNow CMDB + Approval Workflow + Audit Logging:** Build conversational CI update interface with strict authorization, approval workflows, and comprehensive audit logs.

---

### 3. Service Mapping Agent
**Supervisor:** Configuration Manager Agent
**Type:** Autonomous (OOB)
**Efficiency Gain:** 10-25%
**Build Team:** GSM

**Description:**
Automates a good portion of Service Mapping within ServiceNow.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution  


**ServiceNow Service Mapping OOB + Discovery:** Leverage out-of-box Service Mapping enhanced with additional discovery patterns and IntegrationHub for API-based discovery.

---

## Governance & Compliance

### 1. Process Governance Agent
**Supervisor:** ITSM Governance Manager
**Type:** Autonomous (OOB)
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Monitors execution of ITSM processes to detect non-compliance, gaps, and deviations from policy.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **ETHICS & COMPLIANCE CHAT AGENT**: Policy and procedures knowledge worker for compliance monitoring  


---

### 2. Continuous Improvement Agent
**Supervisor:** Continuous Management Manager
**Type:** Human-Assisted
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Analyzes trends across all ITSM processes to identify systemic inefficiencies and recommend improvements.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  


---

### 3. Executive Insights Agent
**Supervisor:** ITSM Reporting Manager Agent
**Type:** Autonomous (OOB)
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Aggregates operational metrics into executive-level dashboards linking IT performance to business KPIs and OKRs.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 4. Compliance Monitoring Agent
**Supervisor:** ITSM Reporting Manager Agent
**Type:** Autonomous (OOB)
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Continuously scans ITSM records to detect violations of policy and regulatory requirements.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **ETHICS & COMPLIANCE CHAT AGENT**: Policy and procedures knowledge worker for compliance monitoring  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

### 5. Audit Prep Agent
**Supervisor:** ITSM Reporting Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Prepares ITSM records for audit by validating documentation completeness, traceability, and approvals.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations  
✅ **ETHICS & COMPLIANCE CHAT AGENT**: Policy and procedures knowledge worker for compliance monitoring  


---

### 6. Service Design Readiness Agent
**Supervisor:** Service Design Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Validates whether service design is operationally ready for production by checking monitoring, runbooks, and resilience criteria.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation  


---

## Additional Service Management Agents

### 1. Resource Alignment Agent
**Supervisor:** Resource Manager Agent
**Type:** Human-Assisted
**Efficiency Gain:** 20-50%
**Build Team:** GSM

**Description:**
Analyzes workload, ticket volumes, SLA pressure, and skill distribution to identify staffing bottlenecks.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  


---

### 2. Analyze and Improve Services
**Supervisor:** Service Manager Agent
**Type:** Human-Assisted (OOB Agentic Workflow)
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Analyzes customer feedback and operational trends to identify improvement opportunities.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  


**ServiceNow OOB Agentic Workflow + Performance Analytics:** Leverage out-of-box workflow for service analysis with integrated survey platforms and trend identification.

---

### 3. Generate My Work Plan
**Supervisor:** Service Manager Agent
**Type:** Human-Assisted (OOB Agentic Workflow)
**Efficiency Gain:** 15-30%
**Build Team:** GSM
**Status:** Building during ServiceNow Workshop W/O 2/23/26

**Description:**
Generates structured work plan prioritizing tasks based on priority, SLAs, and sentiment.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX AI PLATFORM**: Leverage Cortex's 111 inference models, 13 embedding models, and 1,091 shared prompts to build custom agent  


**ServiceNow Workload Optimization + OOB Agentic Workflow:** Use out-of-box work plan generation with Outlook/Teams calendar integration and AI prioritization.

---

### 4. Identify Ways to Improve Service
**Supervisor:** Service Manager Agent
**Type:** Human-Assisted (OOB Agentic Workflow)
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Analyzes survey data to evaluate satisfaction metrics, identify concerns, and provide improvement recommendations.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics  


---

### 5. Manage Ticket with Voice AI Agent
**Supervisor:** User Experience Manager Agent
**Type:** Human-Assisted (OOB AI Agent)
**Efficiency Gain:** 15-30%
**Build Team:** GSM

**Description:**
Voice AI agent assisting users with managing active tickets, fetching details, adding comments, or escalating urgency.

**Implementation Recommendation:**

**Existing Cortex Capabilities:**  
✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates  
✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing  


**ServiceNow OOB Voice Agent + Telephony Integration:** Leverage out-of-box Voice AI Agent with Lilly telephony systems and Azure Speech Services.

---

## Implementation Priorities

### High Impact (40-70% efficiency gain)
1. Request Fulfillment Agent
2. Incident Creation Agent
3. Fix Automation Agent (both versions)
4. Change Record Assistant Agent

### Medium-High Impact (20-40% efficiency gain)
1. Self-Healing Agent
2. Event Monitoring/Correlation/Resolution Agents
3. Automation Analysis/Development Agents
4. DevOps Agents
5. SRE Agents
6. Request Creation Agent

### Medium Impact (15-35% efficiency gain)
1. All Incident Management agents
2. Problem Management agents
3. Knowledge Management agents
4. Major Incident agents

### Foundation Impact (10-25% efficiency gain)
1. Configuration Management agents
2. Governance & Compliance agents

---

## Technology Stack Summary

### Core Platforms
- **ServiceNow:** ITSM platform, workflows, CMDB, analytics
- **Cortex AI:** Decision-making, ML models, NLP, pattern detection
- **TEA:** Automation execution library
- **ChatNow:** Conversational interfaces

### Integration Points
- **Monitoring:** Splunk, Dynatrace, Prometheus
- **Device Management:** Nexthink
- **Development:** Azure DevOps, JIRA, GitHub
- **Communication:** Everbridge, Teams, Slack
- **Enterprise Search:** SharePoint, Confluence

---

## Next Steps

1. **Prioritization Workshop:** Review backlog with stakeholders to prioritize based on business value and technical feasibility
2. **Pilot Selection:** Choose 3-5 high-impact agents for initial pilot
3. **MVP Development:** Build minimum viable products using recommended technology stack
4. **Measure & Iterate:** Track efficiency gains and refine before scaling
5. **Scale Deployment:** Gradually roll out proven agents across organization

---

**Document Owner:** Service Management Office
**Contributors:** GSM, TEA, ChatNow Team, Data Management
**Review Cycle:** Quarterly
