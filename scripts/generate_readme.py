#!/usr/bin/env python3
import csv, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

SECTION_META = {
    "government": {},
    "research": {},
    "international": {},
    "independent": {},
    "platforms": {},
}

TABLE_HEADER_LINES = [
    "| ردیف | عنوان | موضوع(ات) | فرمت انتشار | توضیحات |",
    "|:----:|:-----:|:---------:|:-----------:|:-------:|"
]

def read_csv(name):
    p = ROOT / "data" / f"{name}.csv"
    if not p.exists():
        return []
    rows = []
    with open(p, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("active", "true").strip().lower() == "true":
                rows.append(row)
    return rows

def make_table(rows):
    lines = list(TABLE_HEADER_LINES)
    for row in rows:
        title = row.get("title", "").strip()
        url = row.get("url", "").strip()
        topics = row.get("topics", "").strip()
        formats = row.get("formats", "").strip().replace(",", "<br/>")
        desc = row.get("description", "").strip()
        row_id = row.get("id", "").strip()
        linked_title = f"[{title}]({url})" if url else title
        lines.append(f"| {row_id} | {linked_title} | {topics} | {formats} | {desc} |")
    return "\n".join(lines)

def build_readme():
    template_path = ROOT / "README.template.md"
    if not template_path.exists():
        print("ERROR: README.template.md not found", file=sys.stderr)
        sys.exit(1)
    template = template_path.read_text(encoding="utf-8")
    for key in SECTION_META:
        rows = read_csv(key)
        table = make_table(rows)
        placeholder = f"<!-- TABLE:{key.upper()} -->"
        template = template.replace(placeholder, table)
    (ROOT / "README.md").write_text(template, encoding="utf-8")
    print("README.md regenerated successfully.")

if __name__ == "__main__":
    build_readme()
