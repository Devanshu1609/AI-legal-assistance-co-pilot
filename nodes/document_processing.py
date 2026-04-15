import fitz
import os
import re
from PIL import Image
import io
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,
    chunk_overlap=180,
    separators=["\n\n", "\n", ".", " ", ""]
)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    batch_size=32,
    google_api_key=GOOGLE_API_KEY
)

def extract_pdf_content(pdf_path, image_output_dir="extracted_images"):
    
    os.makedirs(image_output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    
    full_text = ""
    image_metadata = []
    
    for page_number in range(len(doc)):
        page = doc[page_number]
        
        text = page.get_text("text")
        full_text += f"\n\n--- Page {page_number+1} ---\n"
        full_text += text
        
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            image_filename = f"{image_output_dir}/page{page_number+1}_img{img_index}.{image_ext}"
            
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)
            
            image_metadata.append({
                "page": page_number + 1,
                "image_path": image_filename
            })
    
    return full_text, image_metadata


def process_document(file_path):
    if file_path.lower().endswith(".pdf"):
        file_name = os.path.basename(file_path)
        persist_directory = f"./chroma_legal_db/{file_name}"

        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            print(f"Loading existing vector store for '{file_name}'...")

            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )

            text, _ = extract_pdf_content(file_path)
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n+', '\n', text)
            cleaned_text = text.strip()

            return vectorstore, cleaned_text, None

        print(f"Creating new vector store for '{file_name}'...")

        text, images = extract_pdf_content(file_path)

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        cleaned_text = text.strip()

        base_document = Document(
            page_content=cleaned_text,
            metadata={"source": file_name}
        )

        chunks = text_splitter.split_documents([base_document])
        print(f"Document '{file_name}' split into {len(chunks)} chunks.")

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )

        print(f"Vector store created at '{persist_directory}'")

        return vectorstore, cleaned_text, chunks

    else:
        raise ValueError("Unsupported file type. Only PDF is supported.")