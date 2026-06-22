#!/usr/bin/env python3
"""
build_readme.py  —  CSV → README.md + datasets.md auto-builder
Run locally:  python scripts/build_readme.py
Run by CI:    triggered automatically on push to data/
"""

import csv, os, re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ── section config ──────────────────────────────────────────────────────────
SECTIONS = [
    {
        "file":    "government.csv",
        "heading": "## داده\u200c\u0647\u0627\u06cc \u0631\u0633\u0645\u06cc \u0648 \u062f\u0648\u0644\u062a\u06cc",
        "intro":   "\u0622\u062f\u0631\u0633\u200c\u0647\u0627\u06cc \u0630\u06a9\u0631 \u0634\u062f\u0647 \u062f\u0631 \u0627\u06cc\u0646 \u0628\u062e\u0634 \u0645\u0631\u0628\u0648\u0637 \u0628\u0647 \u0627\u0631\u06af\u0627\u0646\u200c\u0647\u0627\u06cc \u0631\u0633\u0645\u06cc \u062f\u0648\u0644\u062a\u06cc \u062f\u0631 \u0627\u06cc\u0631\u0627\u0646 \u0647\u0633\u062a\u0646\u062f.",
    },
    {
        "file":    "research.csv",
        "heading": "## \u0645\u0631\u0627\u06a9\u0632 \u067e\u0698\u0648\u0647\u0634\u06cc \u0631\u0633\u0645\u06cc",
        "intro":   "",
    },
    {
        "file":    "international.csv",
        "heading": "## \u0645\u0646\u0627\u0628\u0639 \u0631\u0633\u0645\u06cc \u0628\u06cc\u0646\u200c\u0627\u0644\u0645\u0644\u0644\u06cc",
        "intro":   "",
    },
    {
        "file":    "independent.csv",
        "heading": "## \u0645\u0648\u0633\u0633\u0627\u062a \u0645\u0633\u062a\u0642\u0644 \u0627\u0634\u062a\u0631\u0627\u06a9\u200c\u06af\u0630\u0627\u0631\u06cc \u062f\u0627\u062f\u0647",
        "intro":   "",
    },
    {
        "file":    "platforms.csv",
        "heading": "## \u067e\u0644\u062a\u0641\u0631\u0645\u200c\u0647\u0627\u06cc \u0627\u0634\u062a\u0631\u0627\u06a9 \u062f\u0627\u062f\u0647",
        "intro":   "",
    },
]

DATASETS_SECTION = {
    "file":    "datasets.csv",
    "heading": "## \u062f\u06cc\u062a\u0627\u0633\u062a\u200c\u0647\u0627\u06cc \u062c\u0645\u0639\u200c\u0622\u0648\u0631\u06cc \u0634\u062f\u0647 \u0639\u0645\u0648\u0645\u06cc",
    "intro":   "",
}

README_HEADER = """<div dir=\"rtl\">\n\n# Awesome Iran open data\n\n![Open Source](https://img.shields.io/badge/Open_Source-\u0645\u062c\u0648\u0632_\u0622\u0632\u0627\u062f-007EC6?style=flat&logo=open-source-initiative&logoColor=white)   ![Open Data](https://img.shields.io/badge/Open_Data-\u062f\u0627\u062f\u0647\u200c_\u0628\u0627\u0632-008000?style=flat&logo=open-access&logoColor=white)      ![GitHub Repo stars](https://img.shields.io/github/stars/alirezach/awesome-iran-opendata)\n\n\u0627\u06cc\u0646 \u0645\u062e\u0632\u0646 \u0628\u0627 \u0627\u06cc\u062f\u0647 \u062a\u0633\u0647\u06cc\u0644 \u062f\u0633\u062a\u0631\u0633\u06cc \u0648 \u0622\u0634\u0646\u0627\u06cc\u06cc \u067e\u0698\u0648\u0647\u0634\u06af\u0631\u0627\u0646 \u0648 \u0631\u0648\u0632\u0646\u0627\u0645\u0647\u200c\u0646\u06af\u0627\u0631\u0627\u0646 \u0628\u0647 \u062f\u0627\u062f\u0647\u200c\u0647\u0627\u06cc \u0628\u0627\u0632 \u0628\u0627 \u0645\u062d\u0648\u0631\u06cc\u062a \u0627\u062e\u062a\u0635\u0627\u0635\u06cc \u0627\u06cc\u0631\u0627\u0646 \u0633\u0627\u062e\u062a\u0647 \u0634\u062f\u0647\u200c\u0627\u0633\u062a \u06a9\u0647 \u0634\u0627\u0645\u0644 \u0645\u0646\u0627\u0628\u0639 \u062f\u0648\u0644\u062a\u06cc\u060c \u0645\u0631\u0627\u06a9\u0632 \u067e\u0698\u0648\u0647\u0634\u06cc \u062f\u0648\u0644\u062a\u06cc\u060c \u0645\u0631\u0627\u06a9\u0632 \u0628\u06cc\u0646\u200c\u0627\u0644\u0645\u0644\u0644\u06cc \u0648 \u0645\u0648\u0633\u0633\u0627\u062a \u0645\u0633\u062a\u0642\u0644 \u0627\u0634\u062a\u0631\u0627\u06a9\u200c\u06af\u0630\u0627\u0631\u06cc \u062f\u0627\u062f\u0647\n\u0645\u06cc\u200c\u0628\u0627\u0634\u062f.<br>\n(\u0628\u0627 \u0633\u062a\u0627\u0631\u0647 \u062f\u0627\u062f\u0646 \u0628\u0647 \u0645\u0646 \u0648 \u0628\u0627 \u0627\u0646\u062a\u0634\u0627\u0631\u0634 \u0628\u0647 \u06a9\u0633\u0627\u0646\u06cc \u06a9\u0647 \u067e\u0698\u0648\u0647\u0634\u06af\u0631 \u06cc\u0627 \u0631\u0648\u0632\u0646\u0627\u0645\u0647\u200c\u0646\u06af\u0627\u0631 \u0647\u0633\u062a\u0646\u062f \u0627\u0646\u0631\u0698\u06cc \u0628\u062f\u06cc\u062f.)\n\n### \u062f\u0633\u062a\u0631\u0633\u06cc \u0633\u0631\u06cc\u0639 \u0628\u0647 \u0645\u0646\u0627\u0628\u0639\n\n [\u062f\u0627\u062f\u0647\u200c\u0647\u0627\u06cc \u0631\u0633\u0645\u06cc \u0648 \u062f\u0648\u0644\u062a\u06cc](#\u062f\u0627\u062f\u0647\u0647\u0627\u06cc-\u0631\u0633\u0645\u06cc-\u0648-\u062f\u0648\u0644\u062a\u06cc)<br> [\u0645\u0631\u0627\u06a9\u0632 \u067e\u0698\u0648\u0647\u0634\u06cc \u0631\u0633\u0645\u06cc](#\u0645\u0631\u0627\u06a9\u0632-\u067e\u0698\u0648\u0647\u0634\u06cc-\u0631\u0633\u0645\u06cc)<br>[\u0645\u0646\u0627\u0628\u0639 \u0631\u0633\u0645\u06cc \u0628\u06cc\u0646\u200c\u0627\u0644\u0645\u0644\u0644\u06cc](#\u0645\u0646\u0627\u0628\u0639-\u0631\u0633\u0645\u06cc-\u0628\u06cc\u0646\u0627\u0644\u0645\u0644\u0644\u06cc)<br>[\u0645\u0648\u0633\u0633\u0627\u062a \u0645\u0633\u062a\u0642\u0644 \u0627\u0634\u062a\u0631\u0627\u06a9\u200c\u06af\u0630\u0627\u0631\u06cc \u062f\u0627\u062f\u0647](#\u0645\u0648\u0633\u0633\u0627\u062a-\u0645\u0633\u062a\u0642\u0644-\u0627\u0634\u062a\u0631\u0627\u06a9\u06af\u0630\u0627\u0631\u06cc-\u062f\u0627\u062f\u0647)<br>[\u067e\u0644\u062a\u0641\u0631\u0645\u200c\u0647\u0627\u06cc \u0627\u0634\u062a\u0631\u0627\u06a9 \u062f\u0627\u062f\u0647](#\u067e\u0644\u062a\u0641\u0631\u0645\u0647\u0627\u06cc-\u0627\u0634\u062a\u0631\u0627\u06a9-\u062f\u0627\u062f\u0647)<br>[\u062f\u06cc\u062a\u0627\u0633\u062a\u200c\u0647\u0627\u06cc \u062c\u0645\u0639\u200c\u0622\u0648\u0631\u06cc \u0634\u062f\u0647 \u0639\u0645\u0648\u0645\u06cc](/datasets.md)\n"""

README_FOOTER = """
#### \u0645\u0646\u0627\u0628\u0639\n\n\u0628\u062e\u0634\u06cc \u0627\u0632 \u0627\u0637\u0644\u0627\u0639\u0627\u062a \u0627\u06cc\u0646 \u0645\u062e\u0632\u0646 \u0627\u0632 \u0645\u0646\u0627\u0628\u0639 \u0632\u06cc\u0631 \u062c\u0645\u0639\u200c\u0627\u0648\u0631\u06cc \u0634\u062f\u0647\u200c\u0627\u0646\u062f:\n\n1. [\u062f\u0627\u062f\u0647\u200c\u0647\u0627\u06cc \u0639\u0645\u0648\u0645\u06cc \u062f\u0631 \u0627\u06cc\u0631\u0627\u0646](https://d-learn.ir/courses/storytelling-data-and-journalism/lesson/public-data-in-iran/)\u060c\u062f\u0642\u06cc\u0642\u0647\n2. [\u0645\u0627 \u0627\u0632 \u062f\u0627\u062f\u0647\u200c\u0647\u0627\u06cc \u0628\u0627\u0632 \u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u0645\u06cc\u200c\u06a9\u0646\u06cc\u0645](https://rasmio.com/blog/we-use-open-data/)\u060c \u0631\u0633\u0645\u06cc\u0648\n3. [\u0648\u0628\u06cc\u0646\u0627\u0631 \u0634\u0646\u0627\u0633\u0627\u06cc\u06cc \u0645\u0646\u0627\u0628\u0639 \u0639\u0645\u0648\u0645\u06cc \u062f\u0627\u062f\u0647\u200c \u062f\u0631 \u0627\u06cc\u0631\u0627\u0646: \u06cc\u06a9 \u067e\u06cc\u0634\u200c\u0646\u06cc\u0627\u0632 \u0627\u0633\u0627\u0633\u06cc \u0628\u0631\u0627\u06cc \u062d\u0644 \u0645\u0633\u0626\u0644\u0647{\u0627\u0631\u0627\u0626\u0647\u200c\u062f\u0647\u0646\u062f\u0647: \u0634\u0645\u06cc\u0645 \u0637\u0627\u0647\u0631\u06cc}](https://d-learn.ir/irpd). \u062f\u0642\u06cc\u0642\u0647\n\n### \u0627\u06cc\u0646 \u0645\u062e\u0632\u0646 \u0628\u0647 \u0645\u0631\u0648\u0631 \u062a\u06a9\u0645\u06cc\u0644 \u0645\u06cc\u200c\u06af\u0631\u062f\u062f.\n\n\u0627\u06af\u0631 \u0645\u0646\u0627\u0628\u0639 \u062f\u06cc\u06af\u0631\u06cc \u0645\u06cc\u200c\u0634\u0646\u0627\u0633\u06cc\u062f \u0648 \u062a\u0645\u0627\u06cc\u0644 \u062f\u0627\u0631\u06cc\u062f \u06a9\u0647 \u0628\u0647 \u0644\u06cc\u0633\u062a \u0641\u0648\u0642 \u0627\u0636\u0627\u0641\u0647 \u06a9\u0646\u06cc\u062f \u0645\u06cc\u200c\u062a\u0648\u0627\u0646\u06cc\u062f \u0627\u0632 \u0628\u062e\u0634 \n [![GitHub](https://img.shields.io/badge/GitHub-Issues-181717?style=flat&logo=github&logoColor=white)](https://github.com/alirezach/awesome-iran-opendata/issues) \u0633\u0631\u0627\u0646\u0647\u0627 \u0631\u0627 \u062b\u0628\u062a \u06a9\u0646\u06cc\u062f.\n\u06cc\u0627 \u0627\u06af\u0631 \u0622\u0634\u0646\u0627\u06cc\u06cc \u0628\u0627 \u0641\u0636\u0627\u06cc \u06af\u06cc\u062a\u0647\u0627\u0628 \u0646\u062f\u0627\u0631\u06cc\u062f \u0628\u0647 \u0627\u06cc\u0645\u06cc\u0644 [![Email](https://img.shields.io/badge/Email-\u0645\u0646-D14836?style=flat&logo=gmail&logoColor=white)](mailto:alireza.chamanzar91@gmail.com) \u0627\u0631\u0633\u0627\u0644 \u06a9\u0646\u06cc\u062f.\n\n#### \u0627\u0637\u0644\u0627\u0639\u0627\u062a \u062b\u0628\u062a\u06cc \u0645\u0648\u0631\u062f \u0646\u06cc\u0627\u0632 \u0628\u0647 \u0627\u06cc\u0646 \u0634\u0631\u062d \u0647\u0633\u062a:\n1. \u0633\u0627\u0632\u0645\u0627\u0646 \u0645\u0646\u062a\u0634\u0631 \u06a9\u0646\u0646\u062f\u0647\n2. \u0622\u062f\u0631\u0633 \u062f\u0633\u062a\u0631\u0633\u06cc\n3. \u0645\u0648\u0636\u0648\u0639\u0627\u062a \u067e\u0648\u0634\u0634 \u062f\u0627\u062f\u0647 \u0634\u062f\u0647\n4. \u0641\u0631\u0645\u062a \u0627\u0646\u062a\u0634\u0627\u0631 \u062f\u0627\u062f\u0647\u200c\u0647\u0627\n5. \u062a\u0648\u0636\u06cc\u062d\u0627\u062a \u062f\u0631 \u0645\u0648\u0631\u062f \u0627\u0646\u0648\u0627\u0639 \u062f\u0627\u062f\u0647\u200c\u0647\u0627\u06cc\u06cc \u06a9\u0647 \u062f\u0631 \u062f\u0633\u062a\u0631\u0633 \u0627\u0633\u062a.\n\n<br>\n<br>\n\n<small>\u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc \u0634\u062f\u0647 \u0628\u0627 [\u0627\u0646\u06af\u0627\u0631\u0647](https://engare.net)</small>\n\n</div>\n"""

DATASETS_HEADER = """<div dir=\"rtl\">\n\n## \u062f\u06cc\u062a\u0627\u0633\u062a\u200c\u0647\u0627\u06cc \u0639\u0645\u0648\u0645\u06cc \u0648\u0628 \u0641\u0627\u0631\u0633\u06cc\n\n\u062f\u0631 \u0627\u062f\u0627\u0645\u0647 \u062f\u06cc\u062a\u0627\u0633\u062a\u200c\u0647\u0627\u06cc\u06cc \u06a9\u0647 \u0627\u0641\u0631\u0627\u062f \u0648 \u062a\u06cc\u0645\u200c\u0647\u0627 \u062f\u0631 \u0627\u06cc\u0646\u062a\u0631\u0646\u062a \u0628\u0647 \u0635\u0648\u0631\u062a \u0639\u0645\u0648\u0645\u06cc \u0645\u0646\u062a\u0634\u0631 \u06a9\u0631\u062f\u0647\u200c\u0627\u0646\u062f \u0631\u0627 \u0645\u06cc\u200c\u062a\u0648\u0627\u0646\u06cc\u062f \u0628\u0628\u06cc\u0646\u06cc\u062f.\n\n\u0627\u06af\u0631 \u062f\u06cc\u062a\u0627\u0633\u062a\u06cc \u062f\u0627\u0631\u06cc\u062f \u0648 \u062a\u0645\u0627\u06cc\u0644 \u0628\u0647 \u0627\u0646\u062a\u0634\u0627\u0631 \u0622\u0646 \u062f\u0627\u0631\u06cc\u062f \u0645\u06cc\u200c\u062a\u0648\u0627\u0646\u06cc\u062f \u0627\u0632 \u0628\u062e\u0634 issue \u0622\u0646 \u0631\u0627 \u0645\u0639\u0631\u0641\u06cc \u06a9\u0646\u06cc\u062f \u062a\u0627 \u062f\u0631 \u0644\u06cc\u0633\u062a \u0632\u06cc\u0631 \u0642\u0631\u0627\u0631 \u0628\u06af\u06cc\u0631\u062f.\n\n#### [\u0628\u0631\u06af\u0634\u062a \u0628\u0647 \u0635\u0641\u062d\u0647 \u0627\u0648\u0644](https://github.com/alirezach/awesome-iran-opendata)\n\n## \u062f\u06cc\u062a\u0627\u0633\u062a\u200c\u0647\u0627\u06cc \u062c\u0645\u0639\u200c\u0622\u0648\u0631\u06cc \u0634\u062f\u0647 \u0639\u0645\u0648\u0645\u06cc\n"""

DATASETS_FOOTER = """
#### [\u0628\u0631\u06af\u0634\u062a \u0628\u0647 \u0635\u0641\u062d\u0647 \u0627\u0648\u0644](https://github.com/alirezach/awesome-iran-opendata)\n\n</div>\n"""


def read_csv(filepath):
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def formats_to_md(formats_str):
    """Convert comma-separated formats to <br>-separated lowercase for README style."""
    if not formats_str or formats_str.strip() in ("-", ""):
        return "-"
    parts = [p.strip() for p in re.split(r"[,\u060c]", formats_str) if p.strip()]
    return "<br>".join(p.lower() for p in parts)


def build_main_table(rows):
    """Build markdown table rows for README sections (active rows only)."""
    lines = []
    lines.append("| \u0631\u062f\u06cc\u0641 | \u0639\u0646\u0648\u0627\u0646 | \u0645\u0648\u0636\u0648\u0639(\u0627\u062a) | \u0641\u0631\u0645\u062a \u0627\u0646\u062a\u0634\u0627\u0631 | \u062a\u0648\u0636\u06cc\u062d\u0627\u062a |")
    lines.append("|:----:|:-----:|:---------:|:-----------:|:-------:|")
    for row in rows:
        if row.get("active", "true").strip().lower() == "false":
            continue
        rid    = row.get("id", "").strip()
        title  = row.get("title", "").strip()
        url    = row.get("url", "").strip()
        topics = row.get("topics", "").strip()
        fmts   = formats_to_md(row.get("formats", ""))
        desc   = row.get("description", "").strip()
        title_cell = f"[{title}]({url})" if url else title
        lines.append(f"| {rid} | {title_cell} | {topics} | {fmts} | {desc} |")
    return "\n".join(lines)


def build_datasets_table(rows):
    """Build markdown table for datasets.md (active rows only)."""
    lines = []
    lines.append("| \u0631\u062f\u06cc\u0641 | \u0639\u0646\u0648\u0627\u0646 | \u0646\u0627\u0634\u0631 | \u0641\u0631\u0645\u062a | \u062a\u0648\u0636\u06cc\u062d\u0627\u062a |")
    lines.append("|:----:|:-----:|:----:|:----:|:-------:|")
    for row in rows:
        if row.get("active", "true").strip().lower() == "false":
            continue
        rid       = row.get("id", "").strip()
        title     = row.get("title", "").strip()
        url       = row.get("url", "").strip()
        publisher = row.get("publisher", "").strip()
        fmts      = formats_to_md(row.get("formats", ""))
        desc      = row.get("description", "").strip()
        title_cell = f"[{title}]({url})" if url else title
        lines.append(f"| {rid} | {title_cell} | {publisher} | {fmts} | {desc} |")
    return "\n".join(lines)


def build_readme():
    parts = [README_HEADER]
    for sec in SECTIONS:
        filepath = os.path.join(DATA_DIR, sec["file"])
        if not os.path.exists(filepath):
            print(f"WARNING: {filepath} not found, skipping section.")
            continue
        rows = read_csv(filepath)
        parts.append(sec["heading"])
        if sec["intro"]:
            parts.append("")
            parts.append(sec["intro"])
        parts.append("")
        parts.append(build_main_table(rows))
        parts.append("")
    parts.append(README_FOOTER)
    return "\n".join(parts)


def build_datasets_md():
    filepath = os.path.join(DATA_DIR, DATASETS_SECTION["file"])
    if not os.path.exists(filepath):
        print(f"WARNING: {filepath} not found.")
        return ""
    rows = read_csv(filepath)
    parts = [DATASETS_HEADER, build_datasets_table(rows), DATASETS_FOOTER]
    return "\n".join(parts)


if __name__ == "__main__":
    readme_content = build_readme()
    readme_path = os.path.join(BASE_DIR, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"\u2713 README.md written ({len(readme_content)} chars)")

    datasets_content = build_datasets_md()
    if datasets_content:
        datasets_path = os.path.join(BASE_DIR, "datasets.md")
        with open(datasets_path, "w", encoding="utf-8") as f:
            f.write(datasets_content)
        print(f"\u2713 datasets.md written ({len(datasets_content)} chars)")
