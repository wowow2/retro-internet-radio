 // button_plunger.scad - Standalone Button Plunger

include <config.scad>

module button_plunger() {
    cylinder(d = btn_plunger_shaft_dia, h = btn_plunger_shaft_len);
    translate([0, 0, -btn_plunger_cap_h])
        cylinder(d = btn_cap_dia - 0.4, h = btn_plunger_cap_h + 0.05);
}

// Render self
button_plunger();