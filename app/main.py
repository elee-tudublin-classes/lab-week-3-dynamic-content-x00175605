# import dependencies
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import httpx
from contextlib import asynccontextmanager
from starlette.config import Config

# Load environment variables from .env
config = Config(".env")

# create app instance
app = FastAPI()

# set location for templates
templates = Jinja2Templates(directory="app/view_templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.requests_client = httpx.AsyncClient()
    yield
    await app.requests_client.aclose()

app = FastAPI(lifespan=lifespan)

# handle http get requests for the site root /
# return the index.html page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    serverTime: datetime = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    return templates.TemplateResponse("index.html", {"request": request, "serverTime": serverTime})

@app.get("/params", response_class=HTMLResponse)
async def params(request: Request, name: str | None = ""):
    return templates.TemplateResponse("params.html", {"request": request, "name": name})

@app.get("/advice", response_class=HTMLResponse)
async def advice(request: Request):
    requests_client = request.app.requests_client
    response = await requests_client.get(config("ADVICE_URL"))
    return templates.TemplateResponse("advice.html", {"request": request, "data": response.json()})

@app.get("/apod", response_class=HTMLResponse)
async def apod(request: Request, name: str | None = ""):
    return templates.TemplateResponse("apod.html", {"request": request, "name": name})

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)
