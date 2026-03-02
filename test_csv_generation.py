"""
Test suite for the VDP CSV generation pipeline.

Tests cover: file loading, lane splitting, VDP checks, dummy lanes,
end-to-end CSV generation, summary slicing, and wikkel formula.
"""
import pytest
import pandas as pd
from pathlib import Path

# Functions from app/core/business_logic.py (the refactored/fixed versions)
from app.core.business_logic import (
    file_to_generator,
    splitter_df_2,
    rol_beeld_is_pdf_uit_excel,
    banen_in_vdp_check,
    maak_een_dummy_baan,
    de_uitgerekenende_wikkel,
)

# maak_meerdere_vdps lives in calculations.py (the original pipeline)
from calculations import (
    splitter_df_2 as calc_splitter_df_2,
    maak_meerdere_vdps,
)

# summary_splitter_df_2 from summary.py
from summary import summary_splitter_df_2


TEST_DIR = Path(__file__).parent / "test_files"


# ── fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def sample_df():
    """Load test_labels.csv — 10 rows, total aantal = 1630."""
    df = pd.read_csv(TEST_DIR / "test_labels.csv", sep=";")
    assert len(df) == 10
    assert int(df.aantal.sum()) == 1630
    return df


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Temporary directory for CSV output."""
    return tmp_path


# ── 1-2  file_to_generator ─────────────────────────────────────────

def test_file_to_generator_csv():
    df = file_to_generator(str(TEST_DIR / "test_labels.csv"))
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (10, 5)
    for col in ("aantal", "Omschrijving", "sluitbarcode", "Artnr", "beeld"):
        assert col in df.columns


def test_file_to_generator_xlsx():
    df = file_to_generator(str(TEST_DIR / "test_labels.xlsx"))
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (10, 5)
    for col in ("aantal", "Omschrijving", "sluitbarcode", "Artnr", "beeld"):
        assert col in df.columns


# ── 3-5  splitter_df_2 (business_logic version — returns DataFrames) ──

def test_splitter_df_2_returns_dataframes(sample_df):
    """Each lane must be a DataFrame (not a raw list) — validates the concat fix."""
    lanes = splitter_df_2(sample_df, mes=4)
    assert len(lanes) >= 1
    for lane in lanes:
        assert isinstance(lane, pd.DataFrame), (
            f"Expected DataFrame, got {type(lane).__name__}"
        )


def test_splitter_df_2_lane_count(sample_df):
    """With mes=4, vdp_aantal=1 the splitter should produce ~4 lanes."""
    lanes = splitter_df_2(sample_df, mes=4, aantalvdps=1)
    assert len(lanes) == 4


def test_splitter_df_2_all_rows_preserved(sample_df):
    """Total rows across all lanes accounts for all aantal + extra_etiketten
    plus wikkel and sluitetiket wrapping per input row.
    Per row: wikkel + 1(sluitetiket) + (aantal + extra) + 1(sluitetiket)."""
    extra = 5
    wikkel = 1
    lanes = splitter_df_2(sample_df, mes=4, wikkel=wikkel, extra_etiketten=extra)
    total_rows = sum(len(lane) for lane in lanes)
    # Each of the 10 input rows contributes: wikkel + 2 (sluitetiketten) + aantal + extra
    expected = int(sample_df.aantal.sum()) + len(sample_df) * (extra + wikkel + 2)
    assert total_rows == expected


# ── 6  rol_beeld_is_pdf_uit_excel ──────────────────────────────────

def test_rol_beeld_is_pdf_uit_excel(sample_df):
    row = next(sample_df.itertuples(index=False))
    result_df, aantal = rol_beeld_is_pdf_uit_excel(row, wikkel=1)
    assert isinstance(result_df, pd.DataFrame)
    assert isinstance(aantal, int)
    assert aantal == int(row.aantal)
    expected_cols = {"pdf", "omschrijving", "Artnr", "sluitbarcode"}
    assert set(result_df.columns) == expected_cols
    # rows = wikkel(1) + sluitetiket(1) + (aantal + extra_etiketten) + sluitetiket(1)
    assert len(result_df) == 1 + 1 + (aantal + 5) + 1


# ── 7-9  banen_in_vdp_check ────────────────────────────────────────

def test_banen_in_vdp_check_equal():
    ok, dummies, vdps = banen_in_vdp_check(4, 4, aantal_vdps=1, mes_waarde=4)
    assert ok is True
    assert dummies == 0
    assert vdps == 1


def test_banen_in_vdp_check_fewer():
    """Fewer lanes than needed → need dummy lanes."""
    ok, dummies, vdps = banen_in_vdp_check(4, 3, aantal_vdps=1, mes_waarde=4)
    assert ok is False
    assert dummies == 1          # need 1 dummy
    assert vdps == 1


def test_banen_in_vdp_check_more():
    """More lanes than slots → need extra VDP."""
    result = banen_in_vdp_check(4, 5, aantal_vdps=1, mes_waarde=4)
    ok, dummies, vdps = result[0], result[1], result[2]
    assert ok is False
    assert vdps == 2             # bumped to 2 VDPs
    # dummies = (2 * 4) - 5 = 3
    assert dummies == 3


# ── 10  maak_een_dummy_baan ────────────────────────────────────────

def test_maak_een_dummy_baan(sample_df):
    df_copy = sample_df.copy()
    gemiddelde = 100
    aantal_dummy = 2
    dummy_lanes, count = maak_een_dummy_baan(df_copy, gemiddelde, aantal_dummy)
    assert count == aantal_dummy
    assert len(dummy_lanes) == aantal_dummy
    for lane in dummy_lanes:
        assert isinstance(lane, pd.DataFrame)
        assert len(lane) == gemiddelde
        assert "pdf" in lane.columns


# ── 11-12  maak_meerdere_vdps (end-to-end via calculations.py) ────

def _build_lanes_for_calculations(sample_df):
    """Use calculations.py's splitter (now returns concat'd DataFrames)."""
    return calc_splitter_df_2(sample_df, mes=4, pdf_sluitetiket=False)


def test_maak_meerdere_vdps_creates_files(sample_df, tmp_output_dir):
    lanes = _build_lanes_for_calculations(sample_df)
    maak_meerdere_vdps(
        lanes,
        mes=4,
        aantal_vdps=1,
        ordernummer="TEST123",
        pad=tmp_output_dir,
        sluitbarcode_uitvul_waarde_getal="00000000",
        etiket_y=10,
    )
    csv_files = list(tmp_output_dir.glob("*.csv"))
    assert len(csv_files) >= 1
    assert any("VDP 1" in f.name for f in csv_files)


def test_vdp_csv_column_structure(sample_df, tmp_output_dir):
    lanes = _build_lanes_for_calculations(sample_df)
    maak_meerdere_vdps(
        lanes,
        mes=4,
        aantal_vdps=1,
        ordernummer="COLTEST",
        pad=tmp_output_dir,
        sluitbarcode_uitvul_waarde_getal="00000000",
        etiket_y=10,
    )
    csv_file = tmp_output_dir / "COLTEST VDP 1.csv"
    result = pd.read_csv(csv_file)
    # Columns follow the pattern: pdf_N, omschrijving_N, Artnr_N, sluitbarcode_N
    for n in range(1, 5):
        for base in ("pdf", "omschrijving", "Artnr", "sluitbarcode"):
            assert f"{base}_{n}" in result.columns, (
                f"Missing column {base}_{n} — got {list(result.columns)}"
            )


# ── 13  summary_splitter_df_2 ──────────────────────────────────────

def test_summary_splitter_df_2(sample_df):
    slices = summary_splitter_df_2(sample_df, mes=4)
    assert isinstance(slices, list)
    assert all(isinstance(s, tuple) and len(s) == 2 for s in slices)
    # Slices should cover all rows (begin of first == 0, end of last == 10)
    assert slices[0][0] == 0
    assert slices[-1][1] == len(sample_df)


# ── 14  wikkel_formule ─────────────────────────────────────────────

def test_wikkel_formule():
    # de_uitgerekenende_wikkel(Aantalperrol, formaat_hoogte, kern=76)
    result = de_uitgerekenende_wikkel(1000, 50)
    assert isinstance(result, int)
    assert result == 9
