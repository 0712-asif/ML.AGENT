#!/usr/bin/env python
import subprocess
import sys
import os

os.chdir('project')
result = subprocess.run([sys.executable, 'ml_app.py'], capture_output=True, text=True, timeout=30)
print(result.stdout)
if result.stderr:
    print('STDERR:', result.stderr)
print(f'\nReturn code: {result.returncode}')
