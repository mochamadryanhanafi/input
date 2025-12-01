from datetime import datetime
from app.core.database import get_db

class StatsService:
    async def get_dashboard_data(self): # Saya rename biar lebih umum
        database = await get_db()
        
        # 1. Ambil Data Agregat
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date_published"},
                        "month": {"$month": "$date_published"}
                    },
                    "count": {"$sum": 1}
                }
            }
        ]
        results = await database["news"].aggregate(pipeline).to_list(length=None)
        data_map = {(r["_id"]["year"], r["_id"]["month"]): r["count"] for r in results}
        
        timeline = []
        first_empty_date = None # Variabel penampung tanggal kosong pertama

        # 2. Loop Timeline & Deteksi Slot Kosong
        for year in range(2014, 2025):
            months = []
            for month in range(1, 13):
                if year == 2014 and month < 10:
                    status = "disabled"
                elif year == 2024 and month > 10:
                    status = "disabled"
                else:
                    count = data_map.get((year, month), 0)
                    status = "filled" if count > 0 else "empty"
                    
                    if status == "empty" and first_empty_date is None:
                        first_empty_date = f"{year}-{month:02d}-01"

                months.append({
                    "name": datetime(year, month, 1).strftime("%b"),
                    "count": data_map.get((year, month), 0),
                    "status": status
                })
            timeline.append({"year": year, "months": months})
            
        if first_empty_date is None:
            first_empty_date = datetime.now().strftime("%Y-%m-%d")
            
        return timeline, first_empty_date