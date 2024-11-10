"""Tests for ODI Template: TXSTA."""
import csv
from pathlib import Path
from typing import Final

import pytest

from .common import GenericTests, source_files, load_header

TXSTA: Final[str] = "TXSTA"
TXTA: Final[str] = "TXTA"


# Skip this entire module if there are no TX(S)TA files in source.
pytestmark = pytest.mark.skipif(
    (
        len(source_files(TXSTA)) == 0
        and len(source_files(TXTA)) == 0
    ),
    reason="No TXSTA or TXTA files found."
)


def txsta_txta_files() -> list[tuple[Path, Path]]:
    """Return a list of matching TXSTA and TXTA files from source."""
    all_txsta = {file.name: file for file in source_files(TXSTA)}
    all_txta = {file.name: file for file in source_files(TXTA)}

    matching_files: list[tuple[Path, Path]] = []
    for txsta_filename, txsta_file in all_txsta.items():
        txta_filename = txsta_filename.replace(TXSTA, TXTA, 1)
        if (txta_file := all_txta.get(txta_filename)):
            matching_files.append((txsta_file, txta_file))
    return matching_files


class TestTXSTA_TXTA:
    """Tests for TXSTA / TXTA file sets."""

    def test_file_pairs(self) -> None:
        """Test existence of TXSTA and TXTA file sets."""
        txsta: list[Path] = tuple(file.name for file in source_files(TXSTA))
        txta: list[Path] = tuple(file.name for file in source_files(TXTA))

        assert all(
            file.replace(TXSTA, TXTA) in txta for file in txsta
        )
        assert all(
            file.replace(TXTA, TXSTA) in txsta for file in txta
        )

    @pytest.mark.parametrize(
        ("txsta_file", "txta_file"),
        txsta_txta_files(),
        ids=lambda f: f.name
    )
    def test_txsta_in_txta(self, txsta_file: Path, txta_file: Path) -> None:
        """Test every transaction in TXSTA has at least one assignment in TXTA."""
        txsta_reader = csv.reader(
            txsta_file.read_text("utf-8").splitlines(),
            delimiter="\t",
        )
        txta_reader = csv.reader(
            txta_file.read_text("utf-8").splitlines(),
            delimiter="\t",
        )

        txta_keys = [tuple(row[:4]) for row in txta_reader]
        assert all(
            tuple(row[:4]) in txta_keys for row in txsta_reader
        ), "Every transaction in TXSTA should have at least one assignment in TXTA"

    @pytest.mark.parametrize(
        ("txsta_file", "txta_file"),
        txsta_txta_files(),
        ids=lambda f: f.name
    )
    def test_txta_in_txsta(self, txsta_file: Path, txta_file: Path) -> None:
        """Test every assignment in TXTA is joined by a transaction in TXSTA."""
        txsta_content = txsta_file.read_text("utf-8").splitlines()
        txta_content = txta_file.read_text("utf-8").splitlines()        
        
        txsta_reader = csv.reader(txsta_content, delimiter="\t")
        txta_reader = csv.reader(txta_content, delimiter="\t")

        txsta_keys = {tuple(row[:4]) for row in txsta_reader}
        txta_keys = {tuple(row[:4]) for row in txta_reader}
        
        assert txta_keys.issubset(txsta_keys), "Every assignment in TXTA should have a corresponding transaction in TXSTA"

    def test_template_in_headers(self) -> None:
        """Test that the template name is present in the file headers."""
        for file in source_files():
            headers = load_header(file.stem.split('_')[1])
            assert TXSTA in headers or TXTA in headers, \
                f"Template name {TXSTA} or {TXTA} not found in headers of {file.name}"

class TestTXSTA(GenericTests):
    """Tests for individual TXSTA files."""
    template: str = TXSTA
    primary_key: list[str] = [
        "ORDERID",
        "LINENUMBER",
        "SUBLINENUMBER",
        "EVENTTYPEID",
    ]
    required: list[str] = [
        "VALUE",
        "UNITTYPEFORVALUE",
        "COMPENSATIONDATE",
    ]
    numbers: list[str] = [
        "VALUE",
        "UNITVALUE",
        "GENERICNUMBER1",
        "GENERICNUMBER2",
        "GENERICNUMBER3",
        "GENERICNUMBER4",
        "GENERICNUMBER5",
        "GENERICNUMBER6",
    ]
    dates: list[str] = [
        "ACCOUNTINGDATE",
        "COMPENSATIONDATE",
        "GENERICDATE1",
        "GENERICDATE2",
        "GENERICDATE3",
        "GENERICDATE4",
        "GENERICDATE5",
        "GENERICDATE6",
    ]
    booleans: list[str] = [
        "GENERICBOOLEAN1",
        "GENERICBOOLEAN2",
        "GENERICBOOLEAN3",
        "GENERICBOOLEAN4",
        "GENERICBOOLEAN5",
        "GENERICBOOLEAN6",
    ]


class TestTXTA(GenericTests):
    """Tests for individual TXTA files."""
    template = TXTA
    primary_key = [
        "ORDERID",
        "LINENUMBER",
        "SUBLINENUMBER",
        "EVENTTYPEID",
    ]
    required = [
        "PAYEEID",
        "PAYEETYPE",
        "POSITIONNAME",
        "TITLENAME",
    ]
    numbers = [
        "GENERICNUMBER1",
        "GENERICNUMBER2",
        "GENERICNUMBER3",
        "GENERICNUMBER4",
        "GENERICNUMBER5",
        "GENERICNUMBER6",
    ]
    dates = [
        "GENERICDATE1",
        "GENERICDATE2",
        "GENERICDATE3",
        "GENERICDATE4",
        "GENERICDATE5",
        "GENERICDATE6",
    ]
    booleans = [
        "GENERICBOOLEAN1",
        "GENERICBOOLEAN2",
        "GENERICBOOLEAN3",
        "GENERICBOOLEAN4",
        "GENERICBOOLEAN5",
        "GENERICBOOLEAN6",
    ]

    @pytest.mark.dependency(depends=["good_file"])
    def test_pk_columns(self, source: csv.DictReader) -> None:
        """Test primary key columns."""
        primary_key = self.primary_key
        all_pk = primary_key + self.required
        pa, pat, po, title = self.required

        rows: int = 0
        pks: set[tuple] = set()
        duplicates: list[tuple] = []
        for row in source:
            assert all(row[column] for column in primary_key), \
                "Primary key empty " \
                f"{ {column: row[column] for column in primary_key} }"

            pk_dict = {column: row[column] for column in all_pk}
            assert any(row[column] for column in [pa, po, title]), \
                f"One of {[pa, po, title]} is required {pk_dict}"
            if row[pa]:
                assert row[pat], f"{pat} is required if {pa} is provided {pk_dict}"
            rows += 1
            if (pk := tuple(pk_dict.values())) in pks:
                duplicates.append(pk)
            pks.add(pk)
        assert len(pks) == rows, \
            f"File has one or more rows with the same primary key {duplicates}"

    @pytest.mark.dependency(depends=["good_file"])
    def test_required_columns(self, source: csv.DictReader) -> None:
        """Test required columns are filled."""
        required = self.required
        for row in source:
            assert any(row[column] for column in required), \
                "Required column empty " \
                f"{ {column: row[column] for column in required} }"
