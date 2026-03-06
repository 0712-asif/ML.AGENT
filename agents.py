import ollama

def planner(task):
    """Generate detailed implementation plan."""
    response = ollama.chat(
        model="llama3:8b",
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior software architect.

CRITICAL CONSTRAINTS:
The program must be a self-contained Python SCRIPT that:
- Does NOT require user input (no input(), no prompts)
- Does NOT start a web server (no Flask, FastAPI, Django servers)
- Does NOT run indefinitely or block
- Does NOT use asyncio event loops
- Executes and terminates automatically in seconds
- Produces output to stdout

TASK: {task}

Create a SHORT, CLEAR implementation plan that respects these constraints.

If the task requires something unsupported (interactive, server, long-running), state that in the plan.

PLAN:"""
            }
        ]
    )
    return response['message']['content'].strip()


def coder(plan):
    """Generate complete, working Python code."""
    response = ollama.chat(
        model="deepseek-coder:6.7b",
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior Python developer.

Based on this plan:

{plan}

Generate a COMPLETE SINGLE-FILE working Python program.

CRITICAL RULES (FOLLOW EXACTLY):
- DO NOT use markdown backticks (no ```)
- NO EXPLANATION TEXT BEFORE OR AFTER CODE
- NO COMMENTS
- NO DOCSTRINGS
- DO NOT use input() - EVER
- DO NOT use input_raw() or raw_input()
- DO NOT require user interaction
- DO NOT have infinite loops waiting for input
- DO NOT create running servers (no app.run(), no Flask/FastAPI servers)
- DO NOT use asyncio event loops
- Use hardcoded SAMPLE values for demonstration
- Program must execute automatically in 1-5 seconds
- Program must print output immediately upon execution
- For Flask/FastAPI: Define app but DO NOT run it - just test it
- For APIs: Use requests library to test endpoints, don't start server
- NO markdown, NO code blocks, NO backticks

The program will be run non-interactively in a sandbox.
All data must be hardcoded.
Demonstrate functionality with concrete sample values.

WRITE PURE PYTHON CODE ONLY (NO BACKTICKS, NO MARKDOWN):"""
            }
        ]
    )
    
    content = response['message']['content'].strip()
    return content


def debugger(code, error_msg):
    """Fix broken code with full context."""
    response = ollama.chat(
        model="phi3",
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert Python debugger.

BROKEN CODE:
{code}

ERROR:
{error_msg}

REQUIREMENTS:
- Return COMPLETE FIXED code
- NO MARKDOWN BACKTICKS
- NO EXPLANATIONS
- NO COMMENTS
- Just the corrected Python code
- Ready to execute immediately

FIXED CODE:"""
            }
        ]
    )
    
    content = response['message']['content'].strip()
    return content