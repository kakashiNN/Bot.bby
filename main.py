from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
from pymongo import MongoClient

app = FastAPI()

# --- JSON memory setup (backup / fallback) ---
memory_file = "memory.json"
if os.path.exists(memory_file):
    with open(memory_file, "r") as f:
        memory = json.load(f)
else:
    memory = {}

def save_memory():
    with open(memory_file, "w") as f:
        json.dump(memory, f, indent=4)

# --- MongoDB setup ---
MONGO_URL = "mongodb+srv://Bby001:AYt6mKeahnziwlj5@bby0.wxo4bjv.mongodb.net/?retryWrites=true&w=majority&appName=bby0"
client = MongoClient(MONGO_URL)
db = client["chatbot_db"]
collection = db["memory"]

# --- Pydantic model ---
class Message(BaseModel):
    sender: str
    message: str

# --- API endpoint ---
@app.post("/chat/")
def chat_api(msg: Message):
    text = msg.message.strip()

    # --- Teach command ---
    if text.lower().startswith("/bby teach"):
        try:
            _, rest = text.split(" ", 2)[1:]
            trigger, reply = rest.split(" - ", 1)
            trigger = trigger.strip().lower()
            reply = reply.strip()

            # Save to JSON (backup)
            memory[trigger] = reply
            save_memory()

            # Save to MongoDB (primary)
            collection.update_one(
                {"trigger": trigger},
                {"$set": {"reply": reply}},
                upsert=True
            )

            return {"reply": f"𝚜𝚑𝚒𝚔𝚝𝚎 𝚙𝚊𝚛𝚕𝚊𝚖 ! '{trigger}' 𝚎𝚛 𝚓𝚘𝚗𝚗𝚘 𝚊𝚖𝚒 𝚛𝚎𝚙𝚕𝚢 𝚍𝚒𝚋𝚘 '{reply}'."}
        except:
            return {"reply": "𝚃𝚎𝚊𝚌𝚑 𝚏𝚘𝚛𝚖𝚊𝚝 𝚟𝚑𝚞𝚕: /bby teach trigger - reply"}

    # --- User message reply from MongoDB ---
    if msg.sender.lower() == "user":
        record = collection.find_one({"trigger": text.lower()})
        if record:
            return {"reply": record["reply"]}
        elif "kemon acho" in text.lower():
            return {"reply": "𝚊𝚕𝚕𝚑𝚞𝚖𝚍𝚞𝚕𝚒𝚕𝚕𝚊𝚑, 𝚝𝚖𝚛 𝚔𝚒 𝚔𝚑𝚘𝚋𝚘𝚛?"}
        else:
            return {"reply": "𝚊𝚌𝚑𝚒 𝚟𝚊𝚕𝚊."}

    # --- Owner special response ---
    if msg.sender.lower() == "tumar owner ke":
        return {"reply": "𝙽𝚒𝚛𝚘𝚋 𝚊𝚖𝚊𝚛 𝚘𝚠𝚗𝚎𝚛 🥰"}

    return {"reply": "Invalid sender"}
