#!/usr/bin/env python3
"""
Map Lilly Service Management AI Agents to specific Cortex capabilities
"""

import json
import re
from datetime import datetime

# Read the AI Agents Backlog file
print("📖 Reading Lilly Service Management AI Agents Backlog...")
with open('Lilly_Service_Management_AI_Agents_Backlog.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Read Cortex agents from pagination data
print("📖 Reading Cortex agents from pagination data...")
with open('../Web Crawler/cortex.lilly.com_crawl/pagination_data.json', 'r', encoding='utf-8') as f:
    cortex_data = json.load(f)

cortex_agents = cortex_data['https://cortex.lilly.com/spe/landing-zone/agents?filter=shared']
print(f"✅ Loaded {len(cortex_agents)} Cortex agents")

# Key Cortex capabilities
cortex_toolkits = {
    'cortex-snow-prd': 'ServiceNow integration - retrieve status, comments, create tickets',
    'cortex-jira-prd': 'JIRA integration - retrieve ticket status, post comments',
    'cortex-workday-prd': 'Employee data, org structures, reporting hierarchies',
    'cortex-web-search-prd': 'Web search using Bing API',
    'cortex-web-scraper-prd': 'HTML content extraction and scraping',
}

# Key known agents from Cortex
key_agents = {
    'AI Researcher (AiR)': 'Research with Quick Chat or Deep Research modes',
    'AiR Planning Agent': 'Planning research tasks guided by user input',
    'AiR Research Report Agent': 'Deep research generating comprehensive reports',
    'AI Think Tank': 'Multi-AI group chat for diverse perspectives',
    'Eliza': "Lilly's Personal Assistant",
    'Ethics & Compliance Chat': 'Policy and procedures knowledge worker',
}

def extract_agents_from_markdown(content):
    """Extract agent entries from markdown file"""
    agents = []

    # Split by agent headers (### with numbers)
    sections = re.split(r'\n### \d+\.', content)

    for section in sections[1:]:  # Skip first section (before first agent)
        lines = section.strip().split('\n')
        if not lines:
            continue

        # First line is the agent name
        agent_name = lines[0].strip()

        # Find description
        description = ""
        in_description = False
        for line in lines:
            if line.startswith('**Description:**'):
                in_description = True
                description = line.replace('**Description:**', '').strip()
            elif in_description and line.strip() and not line.startswith('**'):
                description += " " + line.strip()
            elif in_description and line.startswith('**'):
                break

        agents.append({
            'name': agent_name,
            'description': description,
            'full_section': '\n'.join(lines)
        })

    return agents

def search_cortex_agents(query_terms):
    """Search Cortex agents by keywords"""
    results = []
    query_lower = [term.lower() for term in query_terms]

    for agent in cortex_agents:
        title = agent['content']['title'].lower()
        desc = agent['content'].get('description', '').lower()

        # Check if any query term matches
        for term in query_lower:
            if term in title or term in desc:
                results.append({
                    'title': agent['content']['title'],
                    'description': agent['content'].get('description', '')
                })
                break

    return results

def map_agent_to_capabilities(agent_name, agent_description):
    """Map an agent to specific Cortex capabilities"""
    capabilities = []

    name_lower = agent_name.lower()
    desc_lower = agent_description.lower()
    combined = name_lower + " " + desc_lower

    # Check for ServiceNow toolkit needs
    if any(term in combined for term in ['incident', 'ticket', 'request', 'servicenow', 'snow', 'change', 'problem']):
        capabilities.append("✅ **CORTEX SNOW TOOLKIT**: ServiceNow integration for ticket management, status retrieval, and automated updates")

    # Check for JIRA integration
    if any(term in combined for term in ['jira', 'development', 'devops', 'software']):
        capabilities.append("✅ **CORTEX JIRA TOOLKIT**: JIRA integration for development ticket tracking and updates")

    # Check for employee/org data needs
    if any(term in combined for term in ['employee', 'user', 'assignment', 'routing', 'workload', 'org', 'manager']):
        capabilities.append("✅ **CORTEX WORKDAY TOOLKIT**: Employee data, org structures, and reporting hierarchies for intelligent routing")

    # Check for research/knowledge needs
    if any(term in combined for term in ['knowledge', 'research', 'investigation', 'analysis', 'documentation', 'report']):
        capabilities.append("✅ **AI RESEARCHER (AiR)**: Use Quick Chat for fast searches or Deep Research for comprehensive analysis with citations")

    # Check for communication needs
    if any(term in combined for term in ['communication', 'notification', 'email', 'teams', 'chat', 'message']):
        capabilities.append("✅ **ELIZA + Communication Integration**: Adapt Eliza (Lilly's Personal Assistant) for automated notifications via Teams/Email")

    # Check for compliance needs
    if any(term in combined for term in ['compliance', 'policy', 'audit', 'governance', 'security']):
        capabilities.append("✅ **ETHICS & COMPLIANCE CHAT AGENT**: Policy and procedures knowledge worker for compliance monitoring")

    # Check for multi-perspective analysis
    if any(term in combined for term in ['major incident', 'complex', 'review', 'collaboration', 'multiple perspective']):
        capabilities.append("✅ **AI THINK TANK**: Multi-AI group chat for diverse perspectives on complex issues")

    # Check for trend/analytics needs
    if any(term in combined for term in ['trend', 'pattern', 'analytics', 'metric', 'dashboard', 'kpi']):
        capabilities.append("✅ **CORTEX AI MODELS**: 111 inference models available for pattern recognition, classification, and predictive analytics")

    # Check for automation needs
    if any(term in combined for term in ['automation', 'remediation', 'auto', 'orchestration', 'workflow']):
        capabilities.append("✅ **TEA AUTOMATION + CORTEX**: Integrate Cortex AI decision logic with TEA (Technology Enabling Automation) library for automated execution")

    # Check for monitoring/event needs
    if any(term in combined for term in ['monitoring', 'event', 'alert', 'observability', 'performance']):
        capabilities.append("✅ **CORTEX + MONITORING TOOLS**: Build Cortex agent with Splunk/Dynatrace/Prometheus API integrations for event correlation")

    # Search for specific matching Cortex agents
    search_terms = []
    if 'incident' in combined:
        search_terms.extend(['incident', 'ticket', 'ITR'])
    if 'knowledge' in combined:
        search_terms.extend(['knowledge', 'KB', 'search'])
    if 'chat' in combined or 'conversation' in combined:
        search_terms.extend(['chat', 'eliza', 'assistant'])
    if 'risk' in combined:
        search_terms.extend(['risk', 'assessment'])
    if 'device' in combined:
        search_terms.extend(['device', 'endpoint', 'nexthink'])

    if search_terms:
        matching_agents = search_cortex_agents(search_terms)
        if matching_agents:
            agent_list = [f"{a['title']}" for a in matching_agents[:3]]  # Top 3 matches
            if agent_list:
                capabilities.append(f"✅ **EXISTING CORTEX AGENTS**: {', '.join(agent_list)}")

    # If no specific capabilities found, provide general guidance
    if not capabilities:
        capabilities.append("✅ **CORTEX AI PLATFORM**: Leverage Cortex's 111 inference models, 13 embedding models, and 1,091 shared prompts to build custom agent")

    return capabilities

# Extract all agents from markdown
print("\n📝 Extracting agents from markdown...")
agents = extract_agents_from_markdown(content)
print(f"✅ Found {len(agents)} agents")

# Create mapping for each agent
print("\n🔍 Mapping agents to Cortex capabilities...")
agent_mappings = {}
for agent in agents:
    capabilities = map_agent_to_capabilities(agent['name'], agent['description'])
    agent_mappings[agent['name']] = capabilities
    print(f"   Mapped: {agent['name']}")

# Now update the markdown file
print("\n📝 Updating markdown file with specific Cortex capabilities...")
with open('Lilly_Service_Management_AI_Agents_Backlog.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

updated_lines = []
current_agent = None
skip_existing_cortex = False

for i, line in enumerate(lines):
    # Check if we're at an agent header
    if re.match(r'^### \d+\.', line):
        current_agent = line.replace('###', '').strip()
        current_agent = re.sub(r'^\d+\.\s*', '', current_agent)  # Remove number prefix
        updated_lines.append(line)
        skip_existing_cortex = False
        continue

    # Skip existing Cortex Capabilities section
    if line.startswith('**Existing Cortex Capabilities:**'):
        skip_existing_cortex = True
        continue

    if skip_existing_cortex:
        # Skip lines until we hit another ** section or new agent
        if line.startswith('**') and 'Cortex' not in line:
            skip_existing_cortex = False
        elif line.startswith('###') or line.startswith('---'):
            skip_existing_cortex = False
        else:
            continue

    # Add Cortex capabilities after Implementation Recommendation
    if current_agent and line.startswith('**Implementation Recommendation:**'):
        updated_lines.append(line)

        # Find the matching agent in our mappings (handle slight name variations)
        matched_capabilities = None
        for mapped_name, capabilities in agent_mappings.items():
            if current_agent in mapped_name or mapped_name in current_agent:
                matched_capabilities = capabilities
                break

        if matched_capabilities:
            updated_lines.append(f"\n**Existing Cortex Capabilities:**  \n")
            for capability in matched_capabilities:
                updated_lines.append(f"{capability}  \n")
            updated_lines.append("\n")
        else:
            updated_lines.append(f"\n**Existing Cortex Capabilities:**  \n")
            updated_lines.append(f"✅ **CORTEX AI PLATFORM**: Leverage Cortex's 111 inference models, 13 embedding models, and 1,091 shared prompts for custom agent development  \n\n")

        current_agent = None
        continue

    updated_lines.append(line)

# Write updated file
print("💾 Writing updated markdown file...")
with open('Lilly_Service_Management_AI_Agents_Backlog.md', 'w', encoding='utf-8') as f:
    f.writelines(updated_lines)

print("✅ File updated successfully!")

# Generate summary report
print("\n" + "="*80)
print("CORTEX CAPABILITY MAPPING SUMMARY")
print("="*80)
print(f"Total Agents Analyzed: {len(agents)}")
print(f"Total Cortex Agents Available: {len(cortex_agents)}")
print(f"Cortex Toolkits: {len(cortex_toolkits)}")
print("\nKey Capabilities Mapped:")
print("  - ServiceNow Integration (SNOW Toolkit)")
print("  - JIRA Integration (JIRA Toolkit)")
print("  - Employee Data (Workday Toolkit)")
print("  - AI Research (AiR agent)")
print("  - Communication (Eliza)")
print("  - Compliance (Ethics & Compliance Chat)")
print("  - Analytics (111 AI inference models)")
print("  - Automation (TEA + Cortex)")
print("="*80)
print("\n✅ COMPLETE - Markdown file updated with specific Cortex capabilities!")
