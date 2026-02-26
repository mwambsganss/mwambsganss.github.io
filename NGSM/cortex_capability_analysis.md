# Cortex Capability Analysis for Lilly Service Management AI Agents

**Analysis Date:** 2026-02-25

## Summary

- **Total Agents Analyzed:** 96
- **Buildable with Existing Cortex:** ✅ 96 (100.0%)
- **Cortex Shared Agents Available:** 1324
- **Cortex Toolkits:** 5
- **AI Models:** 111 inference, 13 embedding

## Key Cortex Capabilities

### Toolkits
- **cortex-snow-prd**: ServiceNow integration - retrieve status, comments, create tickets
- **cortex-jira-prd**: JIRA integration - retrieve ticket status, post comments
- **cortex-workday-prd**: Employee data, org structures, reporting hierarchies
- **cortex-web-search-prd**: Web search using Bing API
- **cortex-web-scraper-prd**: HTML content extraction and scraping

### Key Agents
- **AI Researcher (AiR)**: Research with Quick Chat or Deep Research modes
- **AiR Planning Agent**: Planning research tasks guided by user input
- **AiR Research Report Agent**: Deep research generating comprehensive reports
- **AI Think Tank**: Multi-AI group chat for diverse perspectives
- **Eliza**: Lilly's Personal Assistant
- **Ethics & Compliance Chat**: Policy and procedures knowledge worker

## Agent-by-Agent Analysis

### Asset Lifecycle Agent
✅ **: Use Cortex AI for asset lifecycle tracking and retirement recommendations.

### Audit Trail Agent
✅ **: Use SNOW toolkit to track and report on all ITSM audit activities.

### Auto-Remediation Agent
✅ **: Use Cortex AI for remediation decisions with TEA automated script execution.

### Automation Orchestration Agent
✅ **: Integrate Cortex agent with TEA library and ServiceNow Flow Designer orchestration.

### Backup Verification Agent
✅ **: Build Cortex agent with Veeam/backup tool integrations for verification automation.

### CI Health Check Agent
✅ **: Use Cortex AI for CI health scoring based on incidents, changes, and performance metrics.

### CI Impact Prediction Agent
✅ **: Leverage Cortex AI for predicting impact of CI changes on services.

### CI Relationship Mapping Agent
✅ **: Use Cortex AI for relationship discovery and mapping via SNOW CMDB data.

### CMDB Population Agent
✅ **: Build Cortex agent with ServiceNow Discovery and asset management tool APIs.

### CMDB Reconciliation Agent
✅ **: Leverage Cortex AI for intelligent data reconciliation across multiple sources.

### Capacity Planning Agent
✅ **CORTEX AI + Resource Analytics**: Use Cortex AI models with infrastructure monitoring data for capacity forecasting.

### Catalog Management Agent
✅ **CORTEX AI + SNOW Data Integration**: Use Cortex AI models to analyze catalog usage patterns with SNOW toolkit data access.

### Change Approval Agent
✅ **CORTEX WORKDAY + SNOW + Workflow**: Combine Workday org data with SNOW toolkit for intelligent approval routing.

### Change Calendar Agent
✅ **CORTEX + Calendar Integration**: Build Cortex agent with Google Calendar/Outlook integration for maintenance window management.

### Change Communication Agent
✅ **ELIZA + Communication Platform**: Adapt Eliza architecture for automated change notifications via Teams/Email.

### Change Impact Analysis Agent
✅ **CORTEX AI + CMDB Analysis**: Use Cortex AI with CMDB relationship data to assess downstream impacts.

### Change Implementation Agent
✅ **CORTEX + TEA + CI/CD**: Integrate Cortex agent with TEA automation and CI/CD pipelines for orchestration.

### Change Request Generator Agent
✅ **CORTEX SNOW TOOLKIT + Change Templates**: Use SNOW toolkit to create change requests from problem records with standard templates.

### Change Risk Assessment Agent
✅ **CORTEX AI + Historical Analysis**: Use Cortex AI models to analyze historical change success rates via SNOW toolkit data.

### Change Rollback Agent
✅ **CORTEX AI + Automation Decision**: Use Cortex AI for rollback decision logic with TEA automated rollback procedures.

### Change Scheduling Agent
✅ **CORTEX AI + Calendar Integration**: Use Cortex AI for conflict detection with calendar/maintenance window integration.

### ChatOps Agent
✅ **ELIZA + Teams/Slack Integration**: Adapt Eliza architecture for Teams/Slack bot with ITSM command execution.

### Compliance Monitoring Agent
✅ **: Adapt Ethics & Compliance Chat agent with compliance monitoring logic.

### Configuration Audit Agent
✅ **: Leverage Cortex AI for configuration compliance monitoring and drift detection.

### Configuration Baseline Agent
✅ **: Use Cortex AI to establish and monitor configuration baselines.

### Configuration Change Detection Agent
✅ **: Build Cortex agent with configuration monitoring tools for change detection.

### Configuration Documentation Agent
✅ **: Use AiR to generate comprehensive CI documentation from CMDB data.

### Cost Optimization Agent
✅ **: Use Cortex AI for cost analysis and optimization recommendations.

### Deployment Automation Agent
✅ **: Integrate Cortex agent with Jenkins/Azure DevOps for intelligent deployment decisions.

### Emergency Change Agent
✅ **CORTEX SNOW TOOLKIT + Fast-Track Workflow**: Use SNOW toolkit with accelerated approval and notification logic.

### Event Alerting Agent
✅ **CORTEX + Notification Integration**: Build Cortex agent with Teams/Email/PagerDuty integrations for multi-channel alerting.

### Event Analytics Agent
✅ **CORTEX AI + Time Series Analysis**: Use Cortex AI models for event trend analysis and predictive insights.

### Event Collection Agent
✅ **CORTEX + Monitoring Tool APIs**: Build Cortex agent with integrations to Splunk, Dynatrace, Prometheus APIs for event ingestion.

### Event Correlation Agent
✅ **CORTEX AI + Pattern Detection**: Leverage Cortex AI models for cross-tool event correlation and pattern recognition.

### Event Dashboard Agent
✅ **CORTEX AI + Visualization APIs**: Integrate Cortex AI with Grafana/Splunk APIs for real-time dashboard updates.

### Event Enrichment Agent
✅ **CORTEX WORKDAY + CMDB Integration**: Use Cortex Workday toolkit for owner identification and CMDB data enrichment.

### Event Filtering Agent
✅ **CORTEX AI + Rule Engine**: Use Cortex inference models for intelligent filtering with configurable thresholds.

### Event Noise Reduction Agent
✅ **CORTEX AI + ML Models**: Leverage Cortex AI models for noise reduction using historical event data patterns.

### Event Remediation Agent
✅ **CORTEX AI + TEA Automation**: Combine Cortex AI decision logic with TEA automated remediation workflows.

### Event-to-Incident Agent
✅ **CORTEX SNOW TOOLKIT + Threshold Logic**: Use SNOW toolkit for automated incident creation based on event severity.

### Feedback Collection Agent
✅ **: Use SNOW toolkit with survey tool integration for feedback collection.

### Governance Reporting Agent
✅ **: Leverage AiR to generate comprehensive governance reports with insights.

### Incident Assignment Agent
✅ **CORTEX WORKDAY TOOLKIT + SNOW**: Combine Workday org data with SNOW toolkit for intelligent assignment based on skills and workload.

### Incident Classification Agent
✅ **CORTEX AI + Classification Models**: Leverage Cortex inference models with incident categorization prompts from shared prompt library (1,091 available).

### Incident Communication Agent
✅ **ELIZA + Email/Teams Integration**: Adapt Eliza assistant architecture with communication plugins for stakeholder updates.

### Incident Creation Agent
✅ **CORTEX SNOW TOOLKIT + ChatNow**: Use Cortex SNOW Agent Toolkit for incident creation with conversational guidance.

### Incident Diagnosis Agent
✅ **AI RESEARCHER (AiR) + Knowledge Base**: Leverage AiR Research Report Agent for comprehensive diagnosis with historical incident analysis.

### Incident Knowledge Capture Agent
✅ **AiR RESEARCH REPORT AGENT + SNOW KB**: Use AiR to generate comprehensive incident reports and update ServiceNow knowledge base.

### Incident Prioritization Agent
✅ **CORTEX AI + Impact Analysis**: Use Cortex AI decision models similar to priority agents already in Cortex ecosystem.

### Incident Resolution Agent
✅ **CORTEX AI + TEA Automation + SNOW**: Integrate Cortex AI for solution recommendation with TEA automation scripts via SNOW toolkit.

### Incident Trend Analysis Agent
✅ **CORTEX AI + Analytics Models**: Leverage Cortex AI models with ServiceNow Performance Analytics data via SNOW toolkit.

### Infrastructure Provisioning Agent
✅ **: Build Cortex agent with Terraform/Ansible API integration for automated provisioning.

### KPI Dashboard Agent
✅ **: Build Cortex agent with Tableau/PowerBI integration for automated KPI dashboards.

### Knowledge Article Creation Agent
✅ **AiR RESEARCH REPORT AGENT + SNOW KB**: Use AiR to generate comprehensive knowledge articles and publish via SNOW toolkit.

### Knowledge Article Retirement Agent
✅ **CORTEX AI + Usage Analytics**: Leverage Cortex AI to analyze article usage and accuracy metrics for retirement decisions.

### Knowledge Article Review Agent
✅ **CORTEX AI + NLP Analysis**: Leverage Cortex AI models for article quality assessment and improvement recommendations.

### Knowledge Article Versioning Agent
✅ **: Use SNOW toolkit for article versioning with automated change tracking.

### Knowledge Feedback Agent
✅ **: Use SNOW toolkit to collect and analyze knowledge article feedback ratings.

### Knowledge Gap Identification Agent
✅ **: Use Cortex AI to identify recurring issues without knowledge articles via SNOW data.

### Knowledge Recommendation Agent
✅ **: Use Cortex AI to recommend relevant knowledge articles based on ticket context via SNOW toolkit.

### Knowledge Search Agent
✅ **AI RESEARCHER (AiR) + Semantic Search**: Use AiR Quick Chat mode with ServiceNow knowledge base semantic search.

### Knowledge Translation Agent
✅ **CORTEX AI + Translation Models**: Leverage Cortex multilingual AI models for knowledge article translation.

### Knowledge Usage Analytics Agent
✅ **: Use Cortex AI for knowledge base usage pattern analysis and optimization.

### Known Error Database Agent
✅ **CORTEX AI + SNOW KEDB**: Integrate Cortex AI for KEDB article recommendations using SNOW toolkit.

### Language Translation Agent
✅ **: Leverage Cortex multilingual capabilities for real-time translation.

### License Management Agent
✅ **: Build Cortex agent with SAM tool integration for license optimization.

### Major Incident Agent
✅ **AI THINK TANK + War Room Coordination**: Use AI Think Tank for multi-perspective analysis during major incidents with SNOW toolkit for updates.

### Notification Management Agent
✅ **: Build Cortex agent with multi-channel notification integrations.

### Patch Management Agent
✅ **: Use Cortex AI for patch risk assessment with SNOW toolkit for change management.

### Performance Monitoring Agent
✅ **: Build Cortex agent with Dynatrace/AppD API integration for performance monitoring.

### Policy Enforcement Agent
✅ **: Use Cortex AI to enforce ITSM policies via automated validation checks.

### Post-Implementation Review Agent
✅ **AiR RESEARCH REPORT AGENT + Change Analysis**: Leverage AiR to generate comprehensive PIR reports with lessons learned.

### Problem Communication Agent
✅ **ELIZA + Notification System**: Adapt Eliza architecture with automated communication for problem updates.

### Problem Diagnosis Agent
✅ **AI THINK TANK + RCA Tools**: Use AI Think Tank multi-AI perspectives for comprehensive root cause analysis.

### Problem Identification Agent
✅ **CORTEX AI + Pattern Recognition**: Use Cortex inference models with incident correlation analysis via SNOW toolkit data.

### Problem Investigation Agent
✅ **AI RESEARCHER (AiR) + Deep Research**: Leverage AiR Deep Research mode for thorough root cause analysis with citation-rich reports.

### Problem Resolution Agent
✅ **CORTEX AI + TEA Automation**: Combine Cortex AI solution recommendations with TEA automated remediation scripts.

### Problem Review Agent
✅ **AI RESEARCHER (AiR) + Report Generation**: Leverage AiR Research Report Agent for comprehensive problem review documentation.

### Problem Trend Analysis Agent
✅ **CORTEX AI + Analytics**: Use Cortex AI models with historical problem data from SNOW toolkit for trend identification.

### Process Improvement Agent
✅ **: Use Cortex AI to analyze process efficiency and recommend improvements.

### Request Approval Agent
✅ **CORTEX WORKDAY TOOLKIT + SNOW**: Combine Cortex Workday toolkit for org hierarchy with SNOW toolkit for approval workflows.

### Request Classification Agent
✅ **CORTEX AI + NLP Models**: Use Cortex inference models (111 available) with classification prompts. Reference existing agents for ticket classification.

### Request Creation Agent
✅ **CORTEX SNOW TOOLKIT + ChatNow**: Use Cortex SNOW Agent Toolkit to create tickets programmatically. Enhance with ChatNow conversational interface.

### Request Escalation Agent
✅ **CORTEX SNOW TOOLKIT + Business Rules**: Use Cortex SNOW toolkit for ticket updates with SLA monitoring and escalation logic.

### Request Knowledge Agent
✅ **AI RESEARCHER (AiR) + ServiceNow KB**: Leverage AiR research capabilities with ServiceNow knowledge base integration.

### Request Priority Agent
✅ **CORTEX AI Decision Engine**: Use Cortex inference models with priority decision logic. Similar to existing triage agents in Cortex.

### Request Routing Agent
✅ **CORTEX SNOW TOOLKIT + ServiceNow Assignment Rules**: Leverage Cortex SNOW toolkit for ticket updates combined with ServiceNow assignment group logic.

### Request Status Agent
✅ **CORTEX SNOW TOOLKIT**: Direct integration - Cortex SNOW Agent Toolkit already retrieves ticket status and comments.

### SLA Monitoring Agent
✅ **CORTEX SNOW TOOLKIT + SLA Analytics**: Use SNOW toolkit for real-time SLA monitoring and breach alerts.

### SRE Runbook Agent
✅ **: Combine Cortex AI for runbook recommendations with TEA automated execution.

### Security Compliance Agent
✅ **: Adapt compliance agent with security tool integrations.

### Self-Service Portal Agent
✅ **ELIZA + ChatNow + Knowledge Base**: Adapt Eliza (Lilly's Personal Assistant) architecture with ServiceNow knowledge integration via Cortex SNOW toolkit.

### Sentiment Analysis Agent
✅ **CORTEX AI + NLP Models**: Use Cortex NLP models for ticket sentiment analysis and escalation triggers.

### Site Reliability Agent
✅ **: Use Cortex AI for SLO/SLA monitoring and proactive reliability recommendations.

### Virtual Agent Orchestrator
✅ **: Use AI Think Tank architecture for multi-agent orchestration and coordination.

### Workaround Management Agent
✅ **CORTEX SNOW TOOLKIT + Knowledge Base**: Use SNOW toolkit for workaround documentation and distribution via knowledge base.

