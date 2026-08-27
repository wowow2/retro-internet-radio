 // front_body.scad - Main Front Enclosure Shell

include <config.scad>
include <utils.scad>

module lcd_standoffs() {
    hole_pitch_x = 75.0;
    hole_pitch_z = 31.0;

    translate([lcd_x, wall, lcd_z]) {
        for (dx = [-hole_pitch_x/2, hole_pitch_x/2]) {
            for (dz = [-hole_pitch_z/2, hole_pitch_z/2]) {
                translate([dx, 0, dz])
                    rotate([-90, 0, 0])
                    difference() {
                        cylinder(d = 6, h = 6);
                        translate([0, 0, -0.1])
                            cylinder(d = 2.4, h = 6.2);
                    }
            }
        }
    }
}

module button_boss_internals() {
    translate([btn_x, wall, btn_z])
        rotate([-90, 0, 0])
        difference() {
            cylinder(d = btn_sleeve_od, h = btn_sleeve_len);
            translate([0, 0, -0.1])
                cylinder(d = btn_shaft_hole_dia, h = btn_sleeve_len + 0.2);
        }

    translate([btn_x - btn_switch_pad_w/2, wall + btn_sleeve_len, btn_z - btn_switch_pad_d/2])
        cube([btn_switch_pad_w, btn_switch_standoff_h, btn_switch_pad_d]);
}

module radio_front_body() {
    difference() {
        rounded_box(box_w, box_d, box_h, corner_r);

        // Hollow interior
        translate([wall, wall, wall])
            rounded_box(box_w - 2*wall, box_d * 2, box_h - 2*wall, corner_r - wall);

        // Speaker opening
        translate([spk_x, -1, spk_z])
            rotate([-90, 0, 0])
            cylinder(d = spk_hole_dia, h = wall + 2);

        // LCD window
        translate([lcd_x - lcd_win_w/2, -1, lcd_z - lcd_win_h/2])
            cube([lcd_win_w, wall + 2, lcd_win_h]);

        // Potentiometer shaft hole
        translate([pot_x, -1, pot_z])
            rotate([-90, 0, 0])
            cylinder(d = pot_hole, h = wall + 2);

        // Button recess + shaft hole
        translate([btn_x, -0.1, btn_z])
            rotate([-90, 0, 0])
                cylinder(d = btn_cap_dia, h = btn_cap_recess_depth + 0.1);

        translate([btn_x, -1, btn_z])
            rotate([-90, 0, 0])
                cylinder(d = btn_shaft_hole_dia, h = wall + 2);
    }

    // Interior Standoffs
    lcd_standoffs();
    button_boss_internals();
    standoff_block(pi_x, pi_y, pi_w, pi_d, standoff_h = 4);
    standoff_block(ard_x, ard_y, ard_w, ard_d, standoff_h = ard_standoff_h);
    standoff_block(hub_x, hub_y, hub_w, hub_d, standoff_h = hub_riser_h, boss_d = 8);
}

// Render self when opened directly
color(wood_color) radio_front_body();