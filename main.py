from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import motor.motor_asyncio
from textblob import TextBlob  # Optional sentiment analysis library

app = FastAPI()

# MongoDB connection setup
connection_string = "mongodb+srv://db_alaa:IEYkCC1vujAVNxVy@cluster0.ccvxq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
db = client["mydatabase"]
collection = db["messages"]

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI REST API!"}

# Add message (GET /add_message)
@app.get("/add_message")
async def add_message(message: str, subject: Optional[str] = None, class_name: Optional[str] = None):
    document = {"message": message, "subject": subject, "class_name": class_name}
    
    # Insert message into MongoDB
    try:
        result = await collection.insert_one(document)
        return {"message": "Message added successfully!", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting message: {str(e)}")

# Get all messages (GET /messages)
@app.get("/messages")
async def get_messages():
    messages = []
    async for message in collection.find():
        messages.append({
            "message": message["message"],
            "subject": message.get("subject"),
            "class_name": message.get("class_name")
        })
    return {"messages": messages}

# Analyze sentiment (GET /analyze)
@app.get("/analyze")
async def analyze(group_by: Optional[str] = None):
    # Fetch all messages
    messages = []
    async for message in collection.find():
        messages.append({
            "message": message["message"],
            "subject": message.get("subject"),
            "class_name": message.get("class_name")
        })
    
    # Sentiment Analysis
    def get_sentiment(message: str):
        blob = TextBlob(message)
        sentiment = blob.sentiment.polarity
        if sentiment > 0:
            return "positive"
        elif sentiment < 0:
            return "negative"
        return "neutral"
    
    if group_by:
        grouped = {}
        for message in messages:
            key = message.get(group_by)
            if key:
                grouped[key] = grouped.get(key, 0) + 1
        return {"grouped_by": group_by, "analysis": grouped}
    
    return {"message": "No grouping selected. You can group by 'subject' or 'class_name'."}
