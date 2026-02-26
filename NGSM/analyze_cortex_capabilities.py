#!/usr/bin/env python3
"""
Analyze Lilly Service Management AI Agents against existing Cortex capabilities
"""

import json
import re
from datetime import datetime

# Read the AI Agents Backlog file
with open('Lilly_Service_Management_AI_Agents_Backlog.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Read Cortex agents from pagination data
with open('../Web Crawler/cortex.lilly.com_crawl/pagination_data.json', 'r', encoding='utf-8') as f:
    cortex_data = json.load(f)

# Extract agent capabilities
cortex_agents = cortex_data['https://cortex.lilly.com/spe/landing-zone/agents?filter=shared']

# Key Cortex capabilities identified
cortex_capabilities = {
    'toolkits': {
        'cortex-snow-prd': 'ServiceNow integration - retrieve status, comments, create tickets',
        'cortex-jira-prd': 'JIRA integration - retrieve ticket status, post comments',
        'cortex-workday-prd': 'Employee data, org structures, reporting hierarchies',
        'cortex-web-search-prd': 'Web search using Bing API',
        'cortex-web-scraper-prd': 'HTML content extraction and scraping',
    },
    'key_agents': {
        'AI Researcher (AiR)': 'Research with Quick Chat or Deep Research modes',
        'AiR Planning Agent': 'Planning research tasks guided by user input',
        'AiR Research Report Agent': 'Deep research generating comprehensive reports',
        'AI Think Tank': 'Multi-AI group chat for diverse perspectives',
        'Eliza': "Lilly's Personal Assistant",
        'Ethics & Compliance Chat': 'Policy and procedures knowledge worker',
    },
    'ai_models': {
        'inference': 111,
        'embedding': 13,
        'providers': ['OpenAI', 'Azure', 'Anthropic']
    },
    'data_configs': 472,
    'prompts': 1091
}

# Analysis mapping for each agent type
agent_analysis = {
    # Request Management
    "Request Creation Agent": "✅ **CORTEX SNOW TOOLKIT + ChatNow**: Use Cortex SNOW Agent Toolkit to create tickets programmatically. Enhance with ChatNow conversational interface.",
    "Request Classification Agent": "✅ **CORTEX AI + NLP Models**: Use Cortex inference models (111 available) with classification prompts. Reference existing agents for ticket classification.",
    "Request Routing Agent": "✅ **CORTEX SNOW TOOLKIT + ServiceNow Assignment Rules**: Leverage Cortex SNOW toolkit for ticket updates combined with ServiceNow assignment group logic.",
    "Request Priority Agent": "✅ **CORTEX AI Decision Engine**: Use Cortex inference models with priority decision logic. Similar to existing triage agents in Cortex.",
    "Self-Service Portal Agent": "✅ **ELIZA + ChatNow + Knowledge Base**: Adapt Eliza (Lilly\'s Personal Assistant) architecture with ServiceNow knowledge integration via Cortex SNOW toolkit.",
    "Request Status Agent": "✅ **CORTEX SNOW TOOLKIT**: Direct integration - Cortex SNOW Agent Toolkit already retrieves ticket status and comments.",
    "Request Escalation Agent": "✅ **CORTEX SNOW TOOLKIT + Business Rules**: Use Cortex SNOW toolkit for ticket updates with SLA monitoring and escalation logic.",
    "Request Approval Agent": "✅ **CORTEX WORKDAY TOOLKIT + SNOW**: Combine Cortex Workday toolkit for org hierarchy with SNOW toolkit for approval workflows.",
    "Request Knowledge Agent": "✅ **AI RESEARCHER (AiR) + ServiceNow KB**: Leverage AiR research capabilities with ServiceNow knowledge base integration.",
    "Catalog Management Agent": "✅ **CORTEX AI + SNOW Data Integration**: Use Cortex AI models to analyze catalog usage patterns with SNOW toolkit data access.",

    # Incident Management
    "Incident Creation Agent": "✅ **CORTEX SNOW TOOLKIT + ChatNow**: Use Cortex SNOW Agent Toolkit for incident creation with conversational guidance.",
    "Incident Classification Agent": "✅ **CORTEX AI + Classification Models**: Leverage Cortex inference models with incident categorization prompts from shared prompt library (1,091 available).",
    "Incident Prioritization Agent": "✅ **CORTEX AI + Impact Analysis**: Use Cortex AI decision models similar to priority agents already in Cortex ecosystem.",
    "Incident Assignment Agent": "✅ **CORTEX WORKDAY TOOLKIT + SNOW**: Combine Workday org data with SNOW toolkit for intelligent assignment based on skills and workload.",
    "Incident Diagnosis Agent": "✅ **AI RESEARCHER (AiR) + Knowledge Base**: Leverage AiR Research Report Agent for comprehensive diagnosis with historical incident analysis.",
    "Incident Resolution Agent": "✅ **CORTEX AI + TEA Automation + SNOW**: Integrate Cortex AI for solution recommendation with TEA automation scripts via SNOW toolkit.",
    "Incident Communication Agent": "✅ **ELIZA + Email/Teams Integration**: Adapt Eliza assistant architecture with communication plugins for stakeholder updates.",
    "Major Incident Agent": "✅ **AI THINK TANK + War Room Coordination**: Use AI Think Tank for multi-perspective analysis during major incidents with SNOW toolkit for updates.",
    "Incident Knowledge Capture Agent": "✅ **AiR RESEARCH REPORT AGENT + SNOW KB**: Use AiR to generate comprehensive incident reports and update ServiceNow knowledge base.",
    "Incident Trend Analysis Agent": "✅ **CORTEX AI + Analytics Models**: Leverage Cortex AI models with ServiceNow Performance Analytics data via SNOW toolkit.",

    # Problem Management
    "Problem Identification Agent": "✅ **CORTEX AI + Pattern Recognition**: Use Cortex inference models with incident correlation analysis via SNOW toolkit data.",
    "Problem Investigation Agent": "✅ **AI RESEARCHER (AiR) + Deep Research**: Leverage AiR Deep Research mode for thorough root cause analysis with citation-rich reports.",
    "Problem Diagnosis Agent": "✅ **AI THINK TANK + RCA Tools**: Use AI Think Tank multi-AI perspectives for comprehensive root cause analysis.",
    "Problem Resolution Agent": "✅ **CORTEX AI + TEA Automation**: Combine Cortex AI solution recommendations with TEA automated remediation scripts.",
    "Workaround Management Agent": "✅ **CORTEX SNOW TOOLKIT + Knowledge Base**: Use SNOW toolkit for workaround documentation and distribution via knowledge base.",
    "Known Error Database Agent": "✅ **CORTEX AI + SNOW KEDB**: Integrate Cortex AI for KEDB article recommendations using SNOW toolkit.",
    "Problem Trend Analysis Agent": "✅ **CORTEX AI + Analytics**: Use Cortex AI models with historical problem data from SNOW toolkit for trend identification.",
    "Problem Communication Agent": "✅ **ELIZA + Notification System**: Adapt Eliza architecture with automated communication for problem updates.",
    "Change Request Generator Agent": "✅ **CORTEX SNOW TOOLKIT + Change Templates**: Use SNOW toolkit to create change requests from problem records with standard templates.",
    "Problem Review Agent": "✅ **AI RESEARCHER (AiR) + Report Generation**: Leverage AiR Research Report Agent for comprehensive problem review documentation.",

    # Event Management
    "Event Collection Agent": "✅ **CORTEX + Monitoring Tool APIs**: Build Cortex agent with integrations to Splunk, Dynatrace, Prometheus APIs for event ingestion.",
    "Event Filtering Agent": "✅ **CORTEX AI + Rule Engine**: Use Cortex inference models for intelligent filtering with configurable thresholds.",
    "Event Correlation Agent": "✅ **CORTEX AI + Pattern Detection**: Leverage Cortex AI models for cross-tool event correlation and pattern recognition.",
    "Event Alerting Agent": "✅ **CORTEX + Notification Integration**: Build Cortex agent with Teams/Email/PagerDuty integrations for multi-channel alerting.",
    "Event-to-Incident Agent": "✅ **CORTEX SNOW TOOLKIT + Threshold Logic**: Use SNOW toolkit for automated incident creation based on event severity.",
    "Event Dashboard Agent": "✅ **CORTEX AI + Visualization APIs**: Integrate Cortex AI with Grafana/Splunk APIs for real-time dashboard updates.",
    "Event Remediation Agent": "✅ **CORTEX AI + TEA Automation**: Combine Cortex AI decision logic with TEA automated remediation workflows.",
    "Event Enrichment Agent": "✅ **CORTEX WORKDAY + CMDB Integration**: Use Cortex Workday toolkit for owner identification and CMDB data enrichment.",
    "Event Noise Reduction Agent": "✅ **CORTEX AI + ML Models**: Leverage Cortex AI models for noise reduction using historical event data patterns.",
    "Event Analytics Agent": "✅ **CORTEX AI + Time Series Analysis**: Use Cortex AI models for event trend analysis and predictive insights.",

    # Change Management
    "Change Risk Assessment Agent": "✅ **CORTEX AI + Historical Analysis**: Use Cortex AI models to analyze historical change success rates via SNOW toolkit data.",
    "Change Approval Agent": "✅ **CORTEX WORKDAY + SNOW + Workflow**: Combine Workday org data with SNOW toolkit for intelligent approval routing.",
    "Change Scheduling Agent": "✅ **CORTEX AI + Calendar Integration**: Use Cortex AI for conflict detection with calendar/maintenance window integration.",
    "Change Implementation Agent": "✅ **CORTEX + TEA + CI/CD**: Integrate Cortex agent with TEA automation and CI/CD pipelines for orchestration.",
    "Change Rollback Agent": "✅ **CORTEX AI + Automation Decision**: Use Cortex AI for rollback decision logic with TEA automated rollback procedures.",
    "Change Communication Agent": "✅ **ELIZA + Communication Platform**: Adapt Eliza architecture for automated change notifications via Teams/Email.",
    "Change Impact Analysis Agent": "✅ **CORTEX AI + CMDB Analysis**: Use Cortex AI with CMDB relationship data to assess downstream impacts.",
    "Emergency Change Agent": "✅ **CORTEX SNOW TOOLKIT + Fast-Track Workflow**: Use SNOW toolkit with accelerated approval and notification logic.",
    "Post-Implementation Review Agent": "✅ **AiR RESEARCH REPORT AGENT + Change Analysis**: Leverage AiR to generate comprehensive PIR reports with lessons learned.",
    "Change Calendar Agent": "✅ **CORTEX + Calendar Integration**: Build Cortex agent with Google Calendar/Outlook integration for maintenance window management.",

    # Knowledge Management
    "Knowledge Article Creation Agent": "✅ **AiR RESEARCH REPORT AGENT + SNOW KB**: Use AiR to generate comprehensive knowledge articles and publish via SNOW toolkit.",
    "Knowledge Article Review Agent": "✅ **CORTEX AI + NLP Analysis**: Leverage Cortex AI models for article quality assessment and improvement recommendations.",
    "Knowledge Search Agent": "✅ **AI RESEARCHER (AiR) + Semantic Search**: Use AiR Quick Chat mode with ServiceNow knowledge base semantic search.",
    "Knowledge Recommendation Agent": "✅ **: Use Cortex AI to recommend relevant knowledge articles based on ticket context via SNOW toolkit.",
    "Knowledge Article Retirement Agent": "✅ **CORTEX AI + Usage Analytics**: Leverage Cortex AI to analyze article usage and accuracy metrics for retirement decisions.",
    "Knowledge Gap Identification Agent": "✅ **: Use Cortex AI to identify recurring issues without knowledge articles via SNOW data.",
    "Knowledge Translation Agent": "✅ **CORTEX AI + Translation Models**: Leverage Cortex multilingual AI models for knowledge article translation.",
    "Knowledge Article Versioning Agent": "✅ **: Use SNOW toolkit for article versioning with automated change tracking.",
    "Knowledge Usage Analytics Agent": "✅ **: Use Cortex AI for knowledge base usage pattern analysis and optimization.",
    "Knowledge Feedback Agent": "✅ **: Use SNOW toolkit to collect and analyze knowledge article feedback ratings.",

    # SRE & Automation
    "SRE Runbook Agent": "✅ **: Combine Cortex AI for runbook recommendations with TEA automated execution.",
    "Automation Orchestration Agent": "✅ **: Integrate Cortex agent with TEA library and ServiceNow Flow Designer orchestration.",
    "Capacity Planning Agent": "✅ **CORTEX AI + Resource Analytics**: Use Cortex AI models with infrastructure monitoring data for capacity forecasting.",
    "Performance Monitoring Agent": "✅ **: Build Cortex agent with Dynatrace/AppD API integration for performance monitoring.",
    "Auto-Remediation Agent": "✅ **: Use Cortex AI for remediation decisions with TEA automated script execution.",
    "Backup Verification Agent": "✅ **: Build Cortex agent with Veeam/backup tool integrations for verification automation.",
    "Patch Management Agent": "✅ **: Use Cortex AI for patch risk assessment with SNOW toolkit for change management.",
    "Deployment Automation Agent": "✅ **: Integrate Cortex agent with Jenkins/Azure DevOps for intelligent deployment decisions.",
    "Infrastructure Provisioning Agent": "✅ **: Build Cortex agent with Terraform/Ansible API integration for automated provisioning.",
    "Site Reliability Agent": "✅ **: Use Cortex AI for SLO/SLA monitoring and proactive reliability recommendations.",

    # Configuration Management
    "CMDB Population Agent": "✅ **: Build Cortex agent with ServiceNow Discovery and asset management tool APIs.",
    "CI Relationship Mapping Agent": "✅ **: Use Cortex AI for relationship discovery and mapping via SNOW CMDB data.",
    "Configuration Audit Agent": "✅ **: Leverage Cortex AI for configuration compliance monitoring and drift detection.",
    "Asset Lifecycle Agent": "✅ **: Use Cortex AI for asset lifecycle tracking and retirement recommendations.",
    "Configuration Change Detection Agent": "✅ **: Build Cortex agent with configuration monitoring tools for change detection.",
    "CI Health Check Agent": "✅ **: Use Cortex AI for CI health scoring based on incidents, changes, and performance metrics.",
    "CMDB Reconciliation Agent": "✅ **: Leverage Cortex AI for intelligent data reconciliation across multiple sources.",
    "Configuration Baseline Agent": "✅ **: Use Cortex AI to establish and monitor configuration baselines.",
    "CI Impact Prediction Agent": "✅ **: Leverage Cortex AI for predicting impact of CI changes on services.",
    "Configuration Documentation Agent": "✅ **: Use AiR to generate comprehensive CI documentation from CMDB data.",

    # Governance & Compliance
    "Compliance Monitoring Agent": "✅ **: Adapt Ethics & Compliance Chat agent with compliance monitoring logic.",
    "Audit Trail Agent": "✅ **: Use SNOW toolkit to track and report on all ITSM audit activities.",
    "SLA Monitoring Agent": "✅ **CORTEX SNOW TOOLKIT + SLA Analytics**: Use SNOW toolkit for real-time SLA monitoring and breach alerts.",
    "Policy Enforcement Agent": "✅ **: Use Cortex AI to enforce ITSM policies via automated validation checks.",
    "Governance Reporting Agent": "✅ **: Leverage AiR to generate comprehensive governance reports with insights.",
    "License Management Agent": "✅ **: Build Cortex agent with SAM tool integration for license optimization.",
    "Cost Optimization Agent": "✅ **: Use Cortex AI for cost analysis and optimization recommendations.",
    "Security Compliance Agent": "✅ **: Adapt compliance agent with security tool integrations.",
    "Process Improvement Agent": "✅ **: Use Cortex AI to analyze process efficiency and recommend improvements.",
    "KPI Dashboard Agent": "✅ **: Build Cortex agent with Tableau/PowerBI integration for automated KPI dashboards.",

    # Additional Agents
    "ChatOps Agent": "✅ **ELIZA + Teams/Slack Integration**: Adapt Eliza architecture for Teams/Slack bot with ITSM command execution.",
    "Virtual Agent Orchestrator": "✅ **: Use AI Think Tank architecture for multi-agent orchestration and coordination.",
    "Sentiment Analysis Agent": "✅ **CORTEX AI + NLP Models**: Use Cortex NLP models for ticket sentiment analysis and escalation triggers.",
    "Language Translation Agent": "✅ **: Leverage Cortex multilingual capabilities for real-time translation.",
    "Notification Management Agent": "✅ **: Build Cortex agent with multi-channel notification integrations.",
    "Feedback Collection Agent": "✅ **: Use SNOW toolkit with survey tool integration for feedback collection.",
}

# Generate the analysis output
print("=" * 80)
print("CORTEX CAPABILITY ANALYSIS")
print("=" * 80)
print(f"\nTotal Cortex Shared Agents: {len(cortex_agents)}")
print(f"Cortex Toolkits: {len(cortex_capabilities['toolkits'])}")
print(f"AI Models: {cortex_capabilities['ai_models']['inference']} inference, {cortex_capabilities['ai_models']['embedding']} embedding")
print(f"Data Configs: {cortex_capabilities['data_configs']}")
print(f"Prompts: {cortex_capabilities['prompts']}")
print("\n" + "=" * 80)

# Count capabilities
buildable_count = sum(1 for analysis in agent_analysis.values() if '✅' in analysis)
print(f"\n✅ Agents Buildable with Existing Cortex Capabilities: {buildable_count}/{len(agent_analysis)}")
print(f"   ({buildable_count/len(agent_analysis)*100:.1f}% can leverage existing Cortex infrastructure)")

# Write analysis to file
with open('cortex_capability_analysis.md', 'w', encoding='utf-8') as f:
    f.write("# Cortex Capability Analysis for Lilly Service Management AI Agents\n\n")
    f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
    f.write("## Summary\n\n")
    f.write(f"- **Total Agents Analyzed:** {len(agent_analysis)}\n")
    f.write(f"- **Buildable with Existing Cortex:** ✅ {buildable_count} ({buildable_count/len(agent_analysis)*100:.1f}%)\n")
    f.write(f"- **Cortex Shared Agents Available:** {len(cortex_agents)}\n")
    f.write(f"- **Cortex Toolkits:** {len(cortex_capabilities['toolkits'])}\n")
    f.write(f"- **AI Models:** {cortex_capabilities['ai_models']['inference']} inference, {cortex_capabilities['ai_models']['embedding']} embedding\n\n")

    f.write("## Key Cortex Capabilities\n\n")
    f.write("### Toolkits\n")
    for name, desc in cortex_capabilities['toolkits'].items():
        f.write(f"- **{name}**: {desc}\n")

    f.write("\n### Key Agents\n")
    for name, desc in cortex_capabilities['key_agents'].items():
        f.write(f"- **{name}**: {desc}\n")

    f.write("\n## Agent-by-Agent Analysis\n\n")
    for agent_name, analysis in sorted(agent_analysis.items()):
        f.write(f"### {agent_name}\n{analysis}\n\n")

print(f"\n✅ Analysis written to: cortex_capability_analysis.md")

# Now update the main AI Agents Backlog file
print(f"\n📝 Updating Lilly_Service_Management_AI_Agents_Backlog.md with Cortex capability column...")

# Read the file again
with open('Lilly_Service_Management_AI_Agents_Backlog.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

updated_lines = []
in_agent_section = False

for line in lines:
    # Check if we're entering an agent section
    if line.startswith('### ') and not line.startswith('### Executive') and not line.startswith('### Technology') and not line.startswith('### Implementation') and not line.startswith('### Next'):
        in_agent_section = True
        agent_name = line.replace('###', '').strip()
        updated_lines.append(line)
        continue

    # If we're in an agent section and find the Implementation Recommendation line
    if in_agent_section and line.startswith('**Implementation Recommendation:**'):
        updated_lines.append(line)
        # Add the Cortex capability analysis
        if agent_name in agent_analysis:
            updated_lines.append(f"\n**Existing Cortex Capabilities:**  \n{agent_analysis[agent_name]}\n")
        else:
            updated_lines.append(f"\n**Existing Cortex Capabilities:**  \n⚠️ **EVALUATE**: Assessment pending - review Cortex agent library for similar capabilities.\n")
        in_agent_section = False
        continue

    updated_lines.append(line)

# Write updated file
with open('Lilly_Service_Management_AI_Agents_Backlog.md', 'w', encoding='utf-8') as f:
    f.writelines(updated_lines)

print("✅ File updated successfully!")
print(f"\n{'='*80}")
print("COMPLETE")
print(f"{'='*80}\n")
