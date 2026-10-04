"""Checks for the plumber / law firm assistant templates."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import industry_templates  # noqa: E402


@pytest.mark.parametrize("template_id", list(industry_templates.TEMPLATES))
def test_render_fills_business_name(template_id):
    rendered = industry_templates.render(template_id, "Acme & Sons")
    assert "Acme & Sons" in rendered["first_message"]
    assert "Acme & Sons" in rendered["system_prompt"]
    for text in (rendered["first_message"], rendered["system_prompt"]):
        assert "{" not in text and "}" not in text


@pytest.mark.parametrize("template_id", list(industry_templates.TEMPLATES))
def test_services_are_valid(template_id):
    services = industry_templates.TEMPLATES[template_id]["services"]
    names = [s["name"] for s in services]
    assert services and len(names) == len(set(names))
    assert all(2 <= len(n) <= 100 for n in names)  # ServiceBase name limits


def test_law_firm_never_gives_legal_advice_and_discloses_ai():
    rendered = industry_templates.render("law_firm", "Smith Law")
    assert "Never give legal advice" in rendered["system_prompt"]
    assert "virtual assistant" in rendered["first_message"]
    assert "recorded" in rendered["first_message"]


def test_plumber_handles_gas_emergencies():
    rendered = industry_templates.render("plumber", "Joe's Plumbing")
    assert "Gas smell" in rendered["system_prompt"]
    assert "Never quote a price" in rendered["system_prompt"]
