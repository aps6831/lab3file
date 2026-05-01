# KD vs MIS-C cfRNA Machine Learning Pipeline

This project analyzes cell-free RNA (cfRNA) data to classify Kawasaki Disease
(KD) vs MIS-C. The scripts are numbered in the order they should be run. Each
script can be run independently after the scripts it depends on have produced
their output files.

## Input Files

Place the lab data in a `data_ML` folder either inside this project folder or one
level above it:

```text
data_ML/metadata_all_UCSD_MISC.csv
data_ML/counts_all_UCSD_MISC.csv
```

For gene-symbol mapping, the pipeline also looks for:

```text
ensembl_ids_feb2026.tsv
```

The scripts search both the project folder and the parent `Downloads` folder for
the annotation file. If a gene cannot be mapped, the Ensembl ID is kept.

## Required Python Packages

Core analysis:

```bash
pip install numpy pandas scipy scikit-learn matplotlib
```

Dashboard:

```bash
pip install streamlit
```

Optional gene mapping:

```bash
pip install mygene
```

The local `ensembl_ids_feb2026.tsv` annotation file is preferred when available,
so `mygene` is not required for this dataset.

## Run Order

Run scripts from the project root:

```bash
python3 01_data_inspection.py
python3 02_preprocessing.py
python3 03_exploratory_analysis.py
python3 04_differential_expression_volcano.py
python3 05_baseline_logistic_regression.py
python3 06_lasso_elasticnet_model.py
python3 07_model_comparison.py
python3 08_map_genes.py
python3 09_biological_interpretation.py
streamlit run app.py
```

All generated files are saved in `outputs/`.

## Script Outputs

| Script | Purpose | Main outputs |
| --- | --- | --- |
| `01_data_inspection.py` | Checks dimensions, sample matching, class balance, and missing values. | `outputs/data_inspection_summary.txt` |
| `02_preprocessing.py` | Filters low-count genes, computes CPM, applies `log2(CPM + 1)`, and checks library sizes. | `outputs/logCPM_filtered.csv`, `outputs/library_sizes.csv`, `outputs/library_size_histogram.png` |
| `03_exploratory_analysis.py` | Performs PCA and QC comparisons by diagnosis. | `outputs/pca_by_diagnosis.png`, `outputs/library_size_by_diagnosis.png`, `outputs/age_by_diagnosis.png` |
| `04_differential_expression_volcano.py` | Computes gene-wise KD vs MIS-C statistics, Benjamini-Hochberg adjusted p-values, and volcano plot. | `outputs/differential_expression_results.csv`, `outputs/volcano_plot.png` |
| `05_baseline_logistic_regression.py` | Trains a baseline logistic regression model using the top 100 DE genes. | `outputs/baseline_logistic_metrics.txt`, `outputs/baseline_logistic_roc_curve.png`, `outputs/baseline_logistic_confusion_matrix.png` |
| `06_lasso_elasticnet_model.py` | Compares LASSO and elastic net logistic regression with repeated nested CV and saves selected coefficients. | `outputs/lasso_elasticnet_model_performance.csv`, `outputs/lasso_elasticnet_roc_curves.png`, `outputs/l1_logistic_regression_confusion_matrix.png`, `outputs/elastic_net_logistic_regression_confusion_matrix.png`, `outputs/selected_gene_coefficients.csv` |
| `07_model_comparison.py` | Compares LASSO, elastic net, random forest, linear SVM, and gradient boosting using the same split/CV strategy and top 500 DE genes. | `outputs/model_comparison_summary.csv`, `outputs/model_comparison_roc_plot.png` |
| `08_map_genes.py` | Maps selected Ensembl gene IDs to gene symbols. | `outputs/selected_gene_coefficients_mapped.csv` |
| `09_biological_interpretation.py` | Ranks positive and negative model coefficients and plots the top selected genes. | `outputs/selected_gene_biological_interpretation.csv`, `outputs/top20_selected_gene_coefficients.png` |
| `app.py` | Streamlit dashboard for exploring the dataset and outputs. | Interactive app at `http://localhost:8501` |

## Notes

- Positive model coefficients push predictions toward MIS-C.
- Negative model coefficients push predictions toward KD.
- `06_lasso_elasticnet_model.py` and `07_model_comparison.py` may take longer
  than the earlier scripts because they tune machine-learning models.
- Shared paths and labels live in `cfrna_paths.py` so the scripts use consistent
  input and output locations.
