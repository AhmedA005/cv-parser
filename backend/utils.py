from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
import re
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# Load model
base_id = "mistralai/Mistral-Nemo-Instruct-2407"
tokenizer = AutoTokenizer.from_pretrained(base_id, use_fast=True)
bnb_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
model = AutoModelForCausalLM.from_pretrained(base_id, quantization_config=bnb_cfg, device_map="auto").eval()

def generate_text(prompt, max_length=300):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_length,
            pad_token_id=tokenizer.eos_token_id
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def extract_json_block(text):
    pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[-1] if matches else text

# Define output schemas
full_name_schema = ResponseSchema(name="full_name", description="Candidate full name")
email_schema = ResponseSchema(name="email", description="Candidate email")
education_schema = ResponseSchema(name="education", description="List of dictionaries, each with degree, institution, and year.")
skills_schema = ResponseSchema(name="skills", description="List of skills")
experience_schema = ResponseSchema(name="experience", description="List of dictionaries, each with role, company, and years.")

schemas = [full_name_schema, email_schema, education_schema, skills_schema, experience_schema]
output_parser = StructuredOutputParser.from_response_schemas(schemas)
format_instructions = output_parser.get_format_instructions()

cv_template = """
You are an HR assistant. Extract:

- full_name
- email
- education (degree, institution, year)
- skills
- experience (role, company, years)

Respond only in JSON using this format:
{format_instructions}

Candidate CV:
{user_input}
"""
