"""Regression checks for Product Manager agent discovery and routing contracts."""

import ast
import json
import re
from pathlib import Path

import pytest


PLATFORM_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PLATFORM_ROOT.parent
AGENT_PATH = (
    REPOSITORY_ROOT
    / ".github"
    / "agents"
    / "agentic-qa-platform-main.agent.md"
)


def _frontmatter() -> dict[str, str]:
    content = AGENT_PATH.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", content, re.DOTALL)
    assert match, "Product Manager agent must start with YAML frontmatter"

    fields = {}
    for line in match.group(1).splitlines():
        field = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*", line)
        if field:
            fields[field.group(1)] = field.group(2)
    return fields


def _routing_bullets() -> list[str]:
    content = AGENT_PATH.read_text(encoding="utf-8")
    section = re.search(
        r"(?m)^#{1,6}[ \t]+Routing[ \t]*\n(.*?)(?=^#{1,6}[ \t]+|\Z)",
        content,
        re.DOTALL,
    )
    assert section, "Product Manager agent must document a Routing section"
    bullets = re.findall(r"(?ms)^-\s+(.*?)(?=^-\s+|\Z)", section.group(1))
    return [
        re.sub(r"\s+", " ", re.sub(r"\*\*|`", "", bullet)).strip().casefold()
        for bullet in bullets
    ]


def test_product_manager_agent_is_discoverable_from_parent_agents_directory():
    agents_directory = REPOSITORY_ROOT / ".github" / "agents"
    assert AGENT_PATH.is_file()
    assert AGENT_PATH.parent == agents_directory


def test_product_manager_frontmatter_has_discovery_fields_and_agent_tool():
    fields = _frontmatter()

    assert fields.get("name", "").strip()
    assert fields.get("target", "").strip()
    assert fields.get("user-invocable", "").casefold() == "true"
    tools = ast.literal_eval(fields["tools"])
    assert isinstance(tools, list)
    assert "agent" in tools


def test_nested_workspace_enables_parent_repository_customizations():
    settings_path = PLATFORM_ROOT / ".vscode" / "settings.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    assert settings.get("chat.useCustomizationsInParentRepositories") is True


@pytest.mark.parametrize(
    ("route_marker", "dev_role", "qa_role", "context_marker"),
    [
        ("agent-app/", "platform dev-app", "platform qa-app", "application"),
        ("demo-web/", "platform dev-web", "platform qa-web", "demo"),
        (
            "playwright",
            "platform dev-pw",
            "platform qa-tester",
            "infrastructure",
        ),
        (
            "platform dev-docs",
            "platform dev-docs",
            "platform qa-tester",
            "configuration",
        ),
    ],
)
def test_documented_routing_pairs_each_task_kind_with_its_dev_and_qa(
    route_marker: str, dev_role: str, qa_role: str, context_marker: str
):
    matching_bullets = [
        bullet for bullet in _routing_bullets() if route_marker in bullet
    ]

    assert len(matching_bullets) == 1
    assert dev_role in matching_bullets[0]
    assert qa_role in matching_bullets[0]
    assert context_marker in matching_bullets[0]
