"""Check that every proposed sensor branch survives KiCad netlist export."""

import re
from pathlib import Path

from generate import form_at


def nets(path: Path) -> dict[str, set[str]]:
    text = path.read_text(encoding="utf-8")
    result = {}
    for match in re.finditer(r"\(net\s*\(code\s+\"", text):
        form = form_at(text, match.start())
        name = re.search(r'\(name\s+"([^"]+)"', form)
        if name:
            result[name.group(1)] = set(re.findall(r'\(ref\s+"([^"]+)"', form))
    return result


hub = nets(Path(__file__).with_name("temperature-hub.net"))
node = nets(Path(__file__).with_name("temperature-node.net"))
for slot in range(1, 19):
    bank = (slot - 1) // 6 + 1
    connector = f"J{slot + 1}"
    for line in ("SDA", "SCL"):
        refs = hub[f"/{line}_{slot:02d}"]
        assert len(refs) == 3 and connector in refs and f"U{bank}" in refs, (slot, line, refs)
for line in ("HOST_SDA", "HOST_SCL"):
    assert {"J1", "U1", "U2", "U3"}.issubset(hub[f"/{line}"])
for line in ("SDA", "SCL"):
    assert {"J1", "U1"}.issubset(node[f"/{line}"])
assert {"J1", "U1", "C1"}.issubset(node["/3V3"])
assert {"J1", "U1", "C1"}.issubset(node["/GND"])
print("Verified 18 isolated SDA/SCL branches, host buses, and node power connections")
