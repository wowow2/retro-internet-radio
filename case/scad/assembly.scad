 // assembly.scad - Full Visual Preview

include <config.scad>
use <front_body.scad>
use <back_lid.scad>
use <button_plunger.scad>

// Front Enclosure
color(wood_color)
    radio_front_body();

// Rear Lid (separated for viewing)
color(wood_color)
    translate([0, box_d + 30, 0])
    radio_back_lid();

// Button Plunger (separated for viewing)
color([0.2, 0.2, 0.2])
    translate([btn_x, box_d + 50, 0])
    button_plunger();