import streamlit as st

from app.styles import apply_page_config, inject_global_styles
from app.ui import run_app

apply_page_config()
inject_global_styles()
run_app()
