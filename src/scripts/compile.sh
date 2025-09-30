#!/bin/bash
# Sumo Book Compilation Script

echo "Compiling Sumo Wrestling Book..."

# Check for LaTeX installation
if ! command -v pdflatex &> /dev/null; then
    echo "Error: pdflatex not found. Please install LaTeX (TeX Live or MiKTeX)"
    echo "On macOS: brew install mactex"
    echo "On Ubuntu: sudo apt-get install texlive-full"
    exit 1
fi

# Compile with bibliography
echo "First pass..."
pdflatex main.tex

echo "Generating bibliography..."
biber main

echo "Second pass..."
pdflatex main.tex

echo "Final pass..."
pdflatex main.tex

echo "Done! Output: main.pdf"

# Clean up auxiliary files
rm -f main.aux main.bbl main.bcf main.blg main.log main.out main.run.xml main.toc main.lof main.lot main.idx main.ilg main.ind