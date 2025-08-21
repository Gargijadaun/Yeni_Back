import json
import os
import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route to open Admin.html directly
@app.get("/admin")
def get_admin():
    return FileResponse("static/Admin.html")
# Configure CORS
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:8000",
    "https://yeniback-production.up.railway.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:8000", "http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# File path for JSON storage
DATA_FILE = "data.json"

# Initialize JSON file
def initialize_json_file():
    default_data = {"users": []}
    try:
        if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
            logger.debug("Creating new data.json with default data")
            with open(DATA_FILE, "w") as f:
                json.dump(default_data, f, indent=4)
            return default_data
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError in data.json: {e}")
        with open(DATA_FILE, "w") as f:
            json.dump(default_data, f, indent=4)
        return default_data
    except Exception as e:
        logger.error(f"Error reading data.json: {e}")
        return default_data

# Write JSON file
def write_json(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        logger.debug("Successfully wrote to data.json")
    except Exception as e:
        logger.error(f"Error writing to data.json: {e}")


# -------------------- ROUTES --------------------

@app.get("/")
async def test_server():
    logger.debug("Accessed test endpoint")
    return {"message": "Server is running"}


@app.post("/save_name")
async def save_name(request: Request):
    try:
        data = await request.json()
        name = data.get("name")
        if not name:
            return JSONResponse({"error": "Name is required"}, status_code=400)

        user_id = str(uuid.uuid4())
        json_data = initialize_json_file()
        json_data["users"].append({
            "user_id": user_id,
            "name": name,
            "conversations": [],
            "feedback": []
        })
        write_json(json_data)
        logger.debug(f"Saved user: {name}, ID: {user_id}")
        return JSONResponse({"user_id": user_id, "name": name}, status_code=201)
    except Exception as e:
        logger.error(f"Error in save_name: {e}")
        return JSONResponse({"error": "Internal server error"}, status_code=500)


@app.post("/save_conversation")
async def save_conversation(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        conversation = data.get("conversation")
        if not user_id or not conversation:
            return JSONResponse({"error": "User ID and conversation are required"}, status_code=400)

        json_data = initialize_json_file()
        for user in json_data["users"]:
            if user["user_id"] == user_id:
                user["conversations"].append(conversation)
                write_json(json_data)
                logger.debug(f"Saved conversation for user ID: {user_id}")
                return JSONResponse({"success": True, "user_id": user_id}, status_code=201)
        return JSONResponse({"error": "User ID not found"}, status_code=404)
    except Exception as e:
        logger.error(f"Error in save_conversation: {e}")
        return JSONResponse({"error": "Internal server error"}, status_code=500)


@app.post("/save_feedback")
async def save_feedback(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        feedback_text = data.get("feedback_text")
        if not user_id or not feedback_text:
            return JSONResponse({"error": "User ID and feedback text are required"}, status_code=400)

        json_data = initialize_json_file()
        for user in json_data["users"]:
            if user["user_id"] == user_id:
                user["feedback"].append(feedback_text)
                write_json(json_data)
                logger.debug(f"Saved feedback for user ID: {user_id}")
                return JSONResponse({"success": True, "user_id": user_id}, status_code=201)
        return JSONResponse({"error": "User ID not found"}, status_code=404)
    except Exception as e:
        logger.error(f"Error in save_feedback: {e}")
        return JSONResponse({"error": "Internal server error"}, status_code=500)


@app.get("/fetch_all")
async def fetch_all():
    try:
        json_data = initialize_json_file()
        logger.debug("Fetched all data")
        return JSONResponse(json_data, status_code=200)
    except Exception as e:
        logger.error(f"Error in fetch_all: {e}")
        return JSONResponse({"error": "Internal server error"}, status_code=500)


