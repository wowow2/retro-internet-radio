#!/bin/bash
set -e

# Ensure output directories exist
mkdir -p case/stl case/preview

echo "=========================================="
echo "   RENDERING RETRO RADIO 3D ASSETS       "
echo "=========================================="

echo "[1/6] Rendering Front Body STL..."
openscad -o case/stl/front_body.stl case/scad/front_body.scad

echo "[2/6] Rendering Back Lid STL..."
openscad -o case/stl/back_lid.stl case/scad/back_lid.scad

echo "[3/6] Rendering Button Plunger STL..."
openscad -o case/stl/button_plunger.stl case/scad/button_plunger.scad

echo "[4/6] Rendering Full Combined Assembly STL..."
openscad -o case/stl/full_assembly.stl case/scad/assembly.scad

echo "[5/6] Generating High-Res Outer 3D Preview (preview.png)..."
openscad -o case/preview/preview.png case/scad/assembly.scad \
    --imgsize=1920,1080 \
    --viewall \
    --autocenter \
    --colorscheme=Cornfield \
    --preview
echo "=========================================="
echo " Done! All files generated:"
echo "   -> case/stl/front_body.stl"
echo "   -> case/stl/back_lid.stl"
echo "   -> case/stl/button_plunger.stl"
echo "   -> case/stl/full_assembly.stl"
echo "   -> case/preview/preview.png"
echo "=========================================="