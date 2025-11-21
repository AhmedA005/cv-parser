from fastapi import FastAPI, UploadFile, HTTPException, File, Request
import uvicorn, threading, time, socket
from pyngrok import ngrok, conf
import tempfile, os
from dotenv import load_dotenv
from utils import generate_text, extract_json_block, output_parser, cv_template, format_instructions

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
NGROK_TOKEN = os.getenv("NGROK_TOKEN")

app = FastAPI()

@app.post("/extract")
async def extract(req: Request, file: UploadFile = File(...)):
    # Authentication
    if req.headers.get("authorization") != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Save PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Extract text
    from langchain.document_loaders import PyPDFLoader
    loader = PyPDFLoader(tmp_path)
    pages = loader.load()
    cv_text = "\n".join([p.page_content for p in pages])

    # Build prompt
    from langchain.prompts import PromptTemplate
    prompt = PromptTemplate(
        template=cv_template,
        input_variables=["user_input", "format_instructions"]
    ).format(user_input=cv_text, format_instructions=format_instructions)

    # Generate
    llm_output = generate_text(prompt, max_length=1500)

    # Extract JSON
    json_text = extract_json_block(llm_output)

    try:
        structured = output_parser.parse(json_text)
    except:
        structured = {"error": "Parsing failed", "raw": llm_output}

    return {"results": structured}


# Utilities to run FastAPI with ngrok
def free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

port = free_port()
conf.get_default().auth_token = NGROK_TOKEN
public_url = ngrok.connect(port).public_url
print("Your public URL:", public_url)

def run_app(): 
    uvicorn.run(app, host="0.0.0.0", port=port)
    
threading.Thread(target=run_app, daemon=True).start()
time.sleep(1)
