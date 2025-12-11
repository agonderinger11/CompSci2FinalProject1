from PyQt6 import uic

# Replace 'input.ui' and 'output.py' with your actual file names
with open("bankAccGui.py", "w", encoding="utf-8") as fout:
    uic.compileUi("bankAccGui.ui", fout)
