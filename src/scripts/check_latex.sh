#!/bin/bash

echo "LaTeX Document Check Report"
echo "==========================="
echo ""

# Check for unmatched braces
echo "1. Checking for unmatched braces in main.tex..."
awk 'BEGIN{open=0} {for(i=1;i<=length($0);i++){c=substr($0,i,1); if(c=="{")open++; if(c=="}")open--} if(open!=0)print "Line " NR ": Possible brace mismatch (running count: " open ")"} END{if(open!=0)print "ERROR: Unmatched braces. Open braces: " open}' main.tex

echo ""
echo "2. Checking for undefined commands..."
grep -n "\\\\japterm\|\\\\kimarite" chapters/*.tex | head -5

echo ""
echo "3. Checking bibliography..."
if [ -f references.bib ]; then
    echo "✓ references.bib exists"
    # Check for basic bib syntax
    grep -c "@" references.bib | xargs -I {} echo "  Found {} bibliography entries"
else
    echo "✗ references.bib missing"
fi

echo ""
echo "4. Checking for common LaTeX errors..."
# Check for & outside tables
grep -n "&" main.tex chapters/*.tex 2>/dev/null | grep -v "\\\\begin{" | grep -v "\\\\end{" | head -5

echo ""
echo "5. Package dependencies check..."
echo "Essential packages used:"
grep "\\\\usepackage" main.tex | sed 's/.*usepackage\[\?\(.*\)\]\?{\(.*\)}.*/  - \2/' | head -10

echo ""
echo "6. File structure check..."
echo "  Main file: main.tex"
echo "  Chapters: $(ls chapters/*.tex 2>/dev/null | wc -l) files"
echo "  Appendices: $(ls appendices/*.tex 2>/dev/null | wc -l) files"

