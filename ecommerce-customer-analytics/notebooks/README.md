# Notebook workflow

The reproducible workflow is implemented as Python scripts in `src/` so it can run from a terminal or VS Code without notebook setup.

1. Run `python src/generate_data.py`.
2. Run `python src/analyze.py`.
3. Explore CSVs under `outputs/` and charts under `outputs/figures/`.
4. For a notebook version, create a notebook in this folder and import functions / read generated CSVs with Pandas.

Example:
```python
import pandas as pd
kpis = pd.read_csv("../outputs/kpi_summary.csv")
monthly = pd.read_csv("../outputs/monthly_sales.csv")
display(kpis)
display(monthly.head())
```
