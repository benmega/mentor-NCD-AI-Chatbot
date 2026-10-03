from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
#TODO: Start up backend, cd frontend + python -m http.server 5500 in terminal, localhost:5500 in google
import models, schemas, scoring
from database import engine, SessionLocal
import os
from dotenv import load_dotenv # type: ignore
from openai import OpenAI

load_dotenv()
OpenAIKey = os.getenv("OpenAIKey")
client = OpenAI(api_key=OpenAIKey)

AI_INSTRUCTIONS = """
You are the Health AI Assistant for an educational health-risk assessment project.

PURPOSE:
Your purpose is to help users understand general health and lifestyle factors,
particularly factors associated with long-term non-communicable disease (NCD)
risk.

SCOPE:
- Focus on health, lifestyle, wellbeing, and NCD-related questions.
- Keep explanations understandable for teenagers and young adults.
- Provide general educational information rather than diagnosing diseases.
- Do not claim that a user definitely has or does not have a medical condition.
- Encourage the user to speak with a qualified healthcare professional when a
  question requires medical evaluation.

INFORMATION GATHERING:
When relevant, gather useful context from the user before giving a detailed
answer. This can include things such as:
- age or age range
- relevant lifestyle habits
- sleep
- physical activity
- nutrition
- stress and wellbeing
- other information directly relevant to the user's question

Do not unnecessarily ask for personal information that is not relevant to
the user's question.

CONVERSATION:
- Answer the user's current question using the available conversation context.
- Do not repeatedly ask for information that the user has already provided.
- Keep responses reasonably concise unless the user asks for more detail.
- Ask clarifying questions when necessary.

TOPIC LIMIT:
If the user asks about something unrelated to health, lifestyle, wellbeing,
or the purpose of this application, politely explain that you are designed
to assist with health-related topics and redirect them toward an appropriate
health-related question.

SAFETY:
- Do not diagnose the user.
- Do not present the chatbot's response as a substitute for professional
  medical care.
- Do not provide dangerous or harmful instructions.
- For urgent or potentially serious health situations, recommend seeking
  appropriate professional help rather than attempting to resolve the
  situation through the chatbot.

REQUEST LIMIT:
The application may impose a limit on the number of AI requests in a
conversation. Do not claim that a specific request limit exists unless the
application provides that information to you.
"""


#Creates database; database.py sets up essential variables

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://192.168.1.103:5500",
        "*", # TODO remove before using in production
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/analyze", response_model=schemas.UserHealthResponse)
def analyze(data: schemas.UserHealthCreate, db: Session = Depends(get_db)):
    
    # CALCULATE FIRST
    score, level, message, bmi, bmi_percentile = scoring.calculate_score(data)

    # Save to database - data_dict is where data is stored
    data_dict = data.dict()   # <- add ()

    data_dict.update({
        "risk_score": score,
        "risk_level": level
    })
    print(data_dict)
    db_data = models.UserHealth(**data_dict)
    print(db_data)

    
    db.add(db_data)
    print("About to save:")
    print(data_dict)
    db.commit()
    print("Database commit successful")
    db.refresh(db_data)

    return {
        "risk_score": score,
        "risk_level": level,
        "message": message,
        "bmi": bmi,
        "bmi_percentile": bmi_percentile
        
    }

@app.post("/ai")
def ai_chat(data: dict):

    user_message = data.get("message", "").strip()

    print("AI message received:")
    print(user_message)


    response = client.responses.create(
        model="gpt-5.4-mini",

        instructions=AI_INSTRUCTIONS,

        input=user_message
    )


    ai_response = response.output_text

    print("AI response:")
    print(ai_response)


    return {
        "response": ai_response
    }

# RUN APP
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


