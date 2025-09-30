#!/bin/bash

# Move preface
cp chapters/00_preface.tex content/frontmatter/preface/main.tex

# Part 1: Foundations
cp chapters/01_history.tex content/part1_foundations/ch01_history/main.tex
cp chapters/02_prior_work.tex content/part1_foundations/ch02_prior_work/main.tex
cp chapters/03_data_infrastructure.tex content/part1_foundations/ch03_data_infrastructure/main.tex
cp chapters/04_measurement.tex content/part1_foundations/ch04_measurement/main.tex
cp chapters/05_descriptive.tex content/part1_foundations/ch05_descriptive/main.tex

# Part 2: Analysis
cp chapters/06_models.tex content/part2_analysis/ch06_models/main.tex
cp chapters/07_causality.tex content/part2_analysis/ch07_causality/main.tex

# Part 3: Advanced Topics
cp chapters/08_injuries.tex content/part3_advanced/ch08_injuries/main.tex
cp chapters/09_forecasting.tex content/part3_advanced/ch09_forecasting/main.tex
cp chapters/10_case_studies.tex content/part3_advanced/ch10_case_studies/main.tex
cp chapters/11_future.tex content/part3_advanced/ch11_future/main.tex

# Part 4: Appendices
cp appendices/A_data_dictionary.tex content/part4_appendices/A_data_dictionary/main.tex
cp appendices/B_kimarite_catalog.tex content/part4_appendices/B_kimarite_catalog/main.tex
cp appendices/C_code_repository.tex content/part4_appendices/C_code_repository/main.tex
cp appendices/D_statistical_methods.tex content/part4_appendices/D_statistical_methods/main.tex

echo "Files copied to new structure"