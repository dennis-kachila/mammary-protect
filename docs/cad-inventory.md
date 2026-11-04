# CAD inventory

All Fusion 360 exports below were taken from open saved documents on 2026-11-04. `.f3d` files preserve editable Fusion design data. `.step` files are neutral geometry exports. Archive and STEP exports can differ in how references or component structure are represented.

| Export | Source document | Notes |
| --- | --- | --- |
| `almost-final-patch-v16.f3d`, `.step` | Almost final patch design v16 | Main patch iteration with strap attachment and weight-reduction cutouts |
| `breast-patch-v24.f3d`, `.step` | Breast Patch v24 | Earlier patch iteration |
| `probe-design-holder-v5.f3d`, `.step` | Probe Design Holder v5 | Angled probe and holder development; dimensions and magnet interface still need physical verification |
| `breast-holder-assembly-v3.f3d` | Breast Holder assembly v3 | Assembly archive; check references when opening |

Older mesh files in `cad/mesh/` were found in the local project folder and retained as historical iterations. Their exact relationship to the Fusion version history has not been established. In particular, a mesh filename is not evidence that it is the current design.

The OpenSCAD file is a separate parametric exploration. Some comments and parameter names in that early concept are inconsistent (for example, a variable called `magnet_hole_radius` is described as a diameter). Verify all dimensions from the geometry before manufacture.

## Mechanical decisions under review

- Two-magnet probe docking target: 30.5 mm center to center; magnets 3 mm diameter, 5 mm high.
- Hole pairs, path edge clearance, and strap holder positions were iterated by visual review in Fusion.
- Honeycomb cutouts were intended to leave solid material at mounts, corners, and load paths. No structural analysis or load test is included.
- The third strap holder was requested on the lower, opposite side of the patch. Verify its final position in the native model before making hardware.
