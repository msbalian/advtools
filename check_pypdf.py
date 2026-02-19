
import sys
import os

print(f"Python Executable: {sys.executable}")
try:
    import pypdf
    print(f"pypdf version: {pypdf.__version__}")
    print("pypdf installed successfully.")
except ImportError:
    print("pypdf NOT identified.")

try:
    import PyPDF2
    print(f"PyPDF2 version: {PyPDF2.__version__}")
except ImportError:
    print("PyPDF2 NOT identified.")
