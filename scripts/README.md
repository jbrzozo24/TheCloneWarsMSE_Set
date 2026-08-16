## Utility Scripts for Set Management and Design Iteration

### curve_audit.py

Generate an HTML pages showing mana curve for each archetype based on heuristic card tagging

```bash
# Create a venv
python -m venv .venv
source .venv/Scripts/activate
pip install uv
uv pip install pandas
uv pip install openpyxl

# Copy an exported xlsx into the scripts directory
# Named Custom_Set_Cards.xlsx
# Then, run the script
cd scripts
python curve_audit.py Custom_Set_Cards.xlsx --out ../docs/curve-audit.html
```