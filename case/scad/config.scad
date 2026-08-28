// config.scad - Shared Dimensions & Configuration

$fn = 60;

// ENCLOSURE DIMENSIONS (mm)
box_w = 228;   // Width (X)
box_d = 145;   // Depth (Y)
box_h = 140;   // Height (Z)
wall  = 2.8;   // Wall thickness
corner_r = 10; // Vintage rounded corner radius

// PREVIEW COLOR
wood_color = [0.35, 0.20, 0.10];

// SPEAKER BAY
spk_hole_dia   = 80;   // Front sound cutout
spk_bay_dia    = 112;  // Internal clearance
spk_bay_depth  = 100;
spk_x = 62.5;
spk_z = box_h / 2;

// 1602 LCD WINDOW
lcd_win_w = 73;
lcd_win_h = 25.5;
lcd_x     = 175;
lcd_z     = 105;
// CONTROLS
pot_x     = 155;
pot_z     = 35;
pot_hole  = 7.2;

btn_x     = 205;
btn_z     = 35;

// Button plunger & guide sleeve
btn_cap_dia           = 10;
btn_cap_recess_depth  = 1.6;
btn_shaft_hole_dia    = 4.6;
btn_sleeve_od         = 8.0;
btn_sleeve_len        = 6.0;
btn_switch_pad_w      = 8.0;
btn_switch_pad_d      = 8.0;
btn_switch_standoff_h = 8.0;

btn_plunger_shaft_len = 14;
btn_plunger_shaft_dia = 4.2;
btn_plunger_cap_h     = 1.4;

// REAR POWER CUTOUT (USB-C)
pwr_w = 14;
pwr_h = 9;
pwr_z = 18;

// INTERNAL MOUNTING STANDOFFS
// Raspberry Pi
pi_x = 8;
pi_y = 103;
pi_w = 110;
pi_d = 35;

// Arduino
ard_x = 150;
ard_y = 80;
ard_w = 65;
ard_d = 50;
ard_standoff_h = 5;

// USB Hub
hub_x = 130;
hub_y = 40;
hub_w = 100;
hub_d = 30;
hub_riser_h = 20;