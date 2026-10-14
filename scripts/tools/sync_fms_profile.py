import json
import uuid
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.database import SessionLocal
from src.models.profile import UserProfile, ProfileProject, ProfileBullet, ProfileSkill

print("=== 1. Updating jobflow/src/resume.json ===")
with open('/home/zett/RiderProjects/jobflow/src/resume.json', 'r') as f:
    resume_data = json.load(f)

# 1.1 Update skills in resume.json
skills_map = {
    "Cloud Infrastructure & IaC": "Google Cloud Platform (GCP), Google Kubernetes Engine (GKE), Google Artifact Registry (GAR), GCP Workload Identity Federation (WIF), DigitalOcean (DOKS, Spaces, VPC, DNS), Azure (AKS, VNet, NSG, Key Vault, ACR, Blob Storage), Azure OIDC / Entra ID, Cloud Adoption Framework (CAF), Terraform, Helm, Infrastructure as Code (IaC)",
    "Container Orchestration & Linux": "Docker, Kubernetes (K8s), Kustomize (v5), Multi-stage Docker Builds, Pod Security Standards (PSS), Non-Root Containers, Podman, Linux (Fedora/Ubuntu), Kind (Local K8s Development)",
    "Observability & Monitoring": "Prometheus, Grafana, Loki, Grafana Alloy, cAdvisor (Resource Scrape Tuning), Node Exporter, Cloud SQL Proxy Sidecars, postgres-exporter, Full-Stack Observability",
    "Frontend & UI": "React 19, TypeScript, Vite, TailwindCSS, MapLibre GL (WebGL 3D Maps), Jinja2 Templates, EJS Templates, HTMX, Chart.js, Leaflet.js, WeasyPrint (PDF Generation)",
    "Databases & Messaging": "PostgreSQL, Google Cloud SQL, connect-pg-simple (Session Persistence), InfluxDB 2.x (Flux Queries), Redis, SQLAlchemy ORM, Entity Framework Core, Flyway Migrations, Alembic Migrations, MQTT (Mosquitto)"
}

for s in resume_data.get('skills', []):
    if s['category'] in skills_map:
        s['items'] = skills_map[s['category']]

# 1.2 Update Fire Monitoring System project in resume.json
new_fms_bullets = [
    "Demonstrated multi-cloud adaptability by successfully provisioning and deploying the entire Kubernetes architecture across Google Kubernetes Engine (GKE), Azure Kubernetes Service (AKS), and DigitalOcean Kubernetes (DOKS).",
    "Architected a passwordless, Zero-Trust CI/CD pipeline by replacing long-lived JSON service account keys with ephemeral OIDC Workload Identity Federation (WIF) for GitHub Actions and Cloud SQL.",
    "Containerized microservice architecture using multi-stage Dockerfiles, isolating C/C++ compilation toolchains to builder stages and enforcing unprivileged non-root execution (UID 1000) aligned with Kubernetes Pod Security Standards.",
    "Refactored monolithic Kubernetes manifests into decoupled, domain-driven Kustomize layers (apps, data, networking, observability), standardizing modern Kustomize v5 declarative syntax.",
    "Orchestrated Cloud SQL Auth Proxy sidecar containers across application and migration workloads, eliminating startup race conditions and blocking initContainers.",
    "Automated PostgreSQL schema evolution by deploying Flyway database migrations as ephemeral Kubernetes Jobs with ArgoCD Sync Wave Hooks (argocd.argoproj.io/hook: Sync) for zero-downtime rollouts.",
    "Stabilized cAdvisor metric collection to essential subsystems (cpu, memory, network, oom_event) and adjusted Prometheus scrape timeouts to 20s, eliminating node OOM thrashing.",
    "Engineered dynamic in-cluster namespace discovery in the API observability layer, automatically querying Prometheus metrics and Loki logs across dev and prod namespaces without hardcoded hostnames.",
    "Implemented container stream alias mapping in Loki log aggregation, unifying Cloud SQL Auth Proxy sidecar logs with PostgreSQL application queries over configurable 24-hour lookback windows.",
    "Eliminated connect-pg-simple session startup race conditions by standardizing pre-verified PostgreSQL session tables and enforcing explicit asynchronous session persistence (req.session.save()) on login.",
    "Redesigned /api/latest and /api/devices endpoints to join active telemetry with registered sensor nodes, preserving historical last-known telemetry during disconnections to prevent false 0.0 readings.",
    "Architected a high-performance, real-time command center dashboard in React and TypeScript, leveraging MapLibre GL and WebGL for interactive 3D spatial telemetry visualization.",
    "Restructured modal views into a unified CommandCenterModal and System Diagnostics suite with segmented navigation controls and live queried telemetry from PostgreSQL, Prometheus, and InfluxDB without placeholders.",
    "Eliminated WebGL canvas crashes and UI projection thrashing under rapid MQTT telemetry ingestion through React component memoization (React.memo) and frame throttling.",
    "Engineered real-time anomaly indicators featuring animated pulsing markers and auto-framing bounding boxes over active sensor clusters in the National Capital Region (NCR).",
    "Engineered a full-lifecycle Developer CLI via an advanced GNU Makefile supporting 5 SDLC environments, automated pre-flight port conflict detection (lsof/nc), and explicit kubectl context validation."
]

for proj in resume_data.get('projects', []):
    if 'Fire Monitoring' in proj['title']:
        proj['tech_stack'] = "Google Cloud Platform (GCP / GKE), Google Artifact Registry, Azure AKS, DigitalOcean DOKS, Terraform, Docker (Multi-Stage), Kubernetes, Helm, Kustomize, ArgoCD, Cloud SQL Proxy, PostgreSQL, Flyway, InfluxDB 2.x, Redis, MQTT (Mosquitto), Telegraf, Python, Pandas, Node.js, Express.js, React 19, TypeScript, Vite, Tailwind CSS, MapLibre GL, WebGL, Prometheus, Grafana, Loki, Grafana Alloy, cAdvisor, Node Exporter, Trivy, Cloudflare Tunnels, Calico"
        proj['bullets'] = new_fms_bullets

# 1.3 Update detailed context in master_profile
detailed_fms_context = (
    "Production-grade cloud-native platform integrating IoT fire sensors with real-time analytics. "
    "Multi-cloud deployment across Google Kubernetes Engine (GKE), DigitalOcean Kubernetes Service (DOKS), and Azure AKS (East Asia region). "
    "Infrastructure provisioned via 4-layer sequential Terraform pipeline: 00-bootstrap (Resource Groups, Storage), 01-infra (VNet, NSG, ACR, Key Vault, AKS cluster with Calico), 02-platform (Ingress-Nginx, cert-manager, CSI Secrets), 03-argocd (ArgoCD, Cloudflare Tunnel, App-of-Apps). "
    "Zero-Trust security implemented via Workload Identity Federation (WIF) for passwordless GitHub Actions CI/CD and Cloud SQL database authentication. "
    "Database migrations executed via automated Flyway Kubernetes Jobs with ArgoCD Sync Wave Hooks (argocd.argoproj.io/hook: Sync) for zero-downtime schema evolution. "
    "Multi-stage Docker refactoring isolating C/C++ compilation toolchains (gcc, g++, make) to builder stages for Node.js (bcrypt) and Python ETL (wheel builders), standardizing non-root runtime users (UID 1000 node:node, simuser) under Kubernetes Pod Security Standards. "
    "Restructured monolithic Kubernetes base manifests into decoupled, domain-driven Kustomize layers (apps, data, networking, observability) using modern v5 syntax (labels, patches). "
    "Integrated Cloud SQL Auth Proxy sidecar containers across API, ETL, and Flyway workloads, eliminating blocking initContainers and startup races. "
    "Observability stack tuned with Prometheus, Grafana, Loki, Grafana Alloy (DaemonSet log collector), Node Exporter, and cAdvisor; filtered cAdvisor metrics to essential subsystems (cpu, memory, network, oom_event) and increased scrape timeouts to 20s to eliminate node OOM thrashing. "
    "Implemented dynamic in-cluster namespace discovery in the API observability layer to query Prometheus and Loki across dev and prod namespaces dynamically without hardcoded hostnames. "
    "Implemented Loki container stream alias mapping to unify Cloud SQL Auth Proxy sidecar logs with PostgreSQL application queries over configurable 24-hour lookback windows. "
    "Eliminated connect-pg-simple session startup race conditions through pre-verified PostgreSQL session tables and explicit req.session.save() transactional guarantees on login. "
    "Authored Flyway migrations V16–V19 decoupling coordinates into device_registry and seeding accurate Metro Manila (NCR) coordinates. "
    "Updated API endpoints (/api/latest, /api/devices) with resilient fallbacks preserving last-known telemetry during node disconnections to prevent false 0.0 readings. "
    "Modernized frontend with React 19, TypeScript, Vite, Tailwind CSS, and MapLibre GL/WebGL 3D maps, optimizing WebGL rendering via React.memo component memoization to prevent UI frame thrashing during high-frequency MQTT message bursts. "
    "Implemented dynamic device heartbeat tracking (online, warning, offline) and unified CommandCenter and System Diagnostics modals with zero mock placeholders, wiring all telemetry live to PostgreSQL, Prometheus, and InfluxDB. "
    "Engineered an advanced 5-stage SDLC Developer CLI in GNU Makefile with automated pre-flight port conflict checks (lsof/nc) and context-guarded kubectl execution."
)

for proj in resume_data.get('master_profile', {}).get('projects', []):
    if 'Fire Monitoring' in proj['title']:
        proj['detailed_context'] = detailed_fms_context

with open('/home/zett/RiderProjects/jobflow/src/resume.json', 'w') as f:
    json.dump(resume_data, f, indent=4)
print("Updated jobflow/src/resume.json successfully!")

print("\n=== 2. Updating Jobflow PostgreSQL Database ===")
db = SessionLocal()
profile = db.query(UserProfile).first()
if not profile:
    print("Error: No profile found in database!")
    exit(1)

# 2.1 Update Skills in DB
for s in profile.skills:
    if s.category in skills_map:
        s.items = skills_map[s.category]
db.commit()
print("Updated skills in database!")

# 2.2 Update Project in DB
fms_project = None
for p in profile.projects:
    if "Fire Monitoring" in p.title:
        fms_project = p
        break

if fms_project:
    fms_project.tech_stack = "Google Cloud Platform (GCP / GKE), Google Artifact Registry, Azure AKS, DigitalOcean DOKS, Terraform, Docker (Multi-Stage), Kubernetes, Helm, Kustomize, ArgoCD, Cloud SQL Proxy, PostgreSQL, Flyway, InfluxDB 2.x, Redis, MQTT (Mosquitto), Telegraf, Python, Pandas, Node.js, Express.js, React 19, TypeScript, Vite, Tailwind CSS, MapLibre GL, WebGL, Prometheus, Grafana, Loki, Grafana Alloy, cAdvisor, Node Exporter, Trivy, Cloudflare Tunnels, Calico"
    fms_project.detailed_context = detailed_fms_context
    db.commit()
    print("Updated FMS project tech_stack and detailed_context in database!")
else:
    print("Warning: FMS project not found in database!")

# 2.3 Verify bullets
bullet_count = db.query(ProfileBullet).filter(ProfileBullet.project_id == fms_project.id).count() if fms_project else 0
print(f"Verified {bullet_count} bullets in database for project '{fms_project.title if fms_project else 'N/A'}'")

db.close()
print("All Jobflow profile configurations successfully synchronized!")
