import json

with open('/home/zett/RiderProjects/jobflow/src/resume.json', 'r') as f:
    data = json.load(f)

# Update Fire Monitoring System
for proj in data['projects']:
    if proj['title'] == 'IoT-Based Fire Monitoring & Cloud-Native Analytics Platform':
        # Add high-value bullets from the MD file
        new_bullets = [
            "Demonstrated multi-cloud adaptability by successfully provisioning and deploying the entire Kubernetes architecture across Google Kubernetes Engine (GKE), Azure Kubernetes Service (AKS), and DigitalOcean Kubernetes (DOKS).",
            "Architected a passwordless, Zero-Trust CI/CD pipeline by replacing long-lived JSON service account keys with ephemeral OIDC Workload Identity Federation (WIF) for GitHub Actions and Cloud SQL.",
            "Automated PostgreSQL schema evolution by deploying Flyway database migrations as ephemeral Kubernetes Jobs, ensuring zero-downtime schema upgrades prior to API pod initialization.",
            "Deployed Grafana Alloy as an OpenTelemetry collector pipeline and implemented 'Observability as Code' by Git-versioning Grafana dashboards for rapid disaster recovery.",
            "Secured internal observability infrastructure by configuring NGINX as a reverse proxy, safely exposing the Grafana dashboard via custom subdomains without opening direct public ports."
        ]
        # Insert them strategically (avoiding exact duplicates)
        proj['bullets'] = [b for b in proj['bullets'] if 'multi-cloud Kubernetes infrastructure' not in b]
        proj['bullets'] = new_bullets + proj['bullets']

# Update Jobflow
for proj in data['projects']:
    if proj['title'] == 'Jobflow: AI-Powered ATS Resume Builder & Job Pipeline':
        new_bullets = [
            "Automated complex job description extraction and DOM parsing by integrating Playwright, utilizing persistent browser profiles to gracefully handle session caching and bypass anti-bot challenges.",
            "Containerized the full-stack FastAPI application using Docker and docker-compose, scripting automated pre-boot checks (wait_and_migrate.sh) to ensure database schemas are applied before server initialization."
        ]
        proj['bullets'].extend(new_bullets)

# Update AI Job Email Agent
for proj in data['projects']:
    if proj['title'] == 'Autonomous AI Job Email Agent':
        new_bullets = [
            "Integrated Google's Gemini LLM into an automated workflow, engineering precise JSON-enforced prompts to parse unstructured email bodies and extract critical job application metadata."
        ]
        proj['bullets'] = new_bullets + proj['bullets']

with open('/home/zett/RiderProjects/jobflow/src/resume.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Updated JSON successfully!")
