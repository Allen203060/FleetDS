import re
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel


SENTINEL_STRINGS = {"", "?", "n/a", "na", "null", "none", "nan", "-", "--", "unknown"}
SENTINEL_NUMBERS = {-999, -9999, 999999, -1e9}
NUMERIC_STRING_REGEX = re.compile(r"^[\$\€\£\₹\+\-]?\s*[\d,]+\.?\d*\s*%?$")


class ColumnProfile(BaseModel):
    """Deterministic statistical and hygiene profile for a single DataFrame column."""
    name: str
    dtype: str
    null_count: int
    null_pct: float
    nunique: int
    is_constant: bool
    is_unnamed: bool
    sentinel_hits: int
    whitespace_hits: int
    numeric_string_suspects: int
    sample_values: List[str]
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    mean_val: Optional[float] = None
    median_val: Optional[float] = None
    skew: Optional[float] = None


class DatasetProfile(BaseModel):
    """Complete deterministic X-Ray profile of a tabular CSV dataset."""
    file_path: str
    rows: int
    cols: int
    duplicate_rows: int
    total_missing_cells: int
    columns: List[ColumnProfile]

    def to_markdown(self) -> str:
        """Formats the profile into a compact, LLM-friendly Markdown report."""
        lines = [
            f"### Dataset X-Ray: `{self.file_path}`",
            f"- **Shape:** {self.rows} rows x {self.cols} columns",
            f"- **Exact Duplicate Rows:** {self.duplicate_rows}",
            f"- **Total Missing Cells (true NaN):** {self.total_missing_cells}",
            "",
            "| Column | Dtype | Nulls (%) | Unique | Sentinels | Whitespace | Num-Str | Stats (min / med / max / skew) | Samples |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for c in self.columns:
            flags = []
            if c.is_unnamed:
                flags.append("UNNAMED")
            if c.is_constant:
                flags.append("CONSTANT")
            col_label = f"`{c.name}`" + (f" [{', '.join(flags)}]" if flags else "")

            if c.min_val is not None:
                stats_str = (
                    f"{c.min_val:.2f} / {c.median_val:.2f} / "
                    f"{c.max_val:.2f} / skew={c.skew:.2f}"
                )
            else:
                stats_str = "-"

            samples_str = ", ".join(repr(s) for s in c.sample_values[:3])
            lines.append(
                f"| {col_label} | {c.dtype} | {c.null_count} ({c.null_pct:.1f}%) | "
                f"{c.nunique} | {c.sentinel_hits} | {c.whitespace_hits} | "
                f"{c.numeric_string_suspects} | {stats_str} | {samples_str} |"
            )
        return "\n".join(lines)


class DataProfiler:
    """Pure Python deterministic profiling engine ($0 LLM cost, zero hallucination)."""

    @staticmethod
    def load_csv_safely(csv_path: str) -> pd.DataFrame:
        """Attempts UTF-8 first, falling back to latin1 if encoding fails."""
        try:
            return pd.read_csv(csv_path, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(csv_path, encoding="latin1")

    @classmethod
    def profile(cls, csv_path: str) -> DatasetProfile:
        df = cls.load_csv_safely(csv_path)
        rows, cols = df.shape
        duplicate_rows = int(df.duplicated().sum())
        total_missing_cells = int(df.isna().sum().sum())

        col_profiles: List[ColumnProfile] = []
        for col in df.columns:
            series = df[col]
            null_count = int(series.isna().sum())
            null_pct = (null_count / rows * 100.0) if rows > 0 else 0.0
            nunique = int(series.nunique(dropna=True))
            is_constant = nunique <= 1
            is_unnamed = str(col).startswith("Unnamed:")

            non_null = series.dropna()
            sample_values = [str(v) for v in non_null.head(3).tolist()]

            sentinel_hits = 0
            whitespace_hits = 0
            numeric_string_suspects = 0
            min_val = max_val = mean_val = median_val = skew_val = None

            is_bool = pd.api.types.is_bool_dtype(series)
            is_num = pd.api.types.is_numeric_dtype(series) and not is_bool

            if is_num:
                if len(non_null) > 0:
                    min_val = float(non_null.min())
                    max_val = float(non_null.max())
                    mean_val = float(non_null.mean())
                    median_val = float(non_null.median())
                    raw_skew = non_null.skew() if len(non_null) > 2 else 0.0
                    skew_val = float(0.0 if pd.isna(raw_skew) else raw_skew)
                    sentinel_hits = int(non_null.isin(SENTINEL_NUMBERS).sum())
            elif not is_bool and len(non_null) > 0:
                str_vals = non_null.astype(str)
                stripped_lower = str_vals.str.strip().str.lower()
                sentinel_hits = int(stripped_lower.isin(SENTINEL_STRINGS).sum())
                whitespace_hits = int((str_vals != str_vals.str.strip()).sum())
                numeric_string_suspects = int(
                    str_vals.str.strip().str.match(NUMERIC_STRING_REGEX).sum()
                )

            col_profiles.append(
                ColumnProfile(
                    name=str(col),
                    dtype=str(series.dtype),
                    null_count=null_count,
                    null_pct=round(null_pct, 2),
                    nunique=nunique,
                    is_constant=is_constant,
                    is_unnamed=is_unnamed,
                    sentinel_hits=sentinel_hits,
                    whitespace_hits=whitespace_hits,
                    numeric_string_suspects=numeric_string_suspects,
                    sample_values=sample_values,
                    min_val=min_val,
                    max_val=max_val,
                    mean_val=mean_val,
                    median_val=median_val,
                    skew=skew_val,
                )
            )

        return DatasetProfile(
            file_path=csv_path,
            rows=rows,
            cols=cols,
            duplicate_rows=duplicate_rows,
            total_missing_cells=total_missing_cells,
            columns=col_profiles,
        )