# Kiro Robot – 3D Design & Printing Guideline

All Kiro robot body parts are printed in-house on a **Bambu Lab P1S**. Design every part so it prints on that machine without rework.

## 1. Printer limits (Bambu Lab P1S)

| Item | Value |
|---|---|
| Build volume | 256 × 256 × 256 mm |
| **Design limit per part** | **≤ 245 × 245 × 245 mm** (leave margin for brim / purge) |
| Nozzle | 0.4 mm (standard) |
| Enclosure | Yes – PLA, PETG, ABS, ASA all OK |

**Rule:** if a part's bounding box exceeds 245 mm on any axis, split it (see section 2).

## 2. Splitting large parts – dovetail joints

Use dovetails to join split parts. Reference values (proven on the cart power plate):

| Parameter | Value |
|---|---|
| Neck width | 10 mm |
| Head width | 16 mm |
| Depth | 9 mm |
| Clearance | 0.15 mm per side (cut on the socket side only) |
| Spacing | one dovetail every 60–80 mm along the seam, min. 2 per seam |

Rules:
- Put seams on **flat, low-load areas** – never through a screw boss, motor mount, hinge or thin wall.
- Keep a **solid band ≥ 6 mm** on each side of the seam (no holes, honeycomb or text there).
- Dovetails slide in the print's **XY plane** (part lying flat) so the joint isn't weak along layer lines.
- Lock every joint: **CA glue or epoxy**, plus an M3 screw across the seam on load-bearing parts.
- Print a small **test coupon** of the joint first when you change material or clearance.

## 3. Design rules

| Feature | Rule |
|---|---|
| Wall / plate thickness | ≥ 2.4 mm walls, ≥ 4–5 mm for base plates |
| Overhangs | ≤ 45° without supports; add a chamfer instead of a flat overhang |
| Bridges | ≤ 20 mm |
| Hole clearance | +0.2 to +0.3 mm on diameter (M3 → 3.3–3.4 mm) |
| Heat-set inserts M3 | hole Ø 4.0–4.2 mm, depth = insert length + 1 mm |
| Self-tap M3 pilot | Ø 2.6 mm |
| Slip fit between parts | 0.2 mm per side |
| Fillets | Round outer corners (R ≥ 2 mm) – reduces warping and looks finished |
| Text / labels | Engrave 0.6–0.8 mm deep, ≥ 5 mm tall, on the top face |
| Weight / filament saving | Hex cut-outs (10 mm hole, 2.6 mm rib) in non-structural areas |
| Electronics | Raise boards ~10 mm on standoffs for airflow; add zip-tie slots along cable routes |

## 4. Print orientation & settings

- Design each part with its **largest flat face as Z = 0** – no supports if possible.
- Layer lines are weakest in Z: orient so loads run **along** the layers.
- Default settings: 0.2 mm layers, 3 walls, 15–20 % infill (gyroid), 25–40 % for load-bearing parts.

| Material | Use for |
|---|---|
| PLA | Cosmetic covers, prototypes, cool areas |
| PETG | General structure, parts near electronics |
| ASA / ABS | Parts near motors, SMPS or other heat (P1S enclosure closed) |

## 5. File & handoff rules

- Units **mm**, **Z up**, part placed flat on Z = 0.
- Deliver **`.step`** (editable, Fusion 360) **and `.3mf`** (print-ready) for every part.
- Naming: `kiro_<assembly>_<part>_<A|B..>_v<N>.step` – e.g. `kiro_base_plate_A_v2.3mf`.
- Split parts get letters (A, B, C…) and the seam is noted in the file or README.
- Keep source parametric (Fusion timeline or script) so sizes can be edited later.

## 6. Pre-print checklist

- [ ] Every part fits within 245 × 245 × 245 mm
- [ ] Large parts split with dovetails, seams away from load points
- [ ] Hole / insert / fit clearances applied
- [ ] No overhang > 45° without a chamfer or support plan
- [ ] Flat face down, orientation checked for strength
- [ ] Mesh is a single, closed (watertight) body
- [ ] `.step` + `.3mf` exported with the correct name and version
