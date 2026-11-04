// Wearable Ultrasound Honeycomb Breast Patch Parameters
breast_curvature_radius = 110; // Subcutaneous radius to curve the patch around
patch_thickness = 3; // Thickness of the printed shell
honeycomb_radius = 10; // Outer radius of each cell in the honeycomb lattice
honeycomb_wall_thickness = 2.5; // Width of the plastic strut between empty cells
border_thickness = 4.5; // Solid perimeter envelope width
tracker_node_radius = 9; // Size of the 6 solid nodes for ultrasound tracker mounting
magnet_hole_radius = 1.6; // Diameter of insertion holes for small circular magnets
probe_track_width = 10; // 10mm traversal path width for the probe inside the groove
guard_rail_thickness = 1; // 1mm bottom floor layer so the path isn't completely hollow (acts as a rail)
guard_rail_wall_thickness = 2; // Sidewall reinforcement thickness to keep the probe inside the track over empty hexes

// The 6 node indices linked to form the continuous traversal slot
probe_path_sequence = [0,1,2,3,4,5]; 
patch_color = "GhostWhite"; // Structural filament styling

/* [Hidden] */
$fn = 60;
dx = honeycomb_radius * sqrt(3);
dy = honeycomb_radius * 1.5;

// The tracker guides are positioned at exact symmetrical indices [col, row] 
// to embed them continuously within the honeycomb node lattice.
tracker_coords = [
    [ 1,  3], // Node 0: Top Right Lobe
    [-2,  3], // Node 1: Top Left Lobe
    [-2,  1], // Node 2: Mid Left
    [ 1,  1], // Node 3: Mid Right
    [ 1, -3], // Node 4: Bottom Right
    [-2, -3]  // Node 5: Bottom Left
];

// Helper functions to get absolute X/Y 2D positions of individual nodes
function get_offset_x(row) = (abs(row) % 2 == 1) ? dx/2 : 0;
function get_node_pt(i) = [
    tracker_coords[i][0] * dx + get_offset_x(tracker_coords[i][1]),
    tracker_coords[i][1] * dy
];

color(patch_color)
difference() {
    // 1. Solid structural base bounded by the 3D contouring shell
    intersection() {
        translate([0, 0, -breast_curvature_radius + 15])
        difference() {
            sphere(r = breast_curvature_radius + patch_thickness, $fn = 120);
            sphere(r = breast_curvature_radius, $fn = 120);
        }

        translate([0, 0, -breast_curvature_radius])
        linear_extrude(height = breast_curvature_radius * 2.5)
        patch_2d_solid();
    }

    // 2. Etch the continuous path groove, leaving `guard_rail_thickness` intact at the bottom
    intersection() {
        translate([0, 0, -breast_curvature_radius + 15])
        difference() {
            // Subtraction envelope extends past the top of the shell to ensure clean removal
            sphere(r = breast_curvature_radius + patch_thickness + 1, $fn = 120);
            // Protect the floor layer by starting the cut higher up
            sphere(r = breast_curvature_radius + guard_rail_thickness, $fn = 120);
        }

        translate([0, 0, -breast_curvature_radius])
        linear_extrude(height = breast_curvature_radius * 2.5)
        probe_path_slot();
    }

    // 3. Drill complete access holes and magnet ports at the primary skin contact nodes
    translate([0, 0, -breast_curvature_radius])
    linear_extrude(height = breast_curvature_radius * 2.5)
    tracker_nodes_holes();
}

module patch_2d_solid() {
    union() {
        intersection() {
            patch_outline();
            union() {
                // A. Staggered hex structure
                difference() {
                    translate([-100, -100]) square([200, 200]);
                    base_hexagons(); 
                }
                
                // B. Base footprint of trackers
                tracker_nodes_solid();
                
                // C. Widened solid bed underneath the probe path to establish sturdy sidewalls
                probe_path_solid_bed();
            }
        }
        
        // D. Outer reinforced loop envelope
        difference() {
            patch_outline();
            offset(r = -border_thickness) patch_outline();
        }
    }
}

module patch_outline() {
    // Organic, asymmetrical teardrop resembling sports bra cup boundaries
    hull() {
        translate([0, -28]) circle(r = 58);
        translate([-25.98, 45]) circle(r = 23);
        translate([ 25.98, 45]) circle(r = 23);
    }
    
    // External alignment tabs
    translate([-57, -15]) square([8, 18], center=true);
    translate([ 57, -15]) square([8, 18], center=true);
}

module base_hexagons() {
    for(col = [-5 : 5]) {
        for(row = [-7 : 6]) {
            offset_x = (abs(row) % 2 == 1) ? dx/2 : 0;
            x = col * dx + offset_x;
            y = row * dy;
            
            translate([x, y])
            rotate(30)
            circle(r = honeycomb_radius - honeycomb_wall_thickness, $fn=6);
        }
    }
}

module tracker_nodes_solid() {
    for (i = [0 : len(tracker_coords) - 1]) {
        translate(get_node_pt(i))
        rotate(30)
        circle(r = tracker_node_radius, $fn=6);
    }
}

module tracker_nodes_holes() {
    for (i = [0 : len(tracker_coords) - 1]) {
        translate(get_node_pt(i)) {
            // Complete cutout purely at skin contact node point (cuts right through the rail)
            circle(d = probe_track_width, $fn=36);
            
            // Outer 120-degree phase magnets
            for(a = [90, 210, 330]) {
                rotate(a)
                translate([tracker_node_radius * 0.55, 0])
                circle(r = magnet_hole_radius, $fn=24);
            }
        }
    }
}

module probe_path_solid_bed() {
    // Solid widened foundation so the track boolean has substantial material sidewalls to cut through
    if (len(probe_path_sequence) > 1) {
        for (i = [0 : len(probe_path_sequence) - 2]) {
            idx1 = probe_path_sequence[i];
            idx2 = probe_path_sequence[i+1];
            hull() {
                translate(get_node_pt(idx1)) circle(d = probe_track_width + guard_rail_wall_thickness * 2, $fn=36);
                translate(get_node_pt(idx2)) circle(d = probe_track_width + guard_rail_wall_thickness * 2, $fn=36);
            }
        }
    }
}

module probe_path_slot() {
    // Exact inner dimension footprint of the 10mm traversal path
    if (len(probe_path_sequence) > 1) {
        for (i = [0 : len(probe_path_sequence) - 2]) {
            idx1 = probe_path_sequence[i];
            idx2 = probe_path_sequence[i+1];
            hull() {
                translate(get_node_pt(idx1)) circle(d = probe_track_width, $fn=36);
                translate(get_node_pt(idx2)) circle(d = probe_track_width, $fn=36);
            }
        }
    }
}