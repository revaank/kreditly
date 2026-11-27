"""Kreditly home page: loan readiness preparation for first-time borrowers in India."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import streamlit as st

from src.bank_checker import load_bank_rules
from src.translations import t
from src.ui import footer, header, page_setup

page_setup()
header("home")

# Load CSS and HTML template
assets_dir = Path(__file__).resolve().parent / "assets"
css_content = (assets_dir / "home.css").read_text(encoding="utf-8")
html_template = (assets_dir / "home.html").read_text(encoding="utf-8")

# Build dynamic lenders list & last_checked date
try:
    bank_data = load_bank_rules()
    lenders_list = bank_data.get("lenders", [])
    raw_date = bank_data.get("last_checked", "2026-11-27")
    try:
        dt = datetime.strptime(raw_date, "%Y-%m-%d")
        formatted_date = dt.strftime("%d %b %Y")
    except Exception:
        formatted_date = raw_date
except Exception:
    lenders_list = []
    formatted_date = "27 Nov 2026"

if lenders_list:
    lender_grid_items = "".join([
        f'<span style="background: #F5F6F1; border-radius: 10px; padding: 12px">{l.get("short_name", l.get("name"))}</span>'
        for l in lenders_list
    ])
else:
    default_lenders = [
        "SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak",
        "PNB", "Bank of Baroda", "Canara Bank", "Union Bank", "IndusInd",
        "IDFC FIRST", "Federal Bank", "Bajaj Finance", "Tata Capital", "Aditya Birla"
    ]
    lender_grid_items = "".join([
        f'<span style="background: #F5F6F1; border-radius: 10px; padding: 12px">{name}</span>'
        for name in default_lenders
    ])

template_vars = {
    "home_hero_eyebrow": t("home_hero_eyebrow"),
    "home_hero_title": t("home_hero_title"),
    "home_hero_subtext": t("home_hero_subtext"),
    "home_hero_cta": t("home_hero_cta"),
    "home_hero_example": t("home_hero_example"),
    "home_hero_trust1": t("home_hero_trust1"),
    "home_hero_trust2": t("home_hero_trust2"),
    "home_hero_trust3": t("home_hero_trust3"),
    "home_tools_label": t("home_tools_label"),
    "home_tools_compare": t("home_tools_compare"),
    "home_tools_safety": t("home_tools_safety"),
    "home_tools_rejected": t("home_tools_rejected"),
    "home_tools_guide": t("home_tools_guide"),
    "home_card_result": t("home_card_result"),
    "home_card_example": t("home_card_example"),
    "home_card_title": t("home_card_title"),
    "home_card_safely_borrow": t("home_card_safely_borrow"),
    "home_card_safely_borrow_val": t("home_card_safely_borrow_val"),
    "home_card_lenders_matched": t("home_card_lenders_matched"),
    "home_card_lenders_matched_val": t("home_card_lenders_matched_val"),
    "home_card_salary_emi": t("home_card_salary_emi"),
    "home_card_salary_emi_val": t("home_card_salary_emi_val"),
    "home_card_foir_caption": t("home_card_foir_caption"),
    "home_card_more_lenders": t("home_card_more_lenders"),
    "home_how_title": t("home_how_title"),
    "home_step1_title": t("home_step1_title"),
    "home_step1_desc": t("home_step1_desc"),
    "home_step2_title": t("home_step2_title"),
    "home_step2_desc": t("home_step2_desc"),
    "home_step3_title": t("home_step3_title"),
    "home_step3_desc": t("home_step3_desc"),
    "home_lenders_title": t("home_lenders_title"),
    "home_lenders_updated": t("home_lenders_updated", date=formatted_date),
    "lender_grid_items": lender_grid_items,
}

rendered_html = html_template.format(**template_vars)
st.markdown(f"<style>{css_content}</style>{rendered_html}", unsafe_allow_html=True)

footer()
