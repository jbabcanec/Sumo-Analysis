# Sumo Wrestling: The Complete Data Analysis

## Project Overview
Complete quantitative analysis of professional sumo wrestling using every bout from 1958-present (~50,000 bouts, 400+ tournaments).

## Structure

```
Sumo/
├── database/
│   ├── setup.sql              # Complete database schema
│   ├── bulk_import.py         # Downloads entire 1958-present dataset
│   └── sumo.db               # SQLite database (~100MB when complete)
├── papers/                   # Research papers (PDFs)
├── chapters/                 # LaTeX book chapters
├── main.tex                  # Book compilation
└── references.bib            # Citations
```

## The Database

**Complete sumo data 1958-2024:**
- ~50,000 individual bouts
- ~2,000 active/historical wrestlers  
- 400+ tournaments
- Every kimarite (winning technique)
- Complete injury/absence records (kyujo)
- Wrestler anthropometrics and origins

**To build the database:**
```bash
cd database/
python bulk_import.py
```

This downloads everything from Sumo-API and builds a complete SQLite database.

## Key Research Questions

1. **Injury Prediction**: Can we predict career-ending injuries using bout patterns?
2. **Technique Evolution**: How have winning techniques changed 1958-2024?
3. **Foreign Wrestler Impact**: Effect of international wrestlers on technique diversity
4. **Rank Inflation**: Are modern rankings easier to achieve than historical?
5. **7-7 Anomalies**: Evidence for strategic throwing in crucial bouts

## Sample Queries

```sql
-- Career win rates by era
SELECT 
  CASE 
    WHEN debut_date < '1990-01-01' THEN 'Classic Era'
    WHEN debut_date < '2010-01-01' THEN 'Modern Era'
    ELSE 'International Era'
  END as era,
  AVG(total_wins * 1.0 / (total_wins + total_losses)) as win_rate,
  COUNT(*) as wrestler_count
FROM wrestler_stats 
WHERE total_wins + total_losses > 100
GROUP BY era;

-- Most dominant kimarite by decade
SELECT 
  (year/10)*10 as decade,
  kimarite,
  COUNT(*) as frequency,
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY (year/10)*10) as percentage
FROM bouts b 
JOIN tournaments t ON b.tournament_id = t.id
GROUP BY decade, kimarite
ORDER BY decade, frequency DESC;
```

## Papers Collected
- ✅ Ota et al. (2023) - Injury prediction using Hawkes processes  
- [ ] Duggan & Levitt (2002) - Match fixing analysis
- [ ] Body composition studies
- [ ] ACL injury case series

## Current Status
- Database schema: ✅ Complete
- Bulk import script: ✅ Ready  
- Data collection: ⏳ In progress (run bulk_import.py)
- Analysis: ⏳ Pending data
- Writing: 📝 2/11 chapters drafted