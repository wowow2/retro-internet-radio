// utils.scad - Reusable 3D Geometry Modules

include <config.scad>

// 3D Rounded Box with Spherical Fillets
module rounded_box(w, d, h, r) {
    hull() {
        translate([r, r, r]) sphere(r);
        translate([w - r, r, r]) sphere(r);
        translate([r, d - r, r]) sphere(r);
        translate([w - r, d - r, r]) sphere(r);
        translate([r, r, h - r]) sphere(r);
        translate([w - r, r, h - r]) sphere(r);
        translate([r, d - r, h - r]) sphere(r);
        translate([w - r, d - r, h - r]) sphere(r);
    }
}

// 2D Rounded Plate Extrusion
module rounded_plate(w, h, thickness, r) {
    linear_extrude(height = thickness)
        offset(r = r) offset(delta = -r) square([w, h]);
}

// 4-Corner Standoff Array
module standoff_block(x, y, w, d, standoff_h, hole_d = 2.4, boss_d = 6) {
    margin = 4;
    for (dx = [margin, w - margin])
        for (dy = [margin, d - margin])
            translate([x + dx, y + dy, wall])
                difference() {
                    cylinder(d = boss_d, h = standoff_h);
                    translate([0, 0, -0.1])
                        cylinder(d = hole_d, h = standoff_h + 0.2);
                }
}