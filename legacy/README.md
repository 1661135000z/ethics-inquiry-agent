# Archive

`streamlit/` preserves the earlier standalone Python + Streamlit implementation, including its tests, local components and fonts. `design-notes/` contains superseded planning documents; they are historical records, not instructions for the current release.

The current React interface and Python API are at the repository root. This archive is excluded from the current portable package and deployment.

To run the old application, use a separate environment and work from `legacy/streamlit/`:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Configure secrets privately using that folder's template. The archived README describes the earlier release and may contain superseded model names, limits and deployment notes; use the root documentation for the live app.
