# Kenya KES 30,000 draft bill of materials

The supplied [Word worksheet](Mammary_Protect_BOM_Kenya_30000.docx) is preserved here as a historical source. Its 23 line items were transcribed into a [searchable CSV](Mammary_Protect_BOM_Kenya_30000.csv), including the supplier links embedded in the document. The listed amounts add to **KES 30,000**. The file was last modified on 29 October 2026; its prices and supplier availability have not been rechecked.

This is a **partial materials and accessories budget**, not a complete cost to build the present design. It does not list the GM100 probe, pic0rick or another ultrasound acquisition chain, Raspberry Pi or other controller, TMP102 sensors, TCA9548A switches, PCB fabrication, power design, or a thermal camera. The 18 proposed sensor locations in the KiCad design remain provisional.

| Worksheet item | Draft | Current KiCad schematic |
| --- | --- | --- |
| Sensor connectors | 20 pairs of 3-pin connectors | One host connector plus 18 sensor connections, each 4-pin; connector type and footprints still unselected |
| 4.7 kΩ pull-ups | 10 | 36 for the 18 isolated SDA/SCL branches |
| 100 nF capacitors | 20 | 3 on the hub; each of 18 sensor nodes instead has a 10 nF bypass capacitor |
| Temperature ICs and I²C switches | Not listed | 18 TMP102 nodes and 3 TCA9548A switches proposed |
| 3 × 5 mm magnets | 18, KES 13,410 | Mechanical count and fit still under review |

The colored wire rows describe “1 Metre” in the item name but “1 (90m roll)” in the quantity column; that inconsistency remains in the source and needs clarification before purchasing. The magnet row alone represents 44.7% of the draft total. The supplier links are retained as historical references, not buying recommendations.

The [KiCad BOM exports](../../electronics/kicad/) reflect the schematic components and provide the better starting point for a revised electronics budget. Neither the original worksheet nor those exports are yet a procurement-ready BOM.
