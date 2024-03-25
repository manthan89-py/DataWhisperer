from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from utils.langchain_utils import get_qa_chain, retrieve_info

# Load environment variables from .env file (if any)
load_dotenv()


class Response(BaseModel):
    result: str | None


class Question(BaseModel):
    question: str | None


origins = ["http://localhost", "http://localhost:8080", "http://localhost:3000"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
openai_embeddings = OpenAIEmbeddings()


@app.post("/createdb")
async def createdb(uploaded_file: UploadFile = File(...)):
    # Here you can add your logic to handle the file and create the database
    retrieve_info(uploaded_file, openai_embeddings)


@app.post("/predict", response_model=Response)
def predict(question: Question) -> Response:
    chat_llm = ChatOpenAI(temperature=0.7)
    chain = get_qa_chain(chat_llm, openai_embeddings)
    result = chain(question.question)
    return Response(**result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
