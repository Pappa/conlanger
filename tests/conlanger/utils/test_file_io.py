from pathlib import Path

import pandas as pd

from conlanger.utils.file_io import write_manual_mappings_matched_csv


def test_write_manual_mappings_matched_csv(tmp_path: Path):
    from conlanger.ingest.models.mappings import ManualMappingMatch

    path = tmp_path / "manual_mappings_matched_rules.csv"
    write_manual_mappings_matched_csv(
        [
            ManualMappingMatch(
                section_index="17.5.1",
                section_name="Proto-Indo-European to Old Irish",
                rule_id="Old-Irish-mn",
                source="index_diachronica.html:5509",
                from_text="m̩ n̩ → am an / _{s,({m,j,w})V}",
                to_text="m̩ n̩ → am an / _{s,({m,j,w})V}",
            )
        ],
        path,
    )
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    assert list(df.columns) == [
        "section_index",
        "section_name",
        "rule_id",
        "source",
        "from_text",
        "to_text",
    ]
    assert df.iloc[0]["rule_id"] == "Old-Irish-mn"
    assert "_{s,({m,j,w})V}" in df.iloc[0]["from_text"]
    assert "_{s,({m,j,w})V}" in df.iloc[0]["to_text"]
