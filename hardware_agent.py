import anthropic
import gspread
import fitz  # PyMuPDF
import json
import os

# ==========================================
# CONFIGURATION
# ==========================================
ZENMUX_API_KEY = "sk-ai-v1-92344b0bad67b6f18bc7a9b049658e229a0b5b10894bdcd90ff4105e9055eafc" # Paste your key here
GOOGLE_SHEET_NAME = "BOM_spreadsheet" # Exact name of your Google Sheet

# ==========================================
# 1. GOOGLE SHEETS TOOL DEFINITION
# ==========================================
def update_spyder_bom(component_name, category, weight_g, voltage_v, notes):
    """
    This function actually connects to Google Sheets and writes the data.
    """
    print(f"--> [AGENT ACTION] Accessing Google Sheet: {GOOGLE_SHEET_NAME}...")
    try:
        # Authenticate using the bot credentials you downloaded
        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open(GOOGLE_SHEET_NAME)
        worksheet = sh.sheet1 
        
        # Append a new row to the bottom of the spreadsheet
        new_row = [component_name, category, weight_g, voltage_v, notes]
        worksheet.append_row(new_row)
        
        print(f"--> [SUCCESS] Added {component_name} to the BOM!\n")
        return "Success: Row added to Google Sheets."
    except Exception as e:
        print(f"--> [ERROR] Could not update sheet: {e}")
        return str(e)

# ==========================================
# 2. PDF INGESTION HELPER
# ==========================================
def extract_text_from_pdf(pdf_path):
    """Reads the datasheet and converts it to raw text for Agnes."""
    print(f"--> [SYSTEM] Reading datasheet: {pdf_path}...")
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# ==========================================
# 3. THE AGNES AI ORCHESTRATOR
# ==========================================
def analyze_datasheet(pdf_file_path):
    # Initialize the Zenmux/Anthropic client
    client = anthropic.Anthropic(
        api_key=ZENMUX_API_KEY,
        base_url="https://zenmux.ai/api/anthropic"
    )

    # Define the tools available to Agnes
    tools = [
        {
            "name": "update_spyder_bom",
            "description": "Updates the SPYDER micro insect robot Bill of Materials. Call this ONLY if the component seems viable.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "component_name": {"type": "string", "description": "Full model name of the part"},
                    "category": {"type": "string", "description": "e.g., Motor, Microcontroller, Sensor"},
                    "weight_g": {"type": "number", "description": "Weight in grams"},
                    "voltage_v": {"type": "number", "description": "Operating voltage"},
                    "notes": {"type": "string", "description": "Brief reasoning on why this fits the disaster relief constraints"}
                },
                "required": ["component_name", "category", "weight_g", "voltage_v", "notes"]
            }
        }
    ]

    # Extract the text from the local PDF
    datasheet_text = extract_text_from_pdf(pdf_file_path)

    # The Master Prompt
    system_prompt = """
    You are the lead hardware engineering assistant for project, a micro insect robot designed for disaster relief scenarios.
    Review the following manufacturer datasheet. Extract the core specs. 
    If the component weighs less than 15 grams and operates at 6V or less, it is viable. 
    If viable, autonomously trigger the 'update_spyder_bom' tool to log it. 
    If it is too heavy or requires too much power, output a text warning and do NOT log it.
    """

    print("--> [AGENT] Analyzing specs against project constraints... Please wait.")
    
    # Send the data to Agnes
    response = client.messages.create(
        model="sapiens-ai/agnes-1.5-pro",
        max_tokens=1024,
        tools=tools,
        messages=[
            {
                "role": "user",
                "content": f"{system_prompt}\n\nDATASHEET CONTENT:\n{datasheet_text[:15000]}" # Limit text to avoid token limits on massive PDFs
            }
        ]
    )

    # ==========================================
    # 4. EXECUTING THE TOOL COMMAND
    # ==========================================
    # Check if Agnes decided to call our Python function
    tool_was_called = False
    
    for content_block in response.content:
        if content_block.type == 'tool_use':
            tool_was_called = True
            print(f"--> [AGENT DECISION] Component is viable! Preparing to update BOM...")
            
            # Extract the exact parameters Agnes chose
            tool_name = content_block.name
            tool_args = content_block.input
            
            # Execute our local Python code based on the AI's decision
            if tool_name == "update_spyder_bom":
                update_spyder_bom(
                    component_name=tool_args.get("component_name"),
                    category=tool_args.get("category"),
                    weight_g=tool_args.get("weight_g"),
                    voltage_v=tool_args.get("voltage_v"),
                    notes=tool_args.get("notes")
                )

    if not tool_was_called:
        # If Agnes didn't call the tool, it means it rejected the part. Print its reasoning.
        for content_block in response.content:
            if content_block.type == 'text':
                print(f"--> [AGENT DECISION] Component Rejected:\n{content_block.text}")

# ==========================================
# RUNNING THE AGENT
# ==========================================
if __name__ == "__main__":
    # Ensure you have a PDF in the same folder named 'sample_motor.pdf'
    # Or change this path to point to a real datasheet on your computer.
    TARGET_DATASHEET = "sample_motor.pdf" 
    
    if os.path.exists(TARGET_DATASHEET):
        analyze_datasheet(TARGET_DATASHEET)
    else:
        print(f"Error: Could not find {TARGET_DATASHEET}. Please place a PDF in the folder.")