#!/usr/bin/env python3
"""
Script to add implementation recommendations to AI Agents Backlog
"""

# Recommendations based on agent characteristics
recommendations = {
    # High-impact Request/Incident agents (40-70%)
    "Incident Creation Agent": "**ChatNow + ServiceNow Virtual Agent + Cortex:** Enhance ChatNow's existing conversational interface with Cortex AI decision-making. Use ServiceNow's Now Assist for ITSM to guide users through diagnostic questions. Integrate with knowledge base and historical incident data for self-service resolution suggestions before ticket creation.",

    "Fix Automation Agent": "**TEA Automation Library + Cortex + ServiceNow Event Management:** Leverage TEA's existing automation playbooks and extend with Cortex AI for intelligent remediation selection. Use ServiceNow's Automated Test Framework (ATF) for validation. Integrate with monitoring tools (Splunk, Dynatrace) for event-driven execution.",

    "Change Record Assistant Agent": "**ServiceNow Change Management + Cortex + CMDB:** Use ServiceNow's Change Automation with Cortex AI to analyze CMDB relationships and generate change records. Integrate with architectural diagrams stored in Confluence/SharePoint. Leverage ServiceNow's Impact Analysis for risk assessment.",

    "Request Process Agent": "**ServiceNow Flow Designer + Cortex + Approval Engine:** Build on ServiceNow's native request workflow engine with Cortex AI for intelligent routing. Use ServiceNow's approval engine with AI-enhanced policy decisioning. Integrate with IAM for role-based validation.",

    # Event Management agents (20-40%)
    "Self-Healing Agent": "**ServiceNow Event Management + TEA Playbooks + Cortex:** Create event-driven playbooks in ServiceNow that trigger TEA automations. Use Cortex AI to determine confidence levels for autonomous execution vs. human approval. Integrate with monitoring tools for real-time event processing.",

    "Event Monitoring Agent": "**Splunk/Dynatrace + ServiceNow Event Rules + Cortex:** Use existing Lilly observability stack (Splunk, Dynatrace) as data sources. Build Cortex AI models for signal vs. noise classification. Integrate with ServiceNow Event Management for actionable event creation.",

    "Event Correlation Agent": "**ServiceNow Event Management + Cortex ML:** Leverage ServiceNow's native event correlation rules enhanced with Cortex machine learning models. Train on historical event/incident relationships. Use CMDB topology for relationship-based correlation.",

    "Event Resolution Agent": "**ServiceNow Event Actions + TEA Automations + Cortex:** Configure ServiceNow event actions to trigger TEA automation workflows. Use Cortex for confidence scoring and escalation logic. Integrate with ChatOps (Teams/Slack) for human notifications.",

    "Noise Reduction Agent": "**ServiceNow Event Filters + Cortex ML + Historical Data:** Build Cortex ML models trained on closed events with no action taken. Use ServiceNow's transform maps and event rules for filtering. Implement feedback loops for continuous improvement.",

    # Incident Management agents (15-35%)
    "Incident Routing Agent": "**ServiceNow Assignment Rules + Cortex + Workload Analytics:** Extend ServiceNow's assignment rules with Cortex AI for skills-based routing. Use ServiceNow's Performance Analytics to track resolver workload. Integrate with HR systems for availability data.",

    "Incident Triage Agent": "**ChatNow + ServiceNow Virtual Agent + Knowledge:** Build conversational triage workflow in ChatNow using ServiceNow's Virtual Agent framework. Query ServiceNow Knowledge Base and similar incident history. Use Cortex for dynamic question generation based on symptoms.",

    "Incident Resolver Agent v2": "**ServiceNow Now Assist + Cortex + Enterprise Search:** Enhance existing ServiceNow resolution suggestions with Cortex AI. Integrate with Lilly's enterprise search (Coveo/Elasticsearch) for cross-platform knowledge. Query SharePoint, Confluence, and external vendor knowledge.",

    "Incident Communication Agent": "**ServiceNow Notifications + Cortex NLP + Templates:** Use Cortex NLP to generate contextual communications from incident data. Leverage ServiceNow's notification framework with AI-generated content. Provide sentiment-appropriate language based on incident severity.",

    "Incident Trend Agent": "**ServiceNow Performance Analytics + Cortex ML + Problem Suggestions:** Build ML models in Cortex to identify incident patterns. Use ServiceNow's Performance Analytics dashboards for visualization. Auto-create problem records when thresholds met.",

    "Vendor Ticket Agent": "**ServiceNow REST API + Vendor APIs + Cortex Orchestration:** Build API integrations with vendor ticketing systems (Jira, ServiceDesk). Use Cortex to extract relevant incident details and map to vendor fields. Implement bidirectional updates via webhooks.",

    "Incident Documentation Improvement Agent": "**ServiceNow Quality Gates + Cortex NLP + Workflow:** Analyze work notes and resolution fields using Cortex NLP. Implement ServiceNow business rules to flag incomplete documentation. Build assignment group scorecards for accountability.",

    "Incident Business Risk Translator Agent": "**ServiceNow CMDB + Cortex + Business Service Mapping:** Leverage ServiceNow's Business Service Mapping to link technical CIs to business services. Use Cortex to translate technical impacts into business metrics. Integrate with financial/compliance data.",

    # Knowledge Management agents (15-35%)
    "Knowledge Article Recommendation Agent": "**ServiceNow Knowledge + Cortex NLP + Incident Analysis:** Use Cortex NLP to identify knowledge gaps from incident resolution notes. Analyze ServiceNow Knowledge metrics (views, helpfulness). Auto-create knowledge article drafts from well-documented incidents.",

    "Knowledge Relevance and Retirement Agent": "**ServiceNow Knowledge Analytics + Cortex + Usage Tracking:** Monitor ServiceNow Knowledge usage metrics and incident linkage. Use Cortex to identify outdated content based on incident trends. Flag articles with no usage in 6+ months.",

    "Knowledge Creation Agent": "**ServiceNow Now Assist for Creator + Cortex NLP + Templates:** Use ServiceNow's Now Assist for Knowledge article generation from incident data. Apply Cortex NLP to extract procedures from resolution notes. Integrate with corporate templates and style guides.",

    "Knowledge Revision Agent": "**ServiceNow Knowledge + Cortex + Change Detection:** Monitor incident trends for changes in resolution patterns. Use Cortex to suggest article updates based on new resolution methods. Integrate with external vendor knowledge bases (Microsoft, SAP).",

    "Knowledge Search Agent": "**ServiceNow AI Search + Cortex + Enterprise Search:** Extend ServiceNow's AI Search with Cortex to query multiple knowledge repositories. Integrate with SharePoint, Confluence, Teams, and external sources. Return unified results with source attribution.",

    "Knowledge Health Agent": "**ServiceNow Knowledge OOB Metrics + Cortex Analytics:** Leverage ServiceNow's out-of-box knowledge health reports. Enhance with Cortex predictive analytics for proactive updates. Build dashboards for knowledge owners.",

    "External Intelligence Agent": "**Cortex Web Scraping + Vendor APIs + Caching:** Use Cortex to search vendor knowledge bases, forums, and community sites. Implement caching layer for frequently accessed external content. Ensure compliance with vendor ToS and rate limits.",

    # Problem Management agents (15-30%)
    "Problem Ticket Creation Agent": "**ServiceNow Problem + Cortex Pattern Detection + Incident Clustering:** Build Cortex ML models to identify incident clusters indicating systemic problems. Use ServiceNow workflows to auto-create problem records. Link related incidents automatically via API.",

    "Root Cause Analysis Agent v2.0": "**ServiceNow Problem + Cortex AI + Event/Incident Data:** Enhance existing RCA capabilities with Cortex AI analyzing event timelines, CMDB relationships, and change history. Use 5-Whys methodology with AI-guided questioning. Integrate with log analysis tools.",

    "Known Error Management Agent": "**ServiceNow Problem + Knowledge + Cortex Matching:** Create known error records from resolved problems. Use Cortex to match incoming incidents to known errors. Auto-suggest workarounds to resolvers via ServiceNow UI.",

    "RCA Validator Agent": "**ServiceNow Quality Gates + Cortex NLP + Completeness Checks:** Analyze RCA documentation using Cortex NLP for quality and completeness. Check for required elements (timeline, root cause, corrective actions). Flag incomplete RCAs before problem closure.",

    "Problem to Known Error Agent": "**JIRA/ALM API + ServiceNow Problem + Cortex Sync:** Build API integration between development defect tracking (JIRA, HP ALM) and ServiceNow. Auto-create known error records for deferred defects. Maintain bidirectional sync for status updates.",

    # Change Management agents (20-40%)
    "Change Collision Detector Agent": "**ServiceNow Change + CMDB + OOB Collision Detection:** Leverage ServiceNow's out-of-box change collision detection. Enhance with CMDB dependency analysis. Use Cortex to calculate risk amplification scores for overlapping changes.",

    # Automation & SRE agents (20-50%)
    "Automation Analysis Agent": "**TEA Logs + Cortex Failure Analysis + ServiceNow Incidents:** Monitor TEA automation execution logs. Use Cortex to classify failure types and determine self-healing vs. manual intervention. Auto-create incidents to automation team with context.",

    "Automation Development Agent": "**ServiceNow Flow Designer + IntegrationHub + Cortex Code Generation:** Use ServiceNow's Flow Designer and IntegrationHub for building automations. Experiment with Cortex AI for generating automation logic from natural language requirements. Leverage existing TEA patterns.",

    "Runbook Generator Agent": "**ServiceNow Knowledge + Cortex NLP + Incident History:** Analyze resolved incidents to extract common procedures. Use Cortex NLP to generate step-by-step runbooks. Store as ServiceNow Knowledge articles with proper categorization.",

    "Validation Agent": "**ServiceNow ATF + Cortex + Monitoring Integration:** Use ServiceNow's Automated Test Framework for pre/post-change validation. Integrate with monitoring tools for health checks. Use Cortex for anomaly detection in validation results.",

    # Request Management agents (20-45%)
    "Request Creation Agent": "**ChatNow + ServiceNow Catalog + Cortex NLU:** Build conversational catalog interface in ChatNow. Use Cortex Natural Language Understanding to map employee requests to catalog items. Provide form pre-fill with extracted data.",

    "Service Catalog Update Agent": "**ServiceNow Catalog Builder + Now Assist for Creator + Approval Workflow:** Use ServiceNow's Catalog Builder with AI assistance. Implement approval workflows for catalog changes. Integrate with Cortex for intelligent field suggestions based on usage patterns.",

    # Resource & SLA Management (15-35%)
    "Resource Alignment Agent": "**ServiceNow Performance Analytics + Cortex + HR Data:** Analyze ticket volumes, resolution times, and workload distribution using ServiceNow analytics. Use Cortex to identify bottlenecks. Integrate with HR systems for skills inventory.",

    "SLA Sentinel Agent": "**ServiceNow SLA Engine + Cortex Predictive Analytics + OOB Alerts:** Leverage ServiceNow's OOB SLA breach alerting. Enhance with Cortex predictive models for early warning. Auto-escalate to managers before breach.",

    # Observability & Monitoring (15-35%)
    "Observability Agent": "**Splunk/Dynatrace + ServiceNow + Cortex Correlation:** Integrate multiple observability tools (Splunk, Dynatrace, Prometheus) data streams. Use Cortex to correlate failure signals across platforms. Present unified view in ServiceNow.",

    # Major Incident Management (15-30%)
    "Propose Major Incident": "**ServiceNow Major Incident + Cortex Decision Engine + Knowledge:** Use Cortex to analyze incident severity, impact, and historical patterns. Query ServiceNow Knowledge for major incident criteria. Suggest (not auto-declare) major incident status with justification.",

    "IRT Notification and Scheduler Agent": "**Everbridge API + ServiceNow + Teams Calendar:** Integrate Everbridge API for IRT notifications. Use ServiceNow workflows to trigger based on major incident declaration. Auto-schedule Teams meetings with IRT roster.",

    "Major Incident Impact Agent": "**ServiceNow Work Notes + Cortex NLP + Incident Analysis:** Use Cortex NLP to analyze incident notes, chat logs, and impact statements. Calculate business impact score. Recommend IAT/IRT based on severity threshold.",

    # Configuration Management (10-25%)
    "CMDB Query Agent": "**ServiceNow CMDB + Cortex NLU + ChatNow:** Build conversational interface to ServiceNow CMDB using ChatNow. Use Cortex NLU to parse natural language queries into CMDB filters. Return results in human-readable format.",

    "CI Update Agent": "**ServiceNow CMDB + Approval Workflow + Audit Logging:** Build conversational CI update interface with strict authorization checks. Implement approval workflows for sensitive changes. Maintain comprehensive audit logs for compliance.",

    "Service Mapping Agent": "**ServiceNow Service Mapping OOB + Discovery + IntegrationHub:** Leverage ServiceNow's out-of-box Service Mapping capabilities. Enhance with additional discovery patterns. Use IntegrationHub for API-based discovery.",

    # Governance & Compliance (15-30%)
    "Process Governance Agent": "**ServiceNow OOB Reports + Cortex Compliance Checking + Dashboards:** Use ServiceNow's out-of-box governance reports. Build Cortex models to detect process deviations. Create executive dashboards for compliance metrics.",

    "Compliance Monitoring Agent": "**ServiceNow Business Rules + Cortex Policy Engine + OOB Audit:** Implement ServiceNow business rules for policy enforcement. Use Cortex to interpret complex compliance requirements. Leverage ServiceNow's OOB audit capabilities.",

    "Audit Prep Agent": "**ServiceNow Reports + Cortex Document Analysis + Export Utilities:** Build automated audit reports from ServiceNow data. Use Cortex to validate completeness. Generate export packages with evidence and documentation.",

    # UX & Voice (15-30%)
    "Manage ticket with voice AI agent": "**ServiceNow OOB Voice Agent + Telephony Integration + Speech-to-Text:** Leverage ServiceNow's out-of-box Voice AI Agent. Integrate with Lilly's telephony systems. Use Azure Speech Services for transcription.",

    "Request Status Agent": "**ServiceNow OOB AI Agent + ChatNow + SMS/Email:** Use ServiceNow's out-of-box status checking agent. Integrate with ChatNow for conversational status updates. Add SMS/email notification capabilities.",

    # End User Device Management (15-35%)
    "Proactive End User Device Resolution Agent": "**Nexthink + ServiceNow + Automated Remediation:** Leverage Nexthink's device monitoring and remediation capabilities. Trigger ServiceNow workflows when thresholds breached. Use Nexthink's Act feature for automated fixes.",

    "Chat Resolution Agent": "**ChatNow + Nexthink Remote Actions + ServiceNow:** Build ChatNow interface to Nexthink remote actions. Allow users to describe symptoms conversationally. Trigger Nexthink remediations with user consent.",

    # CSI & Reporting (15-30%)
    "Continuous Improvement Agent": "**ServiceNow Performance Analytics + Cortex Trend Analysis + Recommendations:** Analyze ServiceNow metrics across all ITSM processes. Use Cortex to identify improvement opportunities. Generate actionable recommendations with ROI estimates.",

    "Executive Insights Agent": "**ServiceNow OOB Dashboards + Cortex Business Translation + OKR Integration:** Leverage ServiceNow's out-of-box executive dashboards. Use Cortex to translate technical metrics to business KPIs. Integrate with corporate OKR tracking.",

    # Miscellaneous (15-30%)
    "Ops Investigation Agent": "**ServiceNow + Splunk + Cortex Log Analysis:** Query ServiceNow for related records. Pull logs from Splunk/Dynatrace. Use Cortex to analyze logs and create timeline. Present unified investigation view.",

    "Service Desk Triage Agent": "**ServiceNow Virtual Agent + ChatNow + Cortex Routing Logic:** Build intelligent triage workflow in ServiceNow Virtual Agent. Use Cortex to determine Tier 1 vs. escalation. Integrate with ChatNow for real-time assistance.",

    "Testing Agent": "**ServiceNow ATF + Cortex Test Generation + CI/CD:** Use ServiceNow's Automated Test Framework. Explore Cortex for generating test cases from requirements. Integrate with CI/CD pipelines for automated testing.",

    "DevOps Agent": "**ServiceNow + JIRA + Azure DevOps + Cortex Pipeline Orchestration:** Integrate ServiceNow with development tools (JIRA, Azure DevOps, GitHub). Use Cortex for pipeline orchestration and deployment decisioning. Implement automated rollback capabilities.",

    "Release Forecasting Agent": "**ServiceNow Release Management + Cortex Predictive Analytics + Historical Data:** Analyze historical release data in ServiceNow. Build Cortex predictive models for risk and readiness. Generate forecasts with confidence intervals.",

    # Work Planning & Analysis (15-30%)
    "Analyze and improve services": "**ServiceNow OOB Agentic Workflow + Performance Analytics + Customer Feedback:** Leverage ServiceNow's out-of-box workflow for service analysis. Integrate with survey platforms. Use Performance Analytics for trend identification.",

    "Generate my work plan": "**ServiceNow Workload Optimization + OOB Agentic Workflow + Calendar Integration:** Use ServiceNow's out-of-box work plan generation. Integrate with Outlook/Teams calendar. Apply AI for intelligent prioritization.",

    "Identify ways to improve service": "**ServiceNow OOB Agentic Workflow + Survey Analysis + Cortex Sentiment:** Leverage ServiceNow's out-of-box survey analysis workflow. Use Cortex for sentiment analysis and trend detection.",

    "Web research and recommendation AI agent": "**ServiceNow OOB AI Agent + Cortex Web Search + Vendor Knowledge:** Use ServiceNow's out-of-box web research agent. Enhance with Cortex for intelligent search and summarization. Include vendor knowledge bases.",

    # Additional specific agents
    "Metadata Intelligence Agent": "**ServiceNow OOB Tagging + Cortex NLP + Auto-classification:** Leverage ServiceNow's out-of-box metadata capabilities. Use Cortex NLP for auto-tagging based on content analysis. Implement continuous retagging as content evolves.",

    "Threshold Breach Monitor Agent": "**ServiceNow Event Management + Monitoring Tools + Cortex Threshold Analysis:** Integrate monitoring tools (Dynatrace, Splunk) with ServiceNow. Use Cortex to analyze threshold patterns and suggest optimal thresholds.",

    "Outage Opening/Closing Agent": "**ServiceNow Event Playbooks + Outage Records + Cortex Impact Analysis:** Create event-driven playbooks that auto-create outage records. Use Cortex to determine outage impact. Auto-close related incidents when outage is planned.",

    "Service Design Readiness Agent": "**ServiceNow CMDB + Runbooks + Cortex Readiness Checklist:** Query ServiceNow CMDB for monitoring configuration. Check for runbook existence in Knowledge. Use Cortex to validate completeness against SRE checklist.",

    "Incident Alert Supression Agent": "**ServiceNow Event Rules + Cortex Pattern Detection + Auto-Closure Analysis:** Analyze incidents auto-closed in <30 seconds. Use Cortex to identify patterns. Implement event suppression rules to prevent future incident creation.",

    "Incident Risk Scoring Agent": "**ServiceNow + Cortex Risk Modeling + CMDB:** Build Cortex models for multifactor risk scoring. Use CMDB for blast radius calculation. Integrate sentiment analysis from work notes.",

    "Auto PIR (Post Incident Review) Agent": "**ServiceNow Problem + Cortex Timeline Analysis + Template Generation:** Use Cortex to analyze incident timeline and actions. Generate PIR draft using templates. Identify patterns and improvement opportunities.",

    "Document Assistant Agent": "**ServiceNow + Cortex NLP + Template Library:** Use Cortex NLP to assist with problem documentation. Provide templates and prompts. Auto-extract relevant details from linked incidents.",

    "Fix Validation Assistant Agent": "**ServiceNow + Monitoring Tools + Cortex Validation Logic:** Monitor incident recurrence after problem resolution. Use Cortex to determine if fix was effective. Alert if similar incidents still occurring.",

    "Engineering Fixes Agent": "**Cortex Code Analysis + JIRA + ServiceNow Problem:** Analyze problem data and linked incidents. Use Cortex to suggest potential engineering fixes. Create JIRA tickets for development team.",

    "Known Error To Automation Agent": "**ServiceNow Known Errors + TEA + Cortex Automation Potential:** Analyze known error workarounds for automation potential. Use Cortex to score automation feasibility. Auto-create automation backlog items.",

    "Reoccurring Problem Fixer Agent": "**ServiceNow Problem + Cortex Root Cause Chain Analysis + Multi-layer Detection:** Use Cortex to analyze problem recurrence patterns. Identify multi-layered root causes. Suggest comprehensive fix strategies.",

    "Communications Writer Agent": "**ServiceNow Notifications + Cortex NLP Generation + Stakeholder Lists:** Use Cortex to generate stakeholder communications from problem data. Identify impacted users from incident list. Auto-send via ServiceNow notifications.",

    "Artifact Preservation Suggestion Agent": "**ServiceNow + Log Management + Cortex Evidence Analysis:** Analyze problem investigations to identify critical evidence types. Use Cortex to suggest what logs/data to preserve. Auto-configure retention policies.",

    "RCA Task Generation Agent": "**ServiceNow Problem Tasks + Cortex RCA Framework + Work Breakdown:** Use Cortex to break down RCA into investigative tasks. Apply 5-Whys or Fishbone methodologies. Assign tasks to appropriate teams.",

    "Problem Opportunity Monitoring Agent": "**ServiceNow Problem Metrics + Cortex Stall Detection + Manager Alerts:** Monitor problem age and activity. Use Cortex to identify stalled problems. Auto-alert service management office (SMO).",

    "Incident Trends Monitoring Agent (Problem Creation)": "**ServiceNow Analytics + Cortex Pattern Detection + Proactive Problem Creation:** Analyze incident trends by CI and category. Use Cortex to detect emerging patterns. Auto-suggest proactive problem creation.",

    "SMO Analysis Agent": "**ServiceNow Performance Analytics + Cortex + Executive Reports:** Analyze operational metrics across all ITSM processes. Use Cortex to identify patterns and opportunities. Generate executive-level insights.",

    "Development Fix Recommend Agent": "**ServiceNow Incident + Cortex Code Analysis + Development Tools:** Analyze technical incidents for development patterns. Use Cortex to suggest code fixes. Link to JIRA/Azure DevOps for tracking.",

    "Outage Agent": "**ServiceNow Event Monitoring + Cortex Impact Correlation + Outage Declaration:** Monitor event patterns and incident volumes. Use Cortex to correlate signals indicating outage. Suggest (not auto-declare) outage status.",

    "Large Issue and Events Monitoring Agent": "**ServiceNow Event Aggregation + Cortex Impact Analysis + Manager Notification:** Monitor event volumes across CMDB CIs. Use Cortex to detect large-scale issues. Auto-notify incident process owner and managers.",

    "Instant Closed Events Monitoring Agent": "**ServiceNow Event Analytics + Cortex Pattern Detection + Improvement Suggestions:** Track events closed instantly without automation. Use Cortex to identify automation opportunities. Report to service owners.",

    "Incident Patterns Monitoring Agent": "**ServiceNow Incident Analytics + Cortex Pattern Matching + Event Opportunities:** Analyze incident patterns for preventable issues. Use Cortex to suggest event monitoring opportunities. Notify service owners with recommendations.",

    "Events Without Actions Monitoring Agent": "**ServiceNow Event Analysis + Cortex Action Classification + Service Owner Alerts:** Track events with no remediation actions. Use Cortex to classify why no action taken. Suggest improvements to event playbooks.",

    "Event Candidates for Monitoring Agent": "**ServiceNow Incidents + Cortex Proactive Monitoring + Monitoring Tool Integration:** Analyze manually-reported incidents. Use Cortex to identify monitoring gaps. Suggest new monitoring configurations to service owners.",

    "Vendor Ticket Agent": "**ServiceNow + Vendor APIs + Cortex Data Mapping:** Build API integrations with vendor ticketing systems. Use Cortex to map ServiceNow fields to vendor formats. Implement bidirectional sync for updates.",

    "Artifact Preservation Suggestion Agent": "**Log Management + ServiceNow + Cortex Evidence Requirements:** Analyze past problems for evidence gaps. Use Cortex to suggest artifact preservation policies. Auto-configure log retention.",
}

# Add default recommendation for any missing agents
default_recommendation = "**Evaluate with Cortex AI + ServiceNow Platform:** Assess this agent opportunity using Cortex AI for decision logic and ServiceNow as the integration platform. Consider building MVP with existing ServiceNow workflows, Performance Analytics, and Flow Designer. Integrate with relevant data sources (CMDB, monitoring tools, logs) as needed. Pilot with limited scope before broad deployment."

print(f"Prepared {len(recommendations)} recommendations")
print("\nSample recommendations:")
for i, (name, rec) in enumerate(list(recommendations.items())[:3]):
    print(f"\n{i+1}. {name}:")
    print(f"   {rec[:150]}...")
