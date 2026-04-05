import anthropic
import gspread
from duckduckgo_search import DDGS

# ==========================================
# ⚙️ MISSION CONTROL
# ==========================================
ZENMUX_API_KEY = "sk-ai-v1-92344b0bad67b6f18bc7a9b049658e229a0b5b10894bdcd90ff4105e9055eafc" # Paste your key here
GOOGLE_SHEET_NAME = "BOM_spreadsheet" # Update this to your new Sheet name

# ==========================================
# 1. THE TOOLS (Web Search & Google Sheets)
# ==========================================
def search_the_web(query):
    """Searches the internet and returns the top results."""
    print(f"--> [AGENT SEARCHING] Query: '{query}'...")
    try:
        results = DDGS().text(query, max_results=3)
        formatted_results = "\n\n".join([f"Title: {r['title']}\nSnippet: {r['body']}\nLink: {r['href']}" for r in results])
        return formatted_results
    except Exception as e:
        return f"Search failed: {e}"

def update_master_bom(component_name, specs, price, link):
    """Logs the found component into your Google Sheet."""
    print(f"--> [AGENT LOGGING] Adding {component_name} to Google Sheet...")
    try:
        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open(GOOGLE_SHEET_NAME)
        worksheet = sh.sheet1 
        worksheet.append_row([component_name, specs, price, link])
        return f"Successfully added {component_name} to BOM."
    except Exception as e:
        return f"Failed to update spreadsheet: {e}"

# ==========================================
# 2. THE AI ORCHESTRATOR LOOP
# ==========================================
def run_sourcing_agent(requirements):
    client = anthropic.Anthropic(api_key=ZENMUX_API_KEY, base_url="https://zenmux.ai/api/anthropic")

    tools = [
        {
            "name": "search_the_web",
            "description": "Searches the internet for component specs, prices, and suppliers. Use this FIRST.",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The exact search engine query"}},
                "required": ["query"]
            }
        },
        {
            "name": "update_master_bom",
            "description": "Updates the Google Sheet. Call this ONLY after you have verified a component meets all constraints.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "component_name": {"type": "string"},
                    "specs": {"type": "string"},
                    "price": {"type": "string"},
                    "link": {"type": "string"}
                },
                "required": ["component_name", "specs", "price", "link"]
            }
        }
    ]
# We are explicitly ordering her to use the logging tool
    system_directive = """
    You are a strict, fast-acting autonomous sourcing agent. You MUST follow this exact sequence:
    STEP 1: Call 'search_the_web' a maximum of 1 or 2 times to find the component.
    STEP 2: YOU MUST CALL 'update_master_bom' to log the best match you found. If the exact price isn't in the text snippet, do NOT keep searching—just put "Check Link" in the price field and log it anyway.
    STEP 3: Once you have successfully called 'update_master_bom', you are finished. 
    
    CRITICAL RULE: You are strictly forbidden from finishing your task without calling 'update_master_bom' at least once.
    """

    messages = [
        {"role": "user", "content": f"{system_directive}\n\nUser Requirements: '{requirements}'"}
    ]


    # ADD A LOOP COUNTER
    MAX_LOOPS = 5
    loop_count = 0

    while loop_count < MAX_LOOPS:
        loop_count += 1
        
        response = client.messages.create(
            model="sapiens-ai/agnes-1.5-pro",
            max_tokens=2048,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_args = block.input
                    tool_id = block.id

                    if tool_name == "search_the_web":
                        result_text = search_the_web(tool_args["query"])
                    elif tool_name == "update_master_bom":
                        result_text = update_master_bom(tool_args["component_name"], tool_args["specs"], tool_args["price"], tool_args["link"])
                    
                    messages.append({
                        "role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": tool_id, "content": result_text}]
                    })
        else:
            print("\n--> [AGENT FINISHED] Final Thoughts:")
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

    # IF IT HITS THE LIMIT, FORCE IT TO STOP
    if loop_count == MAX_LOOPS:
        print("\n--> [SYSTEM] ERROR: Agent reached maximum search limit (5) and was forced to shut down to save tokens.")


# ==========================================
# RUN THE AGENT (INTERACTIVE TERMINAL)
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("AUTONOMOUS SOURCING AGENT INITIALIZED")
    print("="*50)
    
    user_input = input("\nWhat components do you need me to find today?\n> ")
    
    if user_input.strip():
        run_sourcing_agent(user_input)
    else:
        print("No requirements provided. Shutting down.")