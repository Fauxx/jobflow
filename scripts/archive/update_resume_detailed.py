import json

with open('/home/zett/RiderProjects/jobflow/src/resume.json', 'r') as f:
    data = json.load(f)

for proj in data.get('master_profile', {}).get('projects', []):
    if 'Fire Monitoring' in proj['title']:
        if 'Workload Identity Federation' not in proj['detailed_context']:
            proj['detailed_context'] += " Advanced security implemented via passwordless Zero-Trust pipelines using Workload Identity Federation (WIF). Database migrations executed via automated Flyway Kubernetes Jobs. Observability as Code implemented with Grafana Alloy and version-controlled dashboard JSONs. Multi-cloud deployment successfully orchestrated across Google Kubernetes Engine (GKE), Azure (AKS), and DigitalOcean (DOKS)."
    
    elif 'Jobflow' in proj['title']:
        if 'persistent browser profiles' not in proj['detailed_context']:
            proj['detailed_context'] += " Playwright automation utilizes persistent browser profiles to gracefully bypass anti-bot mechanisms. Architecture fully containerized via Docker and docker-compose with custom pre-boot initialization scripts."

with open('/home/zett/RiderProjects/jobflow/src/resume.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Updated Detailed Context successfully!")
