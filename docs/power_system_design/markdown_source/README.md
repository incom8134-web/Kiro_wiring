# kiro_wiring – power rewiring design for the Kiro / SO-101 mobile dual-arm robot

Created 2026-10-22. All documents are in English.

| File | Content |
|---|---|
| `Kiro_SO101_Power_System_Design_RevA.docx` | **Main deliverable.** Complete electrical design package: context, load budget and calculations, SMPS and converter selection, protection and E-stop, five schematic sheets with reference designators and ratings, designator list, net list, cable schedule, assembly notes, parts list, image sources |
| `context.docx` | Project context: what the robot is, people and milestones, hardware inventory with serial numbers, current power and USB layout, electrical rules learned, goals, open questions |
| `power_calculation.docx` | Load budget per device and rail, SMPS and buck sizing, fuse groups, wire gauges and voltage drops, connectors, protections, E-stop, battery path, bring-up checklist |
| `parts_list.docx` | Bill of materials with specs, quantities, search terms and rough prices |
| `diagrams/schematic_sheet1..5.png` (+ `.svg`) | Electrical schematics: 1 AC input, SMPS, 12 V distribution, E-stop; 2 Jetson and 7.2 V follower rails; 3 5 V logic rail; 4 12 V wheel rail; 5 connector pinouts. Source: `schematic.py` (Python, schemdraw) |
| `diagrams/block_diagram.png`, `power_diagram.png`, `power_diagram_tb.png`, `wiring_diagram.png` | Graphviz overview diagrams (`.dot` sources alongside) |
| `images/web/` | Reference photos used in the Word document, with `sources.json` listing origin and licence |
| `markdown_source/` | Original Markdown versions of the text documents |

## Design in one paragraph

One Mean Well LRS-350-12 (12 V, 29 A) replaces all wall adapters. The wheel servos and the Jetson run
directly from 12 V (the Jetson jack accepts 9–20 V). Two 8 A class buck converters make 7.2 V for the
left and right follower arms (servo limit 8.0 V), one 5 A buck makes 5 V for the USB hub, the lidar and
both leader arms. Two blade fuse groups and a GND bus bar distribute power in a star: group A (Jetson, 5 V buck, spare) is
always on, group B (wheels, both follower bucks) hangs behind a 40 A relay driven by a mushroom E-stop and a key
switch, so a stop kills motion while the Jetson, hub, lidar and leaders stay powered. Design load is 17 A continuous and 27 A worst-case peak on the 12 V bus.

## Re-generating the drawings

```bash
cd diagrams && for f in block_diagram power_diagram power_diagram_tb wiring_diagram; do dot -Tpng -Gdpi=130 $f.dot -o $f.png; dot -Tsvg $f.dot -o $f.svg; done
python3 schematic.py        # needs: pip install schemdraw matplotlib
```
