from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from app.core.database import get_db
from app.services.stats import StatsService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def index(request: Request):
    service = StatsService()
    data = await service.get_dashboard_data() 
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "timeline": data["timeline"],
        "suggested_date": data["suggested_date"],
        "total_news": data["total_news"],
        "category_stats": data["category_stats"],
        "today_count": data["today_count"]
    })

@router.post("/submit")
async def submit_news(
    request: Request,
    portal: str = Form(...),
    date_published: str = Form(...),
    url: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    sentiment: str = Form(None),
    summary: str = Form(None)
):
    database = await get_db()
    
    payload = {
        "portal": portal,
        "date_published": datetime.strptime(date_published, "%Y-%m-%d"),
        "url": url,
        "title": title,
        "content": content,
        "sentiment_label": sentiment,
        "summary_ground_truth": summary,
        "created_at": datetime.utcnow()
    }
    
    await database["news"].insert_one(payload)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)