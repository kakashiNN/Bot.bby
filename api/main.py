from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# --- MongoDB setup ---
MONGO_URL = "mongodb+srv://Bby001:AYt6mKeahnziwlj5@bby0.wxo4bjv.mongodb.net/?retryWrites=true&w=majority&appName=bby0"
client = MongoClient(MONGO_URL)
db = client["chatbot_db"]
collection = db["memory"]

class Message(BaseModel):
    sender: str  # "user" বা "bot"
    message: str

@app.post("/chat/")
def chat_api(msg: Message):
    text = msg.message.strip().lower()

    # --- Teach command ---
    if text.startswith("/bby teach"):
        parts = text.split(" ", 2)
        if len(parts) < 3 or " - " not in parts[2]:
            return {"reply": "❌ 𝗧𝗲𝗮𝗰𝗵 𝗳𝗼𝗿𝗺𝗮𝘁 𝘃𝗵𝘂𝗹: /bby teach trigger - reply"}

        trigger, reply = parts[2].split(" - ", 1)
        trigger = trigger.strip()
        reply = reply.strip()

        # Save to MongoDB
        collection.update_one(
            {"trigger": trigger},
            {"$set": {"reply": reply}},
            upsert=True
        )

        return {"reply": f"✅ 𝘀𝗵𝗶𝗸𝗵𝘁𝗲 𝗽𝗮𝗿𝗹𝗮𝗺 ! '{trigger}' 𝗲𝗿 𝗷𝗼𝗻𝗻𝗼 𝗿𝗲𝗽𝗹𝘆 𝗱𝗶𝗯𝗼'{reply}'."}

    # --- Owner query ---
    if "tumar owner ke" in text or "tumar boss ke" in text:
        return {"reply": "𝐚𝐦𝐚𝐫 𝐨𝐰𝐧𝐞𝐫 𝐧𝐢𝐫𝐨𝐛 😍"}

    # --- Check memory for trigger ---
    record = collection.find_one({"trigger": text})
    if record:
        return {"reply": record["reply"]}

    # --- Trigger not taught yet ---
    return {"reply": "❌ 𝗲𝘁𝗮 𝗮𝗺𝗮𝗸𝗲 𝘁𝗲𝗮𝗰𝗵 𝗸𝗼𝗿𝗮 𝗵𝗼𝘆 𝗻𝗮𝗶 ... 𝗽𝗹𝗲𝗮𝘀𝗲 𝗲𝘁𝗮 𝗮𝗺𝗮𝗸𝗲 𝘁𝗲𝗮𝗰𝗵 𝗸𝗼𝗿𝗼"}
