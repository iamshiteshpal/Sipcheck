# cas360-view

This app is now organized into a small root entrypoint and reusable modules under `app/`:

- `dashboard.py` – Streamlit entrypoint
- `app/styles.py` – page config and global styling
- `app/helpers.py` – utility functions
- `app/exporters.py` – Excel and HTML report generation
- `app/parser.py` – CAS PDF parsing
- `app/live.py` – live NAV fetching
- `app/processor.py` – data transformation
- `app/ui.py` – page rendering and sidebar logic
