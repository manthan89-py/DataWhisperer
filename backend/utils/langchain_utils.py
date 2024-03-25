import os
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

VECTOR_DB_PATH = "vectorstore/faiss_index"


def create_vectordb(data, instructor_embeddings):
    vectordb = FAISS.from_documents(documents=data, embedding=instructor_embeddings)
    vectordb.save_local(VECTOR_DB_PATH)


def get_pdf_to_text(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    docs = []
    chunks = text
    docs.append(
        Document(
            page_content=chunks,
            metadata={
                "name": pdf_doc.name,
                "type": pdf_doc.type,
                "size": pdf_doc.size,
            },
        )
    )
    return docs


def get_text_data(txt_file):
    data = txt_file.file.read()
    document = Document(
        page_content=data,
        metadata={
            "name": txt_file.filename,
            "type": txt_file.content_type,
            "size": txt_file.size,
        },
    )
    return [document]


# Define a function to retrieve information from uploaded files
def retrieve_info(uploaded_file, instructor_embeddings):
    file_path = uploaded_file.filename
    file_extension = os.path.splitext(file_path)[1].lower()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    if uploaded_file.size < 100:
        if file_extension in [".docx", ".md", ".txt"]:
            document = get_text_data(uploaded_file)
            docs = text_splitter.split_documents(document)  # there are 33 total splits.
            create_vectordb(docs, instructor_embeddings)
        elif file_extension == ".pdf":
            document = get_pdf_to_text(uploaded_file)
            docs = text_splitter.split_documents(document)
            create_vectordb(docs, instructor_embeddings)
        else:
            raise Exception("Unsupported file format.")
    else:
        raise Exception("File Size is largen then 5MB. Not Supported for Now.")

def get_qa_chain(llm, instructor_embeddings):
    vectordb = FAISS.load_local(
        VECTOR_DB_PATH, instructor_embeddings, allow_dangerous_deserialization=True
    )
    retriver = vectordb.as_retriever(score_threshold=0.7)
    prompt_template = """Given the following extracted text from the uploaded files and a question, generate an answer based on this text only.
    In the answer, try to provide as much text as possible relevant to the question without making much changes.
    If the answer is not found in the context, kindly state "I don't know" in a professional manner. 

    Context: {context}  # Replace with the extracted text from all files
    Question: {question}
    """

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriver,
        input_key="query",
        return_source_documents=True,
        chain_type_kwargs=chain_type_kwargs,
    )
    return chain
