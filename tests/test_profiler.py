import pandas as pd
from core.profiler import DataProfiler


def test_profiler_detects_dirty_data(tmp_path):
    """Verify the deterministic profiler detects sentinels, whitespace, numeric strings, and duplicates."""
    csv_file = tmp_path / "dirty.csv"
    df = pd.DataFrame({
        "Unnamed: 0": [0, 1, 1],
        " Price($) ": ["$1,200.50", "N/A", "N/A"],
        "City": ["New York ", "new york", "new york"],
        "Age": [25, -999, -999],
    })
    df.to_csv(csv_file, index=False)

    profile = DataProfiler.profile(str(csv_file))

    assert profile.rows == 3
    assert profile.cols == 4
    assert profile.duplicate_rows == 1

    col_map = {c.name: c for c in profile.columns}
    assert col_map["Unnamed: 0"].is_unnamed is True
    assert col_map[" Price($) "].numeric_string_suspects == 1
    assert col_map[" Price($) "].sentinel_hits == 2
    assert col_map["City"].whitespace_hits == 1
    assert col_map["Age"].sentinel_hits == 2

    md = profile.to_markdown()
    assert "Dataset X-Ray" in md
    assert "UNNAMED" in md

