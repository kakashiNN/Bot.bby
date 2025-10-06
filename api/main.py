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
    sender: str
    message: str

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

            # Save to MongoDB
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
            return {"reply": "𝐞𝐭𝐚 𝐚𝐦𝐚𝐤𝐞 𝐭𝐞𝐚𝐜𝐡 𝐤𝐨𝐫𝐚 𝐡𝐨𝐲 𝐧𝐚𝐢."}

    # --- Owner special response ---
    if msg.sender.lower() == "tumar owner ke":
        return {"reply": "𝙽𝚒𝚛𝚘𝚋 𝚊𝚖𝚊𝚛 𝚘𝚠𝚗𝚎𝚛 🥰"}

    return {"reply": "Invalid sender"}
