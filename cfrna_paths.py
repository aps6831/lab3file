"""Shared paths and small helpers for the KD vs MIS-C cfRNA pipeline."""

from pathlib import Path
import os


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
METADATA_NAME = "metadata_all_UCSD_MISC.csv"
COUNTS_NAME = "counts_all_UCSD_MISC.csv"

KD_LABEL = "KD"
MISC_LABEL = "MISC"
RANDOM_STATE = 4020

DATA_DIR_CANDIDATES = [
    ROOT / "data_ML",
    ROOT.parent / "data_ML",
    ROOT.parent.parent / "data_ML",
    ROOT.parent.parent,
]


def configure_matplotlib_cache():
    """Keep matplotlib cache files inside the project folder."""
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib-cache"))


def ensure_output_dir():
    """Create the outputs folder and return its path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def find_data_dir(require_counts=True):
    """Find the lab data folder containing the metadata and, optionally, counts."""
    for data_dir in DATA_DIR_CANDIDATES:
        metadata_file = data_dir / METADATA_NAME
        counts_file = data_dir / COUNTS_NAME
        if metadata_file.exists() and (not require_counts or counts_file.exists()):
            return data_dir

    required = [METADATA_NAME]
    if require_counts:
        required.append(COUNTS_NAME)
    searched = "\n".join(str(path) for path in DATA_DIR_CANDIDATES)
    raise FileNotFoundError(
        f"Could not find required input file(s): {', '.join(required)}\n"
        f"Searched data folders:\n{searched}"
    )


def metadata_path():
    """Return the metadata CSV path."""
    return find_data_dir(require_counts=False) / METADATA_NAME


def counts_path():
    """Return the raw counts CSV path."""
    return find_data_dir(require_counts=True) / COUNTS_NAME


def strip_ensembl_version(gene_id):
    """Remove version suffixes, e.g. ENSG00000133742.14 -> ENSG00000133742."""
    return str(gene_id).split(".")[0]


def detect_count_columns(counts):
    """Return sample columns from a gene-by-sample count matrix."""
    gene_annotation_columns = {
        "geneID",
        "gene_id",
        "gene",
        "gene_name",
        "symbol",
        "transcript_id",
        "feature",
    }
    return [column for column in counts.columns if column not in gene_annotation_columns]
