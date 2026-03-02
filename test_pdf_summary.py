"""Tests for pdf_summary.generate_pdf_summary."""
import pytest
from pathlib import Path

from pdf_summary import generate_pdf_summary


@pytest.fixture
def sample_banen_summary():
    """Two lanes, each with a couple of rolls."""
    return [
        {
            "baan_nr": 1,
            "rollen": [
                {"beeld": "etiket_A.pdf", "omschrijving": "Product A", "aantal": 500},
                {"beeld": "etiket_B.pdf", "omschrijving": "Product B", "aantal": 300},
            ],
            "subtotaal": 800,
        },
        {
            "baan_nr": 2,
            "rollen": [
                {"beeld": "etiket_C.pdf", "omschrijving": "Product C", "aantal": 830},
            ],
            "subtotaal": 830,
        },
    ]


@pytest.fixture
def pdf_kwargs(sample_banen_summary):
    return dict(
        ordernummer="ORD-2025-001",
        mes=2,
        vdp_aantal=1,
        totaal_etiketten=1630,
        wikkel=9,
        kern=76,
        formaat_hoogte=50,
        formaat_breedte=100,
        extra_etiketten=5,
        afwijking_waarde=0,
        meters_per_baan=[42.4, 44.0],
        banen_summary=sample_banen_summary,
    )


def test_generate_pdf_creates_file(tmp_path, pdf_kwargs):
    """Output file exists and starts with the PDF magic bytes."""
    out = tmp_path / "summary.pdf"
    generate_pdf_summary(output_path=out, **pdf_kwargs)

    assert out.exists()
    header = out.read_bytes()[:5]
    assert header == b"%PDF-"


def test_pdf_contains_ordernummer(tmp_path, pdf_kwargs):
    """The ordernummer text must appear somewhere in the raw PDF stream."""
    out = tmp_path / "summary.pdf"
    generate_pdf_summary(output_path=out, **pdf_kwargs)

    raw = out.read_bytes().decode("latin-1")
    assert "ORD-2025-001" in raw


def test_pdf_with_empty_banen(tmp_path, pdf_kwargs):
    """Zero lanes should not crash — produces a valid PDF with no lane rows."""
    pdf_kwargs["banen_summary"] = []
    pdf_kwargs["meters_per_baan"] = []
    out = tmp_path / "empty_banen.pdf"
    generate_pdf_summary(output_path=out, **pdf_kwargs)

    assert out.exists()
    header = out.read_bytes()[:5]
    assert header == b"%PDF-"
