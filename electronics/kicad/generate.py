"""Generate the first-pass Mammary Protect KiCad schematics.

Uses symbol geometry from the installed KiCad standard libraries.  No
third-party ultrasound schematic is copied into this repository.
"""

from __future__ import annotations

import argparse
import re
import uuid
from pathlib import Path


LIB_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\symbols")
OUT = Path(__file__).resolve().parent


def uid() -> str:
    return str(uuid.uuid4())


def form_at(text: str, start: int) -> str:
    depth = 0
    quoted = False
    escape = False
    for i in range(start, len(text)):
        c = text[i]
        if quoted:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    raise ValueError("unbalanced KiCad form")


def extract(lib: str, name: str) -> str:
    text = (LIB_ROOT / f"{lib}.kicad_sym").read_text(encoding="utf-8")
    marker = f'\n\t(symbol "{name}"'
    pos = text.find(marker)
    if pos < 0:
        raise ValueError(f"Missing symbol {lib}:{name}")
    raw = form_at(text, pos + 2)
    return raw.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)


class LibrarySymbol:
    def __init__(self, lib: str, name: str):
        self.lib = lib
        self.name = name
        self.id = f"{lib}:{name}"
        self.raw = extract(lib, name)
        self.pins: dict[str, tuple[float, float, int]] = {}
        for match in re.finditer(r"\(pin\s+(?:input|output|bidirectional|tri_state|passive|power_in|power_out|open_collector|open_emitter|no_connect|free)\s+\w+", self.raw):
            form = form_at(self.raw, match.start())
            nm = re.search(r'\(name\s+"([^"]+)"', form)
            num = re.search(r'\(number\s+"([^"]+)"', form)
            at = re.search(r'\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(\d+)\)', form)
            if num and at:
                pin = (float(at.group(1)), float(at.group(2)), int(at.group(3)))
                self.pins[num.group(1)] = pin
                if nm:
                    self.pins[nm.group(1)] = pin


def q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def fmt(n: float) -> str:
    return f"{n:.4f}".rstrip("0").rstrip(".") if n else "0"


def grid(n: float) -> float:
    return round(n / 1.27) * 1.27


class Sheet:
    def __init__(self, name: str, title: str, paper: str):
        self.name = name
        self.title = title
        self.paper = paper
        self.uuid = uid()
        self.symbols: dict[str, LibrarySymbol] = {}
        self.items: list[str] = []

    def place(self, sym: LibrarySymbol, ref: str, value: str, x: float, y: float, nets: dict[str, str | None], footprint: str = ""):
        x, y = grid(x), grid(y)
        self.symbols[sym.id] = sym
        s = [f'(symbol (lib_id {q(sym.id)}) (at {fmt(x)} {fmt(y)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {q(uid())})']
        if sym.id == 'Interface_Expansion:TCA9548APWR':
            prop_x, prop_y = x, y - 34.29
        elif sym.id == 'Sensor_Temperature:TMP102xxDRL':
            prop_x, prop_y = x + 17.78, y - 12.7
        else:
            prop_x, prop_y = x + 7.62, y - 5.08
        s.append(f'(property "Reference" {q(ref)} (at {fmt(prop_x)} {fmt(prop_y)} 0) (effects (font (size 1.27 1.27))))')
        s.append(f'(property "Value" {q(value)} (at {fmt(prop_x)} {fmt(prop_y + 2.54)} 0) (effects (font (size 1.27 1.27))))')
        s.append(f'(property "Footprint" {q(footprint)} (at {fmt(x)} {fmt(y)} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        s.append(f'(instances (project {q(self.name)} (path {q("/" + self.uuid)} (reference {q(ref)}) (unit 1))))')
        s.append(')')
        self.items.append("\n".join(s))
        for key, net in nets.items():
            if key not in sym.pins:
                raise ValueError(f"{sym.id} has no pin {key}; pins={sorted(sym.pins)}")
            px, py, angle = sym.pins[key]
            gx, gy = x + px, y - py
            if net is None:
                self.items.append(f'(no_connect (at {fmt(gx)} {fmt(gy)}) (uuid {q(uid())}))')
                continue
            dx = {0: -5.08, 180: 5.08, 90: 0, 270: 0}[angle]
            dy = {0: 0, 180: 0, 90: 5.08, 270: -5.08}[angle]
            ex, ey = gx + dx, gy + dy
            self.items.append(f'(wire (pts (xy {fmt(gx)} {fmt(gy)}) (xy {fmt(ex)} {fmt(ey)})) (stroke (width 0) (type default)) (uuid {q(uid())}))')
            self.items.append(f'(label {q(net)} (at {fmt(ex)} {fmt(ey)} 0) (effects (font (size 1.27 1.27))) (uuid {q(uid())}))')

    def note(self, text: str, x: float, y: float):
        self.items.append(f'(text {q(text)} (at {fmt(x)} {fmt(y)} 0) (effects (font (size 1.27 1.27))) (uuid {q(uid())}))')

    def save(self):
        header = f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(self.uuid)}) (paper {q(self.paper)}) (title_block (title {q(self.title)}) (rev "0.1") (comment 1 "Research prototype; electrical design requires review"))'
        lib = '(lib_symbols\n' + '\n'.join(s.raw for s in self.symbols.values()) + '\n)'
        path = OUT / f'{self.name}.kicad_sch'
        path.write_text(header + '\n' + lib + '\n' + '\n'.join(self.items) + '\n)\n', encoding='utf-8')
        return path


def inspect():
    for lib, name in [('Interface_Expansion', 'TCA9548APWR'), ('Sensor_Temperature', 'TMP102xxDRL'), ('Connector_Generic', 'Conn_01x04'), ('Device', 'R'), ('Device', 'C')]:
        sym = LibrarySymbol(lib, name)
        print(sym.id, sorted(sym.pins.items()))


def build_sensor_node() -> Path:
    s = Sheet('temperature-node', 'Mammary Protect - one temperature sensor node', 'A4')
    conn = LibrarySymbol('Connector_Generic', 'Conn_01x04')
    tmp = LibrarySymbol('Sensor_Temperature', 'TMP102xxDRL')
    cap = LibrarySymbol('Device', 'C')
    flag = LibrarySymbol('power', 'PWR_FLAG')
    s.place(conn, 'J1', 'TO_TEMPERATURE_HUB', 50.8, 76.2,
            {'1': '3V3', '2': 'GND', '3': 'SDA', '4': 'SCL'})
    s.place(tmp, 'U1', 'TMP102xxDRL', 132.08, 76.2,
            {'V+': '3V3', 'GND': 'GND', 'SDA': 'SDA', 'SCL': 'SCL', 'ADD0': 'GND', 'ALERT': None},
            'Package_TO_SOT_SMD:SOT-563')
    s.place(cap, 'C1', '10n', 198.12, 76.2, {'1': '3V3', '2': 'GND'},
            'Capacitor_SMD:C_0603_1608Metric')
    s.place(flag, '#FLG01', 'PWR_FLAG', 218.44, 66.04, {'1': '3V3'})
    s.place(flag, '#FLG02', 'PWR_FLAG', 218.44, 86.36, {'1': 'GND'})
    s.note('One identical node per selected patch position; 18 positions are a provisional target.', 127, 130)
    s.note('No local I2C pull-ups: each hub branch has its own pull-ups. Keep cable short.', 127, 140)
    s.note('Contact temperature is not an infrared thermal image; verify sensing method and placement.', 127, 150)
    return s.save()


def build_hub() -> Path:
    s = Sheet('temperature-hub', 'Mammary Protect - 18-position temperature I2C hub', 'A2')
    conn = LibrarySymbol('Connector_Generic', 'Conn_01x04')
    mux = LibrarySymbol('Interface_Expansion', 'TCA9548APWR')
    resistor = LibrarySymbol('Device', 'R')
    cap = LibrarySymbol('Device', 'C')
    flag = LibrarySymbol('power', 'PWR_FLAG')
    s.place(conn, 'J1', 'HOST_3V3_I2C', 63.5, 91.44,
            {'1': '3V3', '2': 'GND', '3': 'HOST_SDA', '4': 'HOST_SCL'})
    s.place(flag, '#FLG01', 'PWR_FLAG', 87.63, 120.65, {'1': '3V3'})
    s.place(flag, '#FLG02', 'PWR_FLAG', 87.63, 137.16, {'1': 'GND'})
    ref_r = 1
    for bank in range(3):
        x = 125.0 + 175.0 * bank
        i2c_address = 0x70 + bank
        nets: dict[str, str | None] = {
            'VCC': '3V3', 'GND': 'GND', 'SDA': 'HOST_SDA', 'SCL': 'HOST_SCL',
            '~{RESET}': f'RESET_{bank}',
            'A0': '3V3' if bank & 1 else 'GND',
            'A1': '3V3' if bank & 2 else 'GND',
            'A2': 'GND',
        }
        for channel in range(8):
            slot = bank * 6 + channel + 1
            nets[f'SD{channel}'] = f'SDA_{slot:02d}' if channel < 6 else None
            nets[f'SC{channel}'] = f'SCL_{slot:02d}' if channel < 6 else None
        s.place(mux, f'U{bank + 1}', f'TCA9548APWR 0x{i2c_address:02X}', x, 105,
                nets, 'Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm')
        s.place(cap, f'C{bank + 1}', '100n', x + 43.18, 100,
                {'1': '3V3', '2': 'GND'}, 'Capacitor_SMD:C_0603_1608Metric')
        s.place(resistor, f'R{ref_r}', '10k', x + 63.5, 100,
                {'1': '3V3', '2': f'RESET_{bank}'}, 'Resistor_SMD:R_0603_1608Metric')
        ref_r += 1
        for channel in range(6):
            slot = bank * 6 + channel + 1
            y = 165 + channel * 35
            sda, scl = f'SDA_{slot:02d}', f'SCL_{slot:02d}'
            s.place(conn, f'J{slot + 1}', f'SENSOR_{slot:02d}', x, y,
                    {'1': '3V3', '2': 'GND', '3': sda, '4': scl})
            s.place(resistor, f'R{ref_r}', '4k7', x + 38.1, y,
                    {'1': '3V3', '2': sda}, 'Resistor_SMD:R_0603_1608Metric')
            ref_r += 1
            s.place(resistor, f'R{ref_r}', '4k7', x + 68.58, y,
                    {'1': '3V3', '2': scl}, 'Resistor_SMD:R_0603_1608Metric')
            ref_r += 1
    s.note('HOST J1: connect to Raspberry Pi 4 3V3, GND, GPIO2/SDA1, GPIO3/SCL1.', 145, 35)
    s.note('pic0rick ultrasound acquisition is a separate USB module; no high-voltage path is on this hub.', 145, 45)
    s.note('Three I2C switches: 0x70, 0x71, 0x72; each active branch has one TMP102 node at 0x48.', 145, 55)
    s.note('Connector footprints, cable routing, total 3V3 load and skin-contact implementation require review.', 145, 65)
    return s.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inspect', action='store_true')
    args = parser.parse_args()
    if args.inspect:
        inspect()
    else:
        print(build_sensor_node())
        print(build_hub())
