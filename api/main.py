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
        parts = text.split(" ", 2)
        if len(parts) < 3:
            return {"reply": "❌ Teach format vhul: /bby teach trigger - reply"}

        rest = parts[2]
        if " - " not in rest:
            return {"reply": "❌ Teach format vhul: /bby teach trigger - reply"}

        trigger, reply = rest.split(" - ", 1)
        trigger = trigger.strip().lower()
        reply = reply.strip()

        # Save to MongoDB
        collection.update_one(
            {"trigger": trigger},
            {"$set": {"reply": reply}},
            upsert=True
        )

        return {"reply": f"✅ Shikte parlam! '{trigger}' er jonno ami reply dibo '{reply}'."}

    # --- User message reply from MongoDB ---
    if msg.sender.lower() == "user":
        trigger_key = text.lower().strip()
        record = collection.find_one({"trigger": trigger_key})

        if record:
            return {"reply": record["reply"]}
        elif any(kw in trigger_key for kw in ["kemon acho", "kemon aso"]):
            return {"reply": "𝚊𝚕𝚕𝚑𝚞𝚖𝚍𝚞𝚕𝚒𝚕𝚕𝚊𝚑, tmr ki khobor?"}
        elif trigger_key.startswith("baby") or trigger_key.startswith("bby") or trigger_key.startswith("babu") or trigger_key.startswith("jan") or trigger_key.startswith("bot"):
            # Baby cmds default replies
            baby_replies = [
                "Ooo bby bolecho 🌚",
                "Yes 😀, I am NIROB bot here 🖤",
                "Bolo jaan ki korte pari tmr jonno"
            ]
            import random
            return {"reply": random.choice(baby_replies)}
        else:
            return {"reply": "𝐚𝐦𝐚𝐤𝐞 𝐞𝐭𝐚 𝐭𝐞𝐚𝐜𝐡 𝐤𝐨𝐫𝐚 𝐡𝐨𝐲 𝐧𝐚𝐢 🥲 𝐩𝐥𝐢𝐥𝐢𝐳 𝐚𝐦𝐚𝐤𝐞 𝐞𝐭𝐚 𝐭𝐞𝐚𝐜𝐡 𝐤𝐨𝐫𝐨"}

    # --- Owner special response ---
    if msg.sender.lower() == "tumar owner ke":
        return {"reply": "𝙽𝚒𝚛𝚘𝚋 𝚊𝚖𝚊𝚛 𝚘𝚠𝚗𝚎𝚛 🥰"}

    return {"reply": "Invalid sender"}
