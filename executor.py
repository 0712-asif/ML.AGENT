import os
import subprocess
import re
import ast
import sys

MAX_EXECUTION_TIME = 20
ML_EXECUTION_TIME = 30


def detect_program_type(code):
    """Classify program type for autonomous execution."""
    code_lower = code.lower()
    
    ml_keywords = ["sklearn", "pandas", "numpy", "xgboost", "lightgbm", "cross_val", "train_test_split"]
    if any(kw in code_lower for kw in ml_keywords):
        return "ml"
    
    if "app.run(" in code_lower or "uvicorn.run(" in code_lower:
        return "server"
    if "flask(" in code_lower or "fastapi(" in code_lower:
        return "server"
    if "django" in code_lower and "management" in code_lower:
        return "server"
    if "input(" in code_lower:
        return "interactive"
    if "asyncio.run(" in code_lower or "asyncio.get_event_loop" in code_lower:
        return "async"
    
    return "script"


def extract_python_code(text):
    """Extract Python code from AI response - strip ALL markdown artifacts."""
    text = text.strip()
    
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    
    patterns = [
        r"```python\s*(.*?)\s*```",
        r"```py\s*(.*?)\s*```",
        r"```\s*python\s*(.*?)\s*```",
        r"```\s*Python\s*(.*?)\s*```",
        r"```\s*(.*?)\s*```",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            code = matches[0].strip()
            code = code.encode('utf-8', 'ignore').decode('utf-8')
            lines = code.split('\n')
            if lines and lines[0].lower() in ['python', 'py', 'python3']:
                code = '\n'.join(lines[1:]).strip()
            if code and code.count('\n') > 2:
                return _clean_code_lines(code)
    
    clean_text = text.strip()
    if clean_text.startswith(('from ', 'import ', 'def ', 'class ')):
        lines = clean_text.split('\n')
        code_lines = []
        for line in lines:
            line = line.encode('utf-8', 'ignore').decode('utf-8')
            stripped = line.strip()
            
            if stripped and stripped[0] not in '#;!':
                code_lines.append(line)
            elif not stripped and code_lines:
                break
        
        return _clean_code_lines('\n'.join(code_lines).strip())
    
    return _clean_code_lines(text.strip())


def _clean_code_lines(code):
    """Remove explanations and clean code lines."""
    lines = code.split('\n')
    cleaned_lines = []
    last_valid_idx = -1
    
    for i, line in enumerate(lines):
        line_encode = line.encode('utf-8', 'ignore').decode('utf-8').strip()
        if line_encode and not line_encode.startswith(('#', '//', 'Note:', 'Output:', 'Result:', 'Explanation:', 'The ', 'This ', 'You ', 'Here ', 'I ', 'It ', 'We ')):
            cleaned_lines.append(line)
            last_valid_idx = i
    
    if last_valid_idx >= 0:
        return '\n'.join(cleaned_lines[:last_valid_idx+1]).strip()
    
    return '\n'.join(cleaned_lines).strip()


def validate_syntax(code):
    """Validate Python syntax using AST."""
    try:
        code_clean = code.encode('utf-8', 'ignore').decode('utf-8')
        ast.parse(code_clean)
        return True, None
    except SyntaxError as e:
        error_msg = f"Line {e.lineno}: {str(e)}"
        return False, error_msg


def block_unsafe_patterns(code):
    """Block interactive and dangerous patterns."""
    unsafe_patterns = [
        ("input(", "Interactive input() is not allowed"),
        ("input_raw(", "Interactive input_raw() is not allowed"),
        ("raw_input(", "Interactive raw_input() is not allowed"),
        ("while True", "Infinite loops not allowed"),
        ("import os; os.system", "Direct system calls not allowed"),
        ("subprocess.Popen", "Subprocess operations not allowed"),
        ("eval(", "eval() is not allowed"),
        ("exec(", "exec() is not allowed"),
        ("__import__", "__import__() is not allowed"),
        ("app.run(", "Server startup not allowed (app.run)"),
        (".run(", "Server startup not allowed (.run)"),
        ("flask import Flask", "Flask server generation not allowed"),
        ("django.core.management", "Django server not allowed"),
        ("asyncio.run", "Async event loop blocking not allowed"),
        ("time.sleep", "Long sleep() calls not allowed"),
    ]

    for pattern, reason in unsafe_patterns:
        if pattern in code.lower():
            return False, reason

    return True, None


def auto_install_missing_module(error_message):
    """Automatically install missing modules."""
    match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", error_message)
    if not match:
        match = re.search(r"ImportError: No module named '([^']+)'", error_message)
    
    if match:
        module_name = match.group(1)
        base_module = module_name.split('.')[0]
        
        pip_name = base_module
        if base_module == 'cv2':
            pip_name = 'opencv-python'
        elif base_module == 'PIL':
            pip_name = 'pillow'
        elif base_module == 'yaml':
            pip_name = 'pyyaml'
        
        print(f"Installing missing module: {pip_name}")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-q', pip_name],
                timeout=30,
                capture_output=True
            )
            return True
        except Exception as e:
            print(f"Failed to install {pip_name}: {e}")
            return False
    
    return False


def create_file(path, content):
    """Create file with validation and safety checks."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    clean_content = extract_python_code(content)
    clean_content = clean_content.encode('utf-8', 'ignore').decode('utf-8')
    clean_content = clean_content.encode('ascii', 'ignore').decode('ascii')
    
    valid, syntax_error = validate_syntax(clean_content)
    if not valid:
        clean_error = syntax_error.encode('ascii', 'ignore').decode('ascii') if syntax_error else ""
        print(f"[SYNTAX ERROR] {clean_error}")
        return False
    
    safe, unsafe_reason = block_unsafe_patterns(clean_content)
    if not safe:
        clean_reason = unsafe_reason.encode('ascii', 'ignore').decode('ascii') if unsafe_reason else ""
        print(f"[SECURITY ERROR] {clean_reason}")
        return False
    
    program_type = detect_program_type(clean_content)
    if program_type == "server":
        print(f"[ERROR] Program type '{program_type}': Server-type programs not supported in autonomous mode")
        return False
    
    if program_type == "interactive":
        print(f"[ERROR] Program type '{program_type}': Interactive programs (using input()) not supported in autonomous mode")
        return False
    
    if program_type == "async":
        print(f"[ERROR] Program type '{program_type}': Async event loop programs not supported in autonomous mode")
        return False
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    return True


def run_python(file_path, timeout=MAX_EXECUTION_TIME):
    """Execute Python file with safety controls."""
    if not os.path.exists(file_path):
        return "", f"File not found: {file_path}"
    
    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", f"Execution timeout after {timeout}s"
    except Exception as e:
        return "", str(e)
