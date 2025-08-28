import os
import json
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from groq import Groq


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Groq API key not found. Please set GROQ_API_KEY in the .env file.")

client = Groq(api_key=GROQ_API_KEY)

# LLM PLANNER 

def generate_automation_plan(task_prompt: str) -> list:
    """
    Uses the Groq API to generate a sequence of automation steps.
    """
    print(f" Generating plan for task: '{task_prompt}'...")

    
    system_prompt = """
    You are an expert web automation assistant. Your task is to convert a user's natural language instruction into a precise, structured JSON plan that a Playwright script can execute.

    The valid action types are: "navigate", "type", "click", "select".

    For each action, you must provide:
    1.  `action`: The type of action.
    2.  `selector`: The CSS selector for the target element.
    3.  `value`: The text to type or the value of the dropdown option. Required for "type" and "select".
    4.  `url`: The URL to navigate to. Required for the "navigate" action.
    5.  `description`: A brief, human-readable description of the step.

    **Important Hint for saucedemo.com:**
    - The login button's selector is `#login-button`.
    - To target an 'Add to cart' button, use the element's `id`. The `id` is constructed by converting the item's name to kebab-case (lowercase with dashes) and prepending 'add-to-cart-'.
    - For example, to add 'Sauce Labs Backpack', the correct selector is `#add-to-cart-sauce-labs-backpack`.

    Output ONLY the raw JSON array of objects, with no surrounding text or markdown.
    """
    
    try:
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": task_prompt,
                }
            ],
            model="llama3-8b-8192",  # Using a powerful Llama 3 model
            temperature=0,  # Lower temperature for more predictable JSON output
            response_format={"type": "json_object"},  # Enforce JSON output
        )
        
        json_response = chat_completion.choices[0].message.content
        data = json.loads(json_response)
        plan = next(iter(data.values())) if isinstance(data, dict) and len(data) == 1 else data

        print("✅ Plan generated successfully!")
        return plan
    except (json.JSONDecodeError, Exception) as e:
        print(f"❌ Error generating or parsing plan: {e}")
        if 'chat_completion' in locals():
            print(f"LLM Response was:\n{chat_completion.choices[0].message.content}")
        return None



def execute_automation_plan(plan: list):
    """
    Executes the automation plan using Playwright.
    """
    print("\n▶️  Starting browser automation...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        for i, step in enumerate(plan):
            action = step.get("action")
            description = step.get("description")
            print(f"Executing Step {i+1}: {description}")

            try:
                if action == "navigate":
                    page.goto(step["url"])
                elif action == "type":
                    page.locator(step["selector"]).fill(step["value"])
                elif action == "click":
                    page.locator(step["selector"]).click()
                elif action == "select":
                    page.locator(step["selector"]).select_option(step["value"])
                else:
                    print(f"⚠️ Unknown action: {action}")
                
                time.sleep(1)

            except Exception as e:
                print(f" Error on step {i+1}: {e}")
                break

        print("\n Automation finished. Browser will close in 5 seconds.")
        time.sleep(5)
        browser.close()


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    user_task = "Go to saucedemo.com, log in with username 'standard_user' and password 'secret_sauce', then add the 'Sauce Labs Backpack' and the 'Sauce Labs Bike Light' to the cart."

    automation_plan = generate_automation_plan(user_task)

    if automation_plan:
        execute_automation_plan(automation_plan)