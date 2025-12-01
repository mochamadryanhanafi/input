from datetime import datetime
from app.core.database import get_db

class StatsService:
    async def get_dashboard_data(self):
        database = await get_db()
        
        category_pipeline = [
            {"$group": {"_id": "$portal", "count": {"$sum": 1}}}
        ]
        cat_results = await database["news"].aggregate(category_pipeline).to_list(None)
        
        category_stats = {r["_id"]: r["count"] for r in cat_results}
        total_news = sum(category_stats.values())

        timeline_pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date_published"},
                        "month": {"$month": "$date_published"},
                        "portal": "$portal" 
                    },
                    "count": {"$sum": 1}
                }
            }
        ]
        raw_results = await database["news"].aggregate(timeline_pipeline).to_list(None)
        
        month_details = {}
        month_totals = {}
        
        for r in raw_results:
            y, m, p = r["_id"]["year"], r["_id"]["month"], r["_id"].get("portal", "Other")
            key = (y, m)
            
            month_totals[key] = month_totals.get(key, 0) + r["count"]
            
            if key not in month_details:
                month_details[key] = []
            month_details[key].append(f"{p}: {r['count']}")
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_count = await database["news"].count_documents({
            "created_at": {"$gte": today_start}
        })

        timeline = []
        first_empty_date = None
        
        for year in range(2014, 2025):
            months = []
            for month in range(1, 13):
                # Logic Range Oct 2014 - Oct 2024
                if (year == 2014 and month < 10) or (year == 2024 and month > 10):
                    status = "disabled"
                    details = ""
                    count = 0
                else:
                    count = month_totals.get((year, month), 0)
                    details = "<br>".join(month_details.get((year, month), ["No Data"]))
                    status = "filled" if count > 0 else "empty"
                    
                    if status == "empty" and first_empty_date is None:
                        first_empty_date = f"{year}-{month:02d}-01"

                months.append({
                    "name": datetime(year, month, 1).strftime("%b"),
                    "count": count,
                    "status": status,
                    "details": details # Data detail untuk tooltip
                })
            timeline.append({"year": year, "months": months})
            
        if first_empty_date is None:
            first_empty_date = datetime.now().strftime("%Y-%m-%d")

            
        return {
            "timeline": timeline,
            "suggested_date": first_empty_date,
            "total_news": total_news,
            "category_stats": category_stats,
            "today_count": today_count
        }