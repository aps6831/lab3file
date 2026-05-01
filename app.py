"""
Streamlit dashboard for the KD vs MIS-C cfRNA machine-learning lab.

Run with:
    streamlit run app.py

The app reads the CSV and PNG artifacts produced by scripts 01-09 and presents
the main quality-control, exploratory, modeling, and gene-interpretation results.
"""

import pandas as pd
import streamlit as st

from cfrna_paths import OUTPUT_DIR, metadata_path


@st.cache_data
def load_csv(path):
    """Load a CSV file with Streamlit caching for faster dashboard refreshes."""
    return pd.read_csv(path)


def show_image(path, caption):
    """Display an output image if it exists, otherwise show a helpful warning."""
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.warning(f"Missing figure: {path}")


def show_table(path, title):
    """Display a CSV table if it exists."""
    st.subheader(title)
    if path.exists():
        st.dataframe(load_csv(path), use_container_width=True)
    else:
        st.warning(f"Missing table: {path}")


def main():
    """Render the Streamlit app."""
    st.set_page_config(page_title="KD vs MIS-C cfRNA Explorer", layout="wide")

    st.title("KD vs MIS-C cfRNA Dataset Explorer")
    st.caption("Explore class balance, QC plots, differential expression, models, and selected genes.")

    try:
        metadata_file = metadata_path()
    except FileNotFoundError:
        metadata_file = None
    selected_genes_file = OUTPUT_DIR / "selected_gene_biological_interpretation.csv"
    mapped_coefficients_file = OUTPUT_DIR / "selected_gene_coefficients_mapped.csv"

    if selected_genes_file.exists():
        selected_gene_count = len(load_csv(selected_genes_file))
    elif mapped_coefficients_file.exists():
        selected_gene_count = len(load_csv(mapped_coefficients_file))
    else:
        selected_gene_count = 20

    st.sidebar.header("Display Options")
    top_gene_count = st.sidebar.slider(
        "Top genes to display",
        min_value=5,
        max_value=max(5, min(100, selected_gene_count)),
        value=min(20, max(5, selected_gene_count)),
        step=5,
    )

    st.sidebar.markdown("Run the numbered scripts first if any outputs are missing.")

    st.header("Dataset Overview")
    if metadata_file is None:
        st.warning("Could not find metadata_all_UCSD_MISC.csv.")
    else:
        metadata = load_csv(metadata_file)
        class_counts = metadata["diagnosis"].value_counts().rename_axis("diagnosis").reset_index(name="count")

        col1, col2, col3 = st.columns(3)
        col1.metric("Samples", len(metadata))
        col2.metric("KD samples", int(class_counts.loc[class_counts["diagnosis"] == "KD", "count"].sum()))
        col3.metric("MIS-C samples", int(class_counts.loc[class_counts["diagnosis"] == "MISC", "count"].sum()))

        st.subheader("Class Balance")
        st.bar_chart(class_counts.set_index("diagnosis"))
        st.dataframe(class_counts, use_container_width=True)

    st.header("Exploratory Analysis")
    pca_col, qc_col = st.columns(2)
    with pca_col:
        show_image(OUTPUT_DIR / "pca_by_diagnosis.png", "PCA colored by diagnosis")
    with qc_col:
        show_image(OUTPUT_DIR / "library_size_by_diagnosis.png", "Library size by diagnosis")

    if (OUTPUT_DIR / "age_by_diagnosis.png").exists():
        show_image(OUTPUT_DIR / "age_by_diagnosis.png", "Age by diagnosis")

    st.header("Differential Expression")
    volcano_col, de_col = st.columns([1, 1])
    with volcano_col:
        show_image(OUTPUT_DIR / "volcano_plot.png", "Volcano plot of KD vs MIS-C differential expression")
    with de_col:
        de_results_file = OUTPUT_DIR / "differential_expression_results.csv"
        if de_results_file.exists():
            de_results = load_csv(de_results_file)
            if "gene_symbol" in de_results.columns:
                priority_columns = ["gene_symbol", "geneID", "adjusted_p_value", "p_value"]
                ordered_columns = [
                    column for column in priority_columns if column in de_results.columns
                ]
                ordered_columns += [
                    column for column in de_results.columns if column not in ordered_columns
                ]
                de_results = de_results[ordered_columns]
            st.subheader("Top Differentially Expressed Genes")
            st.dataframe(de_results.head(top_gene_count), use_container_width=True)
        else:
            st.warning(f"Missing table: {de_results_file}")

    st.header("Model Performance")
    model_summary_file = OUTPUT_DIR / "model_comparison_summary.csv"
    if model_summary_file.exists():
        summary = load_csv(model_summary_file)
        st.subheader("Algorithm Comparison")
        st.dataframe(summary, use_container_width=True)

        best = summary.sort_values("test_auc", ascending=False).iloc[0]
        metric_cols = st.columns(5)
        metric_cols[0].metric("Best model", best["model"])
        metric_cols[1].metric("AUC", f"{best['test_auc']:.3f}")
        metric_cols[2].metric("Accuracy", f"{best['test_accuracy']:.3f}")
        metric_cols[3].metric("Precision", f"{best['test_precision']:.3f}")
        metric_cols[4].metric("Recall", f"{best['test_recall']:.3f}")
    else:
        st.warning(f"Missing table: {model_summary_file}")

    roc_col, cm_col = st.columns(2)
    with roc_col:
        show_image(OUTPUT_DIR / "model_comparison_roc_plot.png", "Combined model ROC curves")
        show_image(OUTPUT_DIR / "baseline_logistic_roc_curve.png", "Baseline logistic regression ROC curve")
    with cm_col:
        show_image(OUTPUT_DIR / "baseline_logistic_confusion_matrix.png", "Baseline logistic regression confusion matrix")
        show_image(
            OUTPUT_DIR / "elastic_net_logistic_regression_confusion_matrix.png",
            "Elastic net logistic regression confusion matrix",
        )

    metrics_file = OUTPUT_DIR / "baseline_logistic_metrics.txt"
    if metrics_file.exists():
        with st.expander("Baseline Logistic Regression Metrics Text"):
            st.text(metrics_file.read_text(encoding="utf-8"))

    st.header("Selected Model Genes")
    if selected_genes_file.exists():
        genes = load_csv(selected_genes_file)
        st.subheader(f"Top {top_gene_count} MIS-C-associated coefficients")
        misc_genes = (
            genes.loc[genes["associated_diagnosis"] == "MIS-C"]
            .sort_values("coefficient", ascending=False)
            .head(top_gene_count)
        )
        st.dataframe(misc_genes, use_container_width=True)

        st.subheader(f"Top {top_gene_count} KD-associated coefficients")
        kd_genes = (
            genes.loc[genes["associated_diagnosis"] == "KD"]
            .sort_values("coefficient", ascending=True)
            .head(top_gene_count)
        )
        st.dataframe(kd_genes, use_container_width=True)
    elif mapped_coefficients_file.exists():
        genes = load_csv(mapped_coefficients_file)
        st.dataframe(
            genes.sort_values("absolute_coefficient", ascending=False).head(top_gene_count),
            use_container_width=True,
        )
    else:
        st.warning("Missing selected gene coefficient tables.")

    show_image(
        OUTPUT_DIR / "top20_selected_gene_coefficients.png",
        "Top selected gene coefficients by absolute magnitude",
    )


if __name__ == "__main__":
    main()
