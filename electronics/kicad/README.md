# KiCad temperature-sensing prototype

Open `temperature-hub.kicad_sch` or `temperature-node.kicad_sch` in KiCad 10's Schematic Editor. These are the editable schematic sources; PDF files and PNG previews are included for quick review. A PCB project has not been created yet. `generate.py` records how the initial schematics were constructed from KiCad's installed standard symbol libraries.

## Proposed wiring

The hub has three TCA9548A I²C switches at addresses `0x70`, `0x71`, and `0x72`. Six channels of each switch feed one identical TMP102 sensor node, for 18 proposed positions. The two spare channels on each switch are marked as unconnected. Each downstream bus has its own 4.7 kΩ SDA and SCL pull-up resistors. The node's ADD0 pin is grounded, making its 7-bit address `0x48` on its isolated branch. TI specifies the address selection and recommends approximately 5 kΩ bus pull-ups and a 0.01 µF supply bypass capacitor. [TMP102 datasheet](https://www.ti.com/lit/ds/symlink/tmp102.pdf), [TCA9548A datasheet](https://www.ti.com/lit/ds/symlink/tca9548a.pdf)

| Hub connector J1 pin | Signal | Proposed Raspberry Pi 4 header connection |
| --- | --- | --- |
| 1 | 3V3 | Physical pin 1 |
| 2 | GND | Physical pin 6 |
| 3 | HOST_SDA | Physical pin 3, GPIO2/SDA1 |
| 4 | HOST_SCL | Physical pin 5, GPIO3/SCL1 |

The Raspberry Pi's GPIO2 and GPIO3 have fixed 1.8 kΩ pull-ups, so the proposed host bus has no additional pull-ups on the hub. [Raspberry Pi hardware documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)

Each sensor connector J2–J19 uses the same pin order: `3V3`, `GND`, `SDA`, `SCL`. The connector footprint is intentionally unassigned until the wearable cable, strain relief, and board placement are selected. The TMP102 ALERT output is unused. The hub has no ultrasound high-voltage wiring.

## Scope and checks

- These are schematic-stage designs. There is no PCB layout or fabricated board yet.
- The 18 contact-temperature positions are provisional. A TMP102 on a small board measures local board temperature; its coupling to skin and its relationship to the proposed thermal-imaging concept require experiments.
- Supply current, cable capacitance, I²C rise times, connector retention, mechanical fit, temperature accuracy, and electrical isolation have not been measured.
- The exact ultrasound probe and its transmit/receive pins must be identified before adapting any pulser board. The [pic0rick](https://github.com/kelu124/pic0rick) reference targets a 5 MHz single-element contact probe in its setup guide, while the candidate probe discussed for this project is dual-element.
- KiCad ERC reported zero violations for both schematics. ERC cannot establish that a wearable device is safe for human use.

The KiCad PDF exports, netlists, and ERC reports are generated review artifacts. Edit the `.kicad_sch` files and run ERC again after any change.
