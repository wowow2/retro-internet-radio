 // back_lid.scad - Rear Panel with Vents & USB Cutout

include <config.scad>
include <utils.scad>

module radio_back_lid() {
    difference() {
        union() {
            // Main back plate
            rotate([90, 0, 0])
                rounded_plate(box_w, box_h, wall, corner_r);

            // Inset snap lip
            translate([wall + 0.5, 0, wall + 0.5])
                cube([box_w - 2*wall - 1, 4, box_h - 2*wall - 1]);
        }

        // Hollow out lip interior
        translate([wall + 3, -1, wall + 3])
            cube([box_w - 2*wall - 6, 6, box_h - 2*wall - 6]);

        // USB-C Power cutout
        translate([box_w - 30, -wall - 2, pwr_z])
            cube([pwr_w, wall * 4, pwr_h]);

        // Ventilation slots
        for (vz = [40 : 12 : box_h - 30])
            translate([35, -wall - 2, vz])
                cube([box_w - 70, wall * 4, 4]);
    }
}

// Render self when opened directly
color(wood_color) radio_back_lid();