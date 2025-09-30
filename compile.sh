#!/bin/bash
# Clean LaTeX compilation script

echo "Compiling LaTeX document..."

# First pass
pdflatex -interaction=nonstopmode main.tex

# Run biber for bibliography
biber main

# Second pass (for references)
pdflatex -interaction=nonstopmode main.tex

# Third pass (for final formatting)
pdflatex -interaction=nonstopmode main.tex

# Move all auxiliary files to build directory
mkdir -p build
mv *.aux *.toc *.lof *.lot *.log *.out *.bbl *.bcf *.blg *.idx *.run.xml build/ 2>/dev/null || true
mv src/content/*/*.aux build/ 2>/dev/null || true
mv src/content/*/*/*.aux build/ 2>/dev/null || true

echo "Compilation complete!"
echo "PDF: main.pdf"
echo "Build artifacts in: build/"
