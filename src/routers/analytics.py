from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.job import Job
from src.models.application import Application
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta, timezone
from collections import defaultdict

router = APIRouter(prefix="/analytics", tags=["analytics"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def analytics_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(db)

    # ── 1. Top-Level KPIs ─────────────────────────────────────────────────────
    total_jobs_scraped = db.query(func.count(Job.id)).scalar() or 0

    all_apps = db.query(Application).filter(Application.user_id == user.id).all()

    total_applied  = sum(1 for a in all_apps if a.status == "APPLIED")
    total_approved = sum(1 for a in all_apps if a.status == "APPROVED")
    total_skipped  = sum(1 for a in all_apps if a.status == "SKIPPED")
    total_new      = max(total_jobs_scraped - total_applied - total_approved - total_skipped, 0)

    # Sub-status breakdown (only APPLIED apps have meaningful sub_statuses)
    applied_apps = [a for a in all_apps if a.status == "APPLIED"]
    sub_status_counts = defaultdict(int)
    for a in applied_apps:
        sub_status_counts[a.sub_status or "APPLIED"] += 1

    screening_count = sub_status_counts.get("SCREENING", 0)
    interview_count = sub_status_counts.get("INTERVIEW", 0)
    offer_count     = sub_status_counts.get("OFFER", 0)
    rejected_count  = sub_status_counts.get("REJECTED", 0)
    just_applied    = sub_status_counts.get("APPLIED", 0)

    # Response rate: apps that progressed past plain APPLIED
    progressed    = screening_count + interview_count + offer_count
    response_rate = round((progressed / total_applied * 100), 1) if total_applied > 0 else 0
    offer_rate    = round((offer_count / total_applied * 100), 1) if total_applied > 0 else 0

    # ── 2. Applications Over Time (last 30 days) ──────────────────────────────
    now_utc         = datetime.now(timezone.utc)
    thirty_days_ago = now_utc - timedelta(days=30)

    day_labels = []
    day_counts = []
    day_map    = defaultdict(int)

    for a in all_apps:
        if a.date_applied and a.date_applied >= thirty_days_ago:
            day_key = a.date_applied.strftime("%b %d")
            day_map[day_key] += 1

    for i in range(30):
        day   = thirty_days_ago + timedelta(days=i)
        label = day.strftime("%b %d")
        day_labels.append(label)
        day_counts.append(day_map.get(label, 0))

    # ── 3. Source Breakdown ────────────────────────────────────────────────────
    source_rows = (
        db.query(Job.source, func.count(Job.id))
        .group_by(Job.source)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    source_labels = [r[0] or "Unknown" for r in source_rows]
    source_counts = [r[1] for r in source_rows]

    # ── 4. Employment Type Breakdown ──────────────────────────────────────────
    etype_rows = (
        db.query(Job.employment_type, func.count(Job.id))
        .group_by(Job.employment_type)
        .order_by(func.count(Job.id).desc())
        .limit(6)
        .all()
    )
    etype_labels = [r[0] or "Unspecified" for r in etype_rows]
    etype_counts = [r[1] for r in etype_rows]

    # ── 5. Top Companies (applied to) ─────────────────────────────────────────
    company_rows = (
        db.query(Job.company, func.count(Application.id))
        .join(Application, Application.job_id == Job.id)
        .filter(Application.user_id == user.id, Application.status == "APPLIED")
        .group_by(Job.company)
        .order_by(func.count(Application.id).desc())
        .limit(8)
        .all()
    )
    top_companies = [{"company": r[0], "count": r[1]} for r in company_rows]

    # ── 6. Avg Time-to-Progress ────────────────────────────────────────────────
    time_to_screen    = []
    time_to_interview = []
    for a in applied_apps:
        if a.date_applied and a.date_screening:
            d = (a.date_screening - a.date_applied).days
            if d >= 0:
                time_to_screen.append(d)
        if a.date_applied and a.date_interview:
            d = (a.date_interview - a.date_applied).days
            if d >= 0:
                time_to_interview.append(d)

    avg_time_to_screen    = round(sum(time_to_screen)    / len(time_to_screen),    1) if time_to_screen    else None
    avg_time_to_interview = round(sum(time_to_interview) / len(time_to_interview), 1) if time_to_interview else None

    # ── 7. Recent Activity Feed ────────────────────────────────────────────────
    recent_apps = (
        db.query(Application, Job)
        .join(Job, Application.job_id == Job.id)
        .filter(Application.user_id == user.id)
        .order_by(Application.updated_at.desc().nulls_last(), Application.created_at.desc())
        .limit(10)
        .all()
    )
    activity_feed = []
    for app, job in recent_apps:
        ts = app.updated_at or app.created_at
        activity_feed.append({
            "job_id":     job.id,
            "title":      job.title,
            "company":    job.company,
            "status":     app.status,
            "sub_status": app.sub_status,
            "ts":         ts.strftime("%b %d, %Y") if ts else "—",
        })

    context = {
        "request": request,
        # KPIs
        "total_jobs_scraped":   total_jobs_scraped,
        "total_new":            total_new,
        "total_approved":       total_approved,
        "total_applied":        total_applied,
        "total_skipped":        total_skipped,
        "just_applied":         just_applied,
        "screening_count":      screening_count,
        "interview_count":      interview_count,
        "offer_count":          offer_count,
        "rejected_count":       rejected_count,
        "response_rate":        response_rate,
        "offer_rate":           offer_rate,
        # Charts
        "day_labels":           day_labels,
        "day_counts":           day_counts,
        "source_labels":        source_labels,
        "source_counts":        source_counts,
        "etype_labels":         etype_labels,
        "etype_counts":         etype_counts,
        # Tables
        "top_companies":        top_companies,
        "activity_feed":        activity_feed,
        # Time metrics
        "avg_time_to_screen":   avg_time_to_screen,
        "avg_time_to_interview":avg_time_to_interview,
        # For sidebar compat
        "counts": {
            "NEW":     total_new,
            "APPROVED":total_approved,
            "APPLIED": total_applied,
            "SKIPPED": total_skipped,
        },
        "current_status": None,
        "resume": {"name": ""},
    }

    return templates.TemplateResponse(request=request, name="analytics.html", context=context)
