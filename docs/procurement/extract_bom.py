"""Extract the supplied KES 30,000 Word BOM into a reviewable CSV."""

import csv
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Mammary_Protect_BOM_Kenya_30000.docx"
OUTPUT = ROOT / "Mammary_Protect_BOM_Kenya_30000.csv"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


with zipfile.ZipFile(SOURCE) as archive:
    document = ET.fromstring(archive.read("word/document.xml"))
    relationships = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
    urls = {item.get("Id"): item.get("Target", "") for item in relationships}

rows = []
table = document.find(f".//{{{W}}}tbl")
if table is None:
    raise RuntimeError("No BOM table found")
for row in table.findall(f"{{{W}}}tr")[1:]:
    cells = row.findall(f"{{{W}}}tc")
    fields = ["".join(text.text or "" for text in cell.findall(f".//{{{W}}}t")) for cell in cells]
    if len(fields) != 4:
        raise RuntimeError(f"Expected four fields, got {len(fields)}")
    link = cells[3].find(f".//{{{W}}}hyperlink")
    href = urls.get(link.get(f"{{{R}}}id"), "") if link is not None else ""
    rows.append((fields[0].strip(), fields[1].strip(), int(fields[2].replace(",", "").strip()), fields[3].strip(), href))

total = sum(row[2] for row in rows)
if len(rows) != 23 or total != 30000:
    raise RuntimeError(f"Unexpected row count or total: {len(rows)} rows, KES {total:,}")

with OUTPUT.open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(("item", "draft_quantity", "estimated_total_kes", "supplier_label", "supplier_url"))
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows; historical draft total KES {total:,}")
