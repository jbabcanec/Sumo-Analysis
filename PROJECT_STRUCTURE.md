# Sumo LaTeX Project Structure

## Directory Organization

```
.
├── main.tex                 # Main LaTeX document
├── main.pdf                 # Compiled PDF output
├── compile.sh               # Build script
│
├── src/                     # Source files
│   ├── content/            # Document content
│   │   ├── 00_frontmatter/ # Preface and introduction
│   │   ├── 01_foundations/ # Part 1: Basic chapters
│   │   ├── 02_analysis/    # Part 2: Statistical analysis
│   │   ├── 03_advanced/    # Part 3: Advanced topics
│   │   └── 04_appendices/  # Appendices
│   ├── references.bib      # Bibliography
│   ├── scripts/            # Utility scripts
│   └── styles/             # Custom LaTeX styles (future)
│
├── build/                   # Build artifacts (auto-generated)
│   └── [*.aux, *.log, etc] # LaTeX auxiliary files
│
├── temp/                    # Temporary files
│   └── [test files]        # Test documents and examples
│
├── docs/                    # Documentation
│   ├── README.md
│   ├── chapter_outlines.md
│   └── latex_test.md
│
├── database/               # Data files
└── papers/                 # Reference papers

```

## Building the Document

To compile the LaTeX document:
```bash
./compile.sh
```

This will:
1. Run pdflatex three times
2. Process bibliography with biber
3. Move all auxiliary files to `build/`
4. Output final PDF as `main.pdf`

## Chapter Organization

Each chapter/section is in its own file within the appropriate part:

- **Frontmatter**: Preface
- **Part 1 - Foundations**: History, Prior Work, Data, Measurement, Descriptive Stats
- **Part 2 - Analysis**: Statistical Models, Causality
- **Part 3 - Advanced**: Injuries, Forecasting, Case Studies, Future Directions
- **Part 4 - Appendices**: Data Dictionary, Kimarite Catalog, Code, Statistical Methods

## Japanese/Kanji Support

The document supports Japanese characters using CJKutf8:
- Use `\ja{日本語}` for inline Japanese text
- Use `\japterm{English}{日本語}` for terms with translations

## Clean Build

All build artifacts (.aux, .log, .toc, etc.) are automatically moved to the `build/` directory to keep the root clean.