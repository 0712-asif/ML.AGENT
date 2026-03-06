import os
import sys
from agents import planner, coder, debugger
from executor import create_file, run_python, auto_install_missing_module, detect_program_type

MAX_RETRIES = 3

# ML task keywords
ML_KEYWORDS = ['ml', 'machine learning', 'model', 'train', 'sklearn', 'predict', 'classification', 'regression', 'neural', 'deep learning']

print("\n" + "="*60)
print("AUTONOMOUS AI CODING AGENT")
print("="*60)

task = input("\nEnter your project idea: ").strip()
if not task:
    print("ERROR: Please provide a project idea")
    sys.exit(1)

# Detect if this is an ML task
is_ml_task = any(keyword in task.lower() for keyword in ML_KEYWORDS)
if is_ml_task:
    print("\n◆ ML task detected!")
    print("⚠ Redirecting to ML Specialist Agent for better results...")
    print("\nRun: python ml_main.py")
    print("And enter the same task for optimized ML pipeline generation.\n")
    sys.exit(0)

# STEP 1: PLANNING
print("\n" + "="*60)
print("STEP 1: PLANNING")
print("="*60)

try:
    plan = planner(task)
    print("\nPlan:\n")
    print(plan)
except Exception as e:
    print(f"ERROR: Planning failed - {e}")
    sys.exit(1)

# STEP 2: CODE GENERATION
print("\n" + "="*60)
print("STEP 2: CODE GENERATION")
print("="*60)

try:
    code = coder(plan)
    print("✓ Code generated")
except Exception as e:
    print(f"ERROR: Code generation failed - {e}")
    sys.exit(1)

# Detect program type
program_type = detect_program_type(code)
print(f"◆ Program type detected: {program_type}")

# Setup project directory
project_dir = os.path.join(os.getcwd(), "project")
os.makedirs(project_dir, exist_ok=True)
file_path = os.path.join(project_dir, "app.py")

# Create file with validation
if not create_file(file_path, code):
    print("ERROR: Code rejected before execution (syntax or safety check failed)")
    sys.exit(1)

print(f"✓ Code saved to {file_path}")

# STEP 3: EXECUTION & RETRY LOOP
attempt = 1
success = False

while attempt <= MAX_RETRIES and not success:
    print("\n" + "="*60)
    print(f"STEP 3: EXECUTION (Attempt {attempt}/{MAX_RETRIES})")
    print("="*60)
    
    output, error = run_python(file_path)
    
    if error:
        print(f"\n⚠ ERROR:\n{error}")
        
        # Try auto-installing missing module
        if auto_install_missing_module(error):
            print("✓ Module installed, retrying...")
            attempt += 1
            continue
        
        # Try debugging if retries remain
        if attempt < MAX_RETRIES:
            print("\n" + "="*60)
            print(f"STEP 4: DEBUGGING (Attempt {attempt})")
            print("="*60)
            
            try:
                print("Analyzing and fixing error...")
                fixed_code = debugger(code, error)
                
                if not create_file(file_path, fixed_code):
                    print("ERROR: Fixed code failed validation (syntax or safety check)")
                    break
                
                code = fixed_code
                print("✓ Code fixed and saved")
            except Exception as e:
                print(f"ERROR: Debugging failed - {e}")
                break
        
        attempt += 1
    else:
        # SUCCESS
        print("\n" + "="*60)
        print("STEP 5: SUCCESS")
        print("="*60)
        print("\nProgram output:\n")
        print(output if output else "(No output produced)")
        success = True

# Final status
print("\n" + "="*60)
if success:
    print("✓ AGENT COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")
    sys.exit(0)
else:
    print("✗ AGENT FAILED")
    print("="*60 + "\n")
    sys.exit(1)