from fastapi import FastAPI

from handlers import get_actions, startup_event, shutdown_event
from models import EntityResponse


app = FastAPI(title="Cow Actions API")

app.add_api_route("/actions", get_actions, methods=["POST"], response_model=list[EntityResponse])

app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)