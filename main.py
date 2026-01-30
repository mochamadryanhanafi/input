import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.database import connect_db, close_db
from app.routes import web

load_dotenv()

app = FastAPI(title="DailyVerse Feeder")

app.add_event_handler("startup", connect_db)
app.add_event_handler("shutdown", close_db)

app.include_router(web.router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3123))
    uvicorn.run(app, host="0.0.0.0", port=port)