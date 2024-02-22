"""Helper functions for SAP Commissions PyTests."""
import csv
import re
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Final, Optional

import pytest

REMAINDER: Final[str] = "__REMAINDER__"
FILENAME_PATTERN: Final[re.Pattern] = re.compile(
    r"^[A-Za-z]{4}_[A-Za-z]{4,10}_[A-Za-z]{3,4}_[0-9]{8}"
    r"(_[0-9]{6})?(_\w+)?\.txt$"
)
NUMBER_PATTERN: Final[re.Pattern] = re.compile(r"^-?[0-9]+(\.[0-9]+)?$")
DATE_PATTERN: Final[re.Pattern] = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")
BOOL_PATTERN: Final[re.Pattern] = re.compile(r"^[01]{1}$")


class PathManager:
    """Utilize properties and cache for paths that don't change,
    reducing redundant path computations"""
    @property
    def fixture_path(self) -> Path:
        if not hasattr(self, "_fixture_path"):
            self._fixture_path = Path(__file__).parent.parent / "fixtures"
        return self._fixture_path

    @property
    def source_path(self) -> Path:
        if not hasattr(self, "_source_path"):
            self._source_path = Path(__file__).parent.parent / "source"
        return self._source_path


path_manager = PathManager()


def load_header(template: str) -> list[str]:
    """Load a header file."""
    header_text = (
        (path_manager.fixture_path / "headers" / f"{template}.txt")
        .read_text(encoding="utf-8")
    )
    return header_text.splitlines()[0].split("\t")


def source_files(template: Optional[str] = None) -> list[Path]:
    """Get a list of txt files for the specified template.

    Return all txt files if no template specified."""
    template_upper = template.upper() if template else ""
    return [
        file for file in path_manager.source_path.iterdir()
        if file.suffix.upper() == ".TXT"
        and (not template or template_upper in file.name.upper())
    ]


class Bootstrap:
    """Inject fixtures based in template."""
    template: str

    def _source_files(self) -> list[Path]:
        """Return a list of files matching the template."""
        return source_files(self.template)

    @pytest.fixture
    def file(self, request: pytest.FixtureRequest) -> Path:
        """Return file from source matching the template."""
        return request.param

    @pytest.fixture
    def source(
        self,
        request: pytest.FixtureRequest,
    ) -> Generator[csv.DictReader, None, None]:
        """Sourcefile with fieldnames."""
        headers: list[str] = load_header(self.template)
        with open(request.param, "r", encoding="utf-8") as f_out:
            yield csv.DictReader(
                f_out,
                delimiter="\t",
                fieldnames=headers,
                restkey="__REMAINDER__",
            )


class GenericTests(Bootstrap):
    """Reusable tests."""
    primary_key: list[str] = []
    required: list[str] = []
    numbers: list[str] = []
    dates: list[str] = []
    booleans: list[str] = []

    @pytest.mark.dependency(name="good_file")
    def test_good_file(self, file: Path) -> None:
        """Test readable file.

        - The file is to be named
            `<TENANT>_<TEMPLATE>_<ENV>_<YYYMMDD>_<HHMISS>_<XXXXXX>.txt`
                - "TENANT" is the assigned 4-character tenant designation.
                - "TEMPLATE" is the assigned template designation.
                - "ENV" indicates the intended target environment.
                - "YYYYMMDD" is the date of transmission. 
                - "HHMISS" is a time-stamp (example, 1:42:57pm is "134257"). 
                - "XXXXXX" is a custom tag.

            An example file name therefore is CALD_TXSTA_DEV_20070805_134257_JULY07.txt.
        - The file is to be a tab-delimited text file.
        - The file is to be in Unicode format if it contains international characters.
        - The file is to contain no header rows.
        """
        filename: str = file.name
        assert FILENAME_PATTERN.match(filename)

        file_content: str = file.read_text("utf-8")
        assert file_content, "File is empty or encoding is not unicode"

        file_lines = file_content.splitlines()
        assert all("\t" in line for line in file_lines), "File not tab-delimited"

        headers: list[str] = load_header(self.template)
        first_line = file_lines[0].split("\t")
        assert all(
            item not in headers for item in first_line
        ), "File has header row"

    @pytest.mark.dependency(depends=["good_file"])
    def test_pk_columns(self, source: csv.DictReader) -> None:
        """Test primary key columns are filled and unique."""
        if not (primary_key := self.primary_key):
            pytest.skip(
                f"{self.template} does not have any primary key columns.")

        rows: int = 0
        pks: set[tuple] = set()
        for row in source:
            assert all(row[column] for column in primary_key), \
                "Primary key empty " \
                f"{ {column: row[column] for column in primary_key} }"
            rows += 1
            pks.add(tuple(row[column] for column in primary_key))
        assert len(pks) == rows, \
            "File has one or more rows with the same primary key"

    @pytest.mark.dependency(depends=["good_file"])
    def test_required_columns(self, source: csv.DictReader) -> None:
        """Test required columns are filled."""
        if not (required := self.required):
            pytest.skip(f"{self.template} does not have any required columns.")

        for row in source:
            assert all(row[column] for column in required), \
                "Required column empty " \
                f"{ {column: row[column] for column in required} }"

    @pytest.mark.dependency(depends=["good_file"])
    def test_number_format(self, source: csv.DictReader) -> None:
        """All number values must be in US format."""
        if not (numbers := self.numbers):
            pytest.skip(f"{self.template} does not have any number columns.")

        for row in source:
            assert all(
                NUMBER_PATTERN.match(row[column])
                for column in numbers
                if row[column]
            ), "Number value must be in format 12345.67 " \
                f"{ {column: row[column] for column in numbers if row[column]} }"

    @pytest.mark.dependency(depends=["good_file"])
    def test_date_format(self, source: csv.DictReader) -> None:
        """All date values must be in format of MM/DD/YYYY."""
        if not (dates := self.dates):
            pytest.skip("Template does not have date columns.")

        for row in source:
            assert all(
                DATE_PATTERN.match(row[column])
                and datetime.strptime(row[column], "%m/%d/%Y")
                for column in dates
                if row[column]
            ), "Date value must be in format of MM/DD/YYYY "\
                f"{ {column: row[column] for column in dates if row[column]} }"

    @pytest.mark.dependency(depends=["good_file"])
    def test_boolean_format(self, source: csv.DictReader) -> None:
        """All boolean values must be either 0, 1 or empty."""
        if not (booleans := self.booleans):
            pytest.skip(f"{self.template} does not have any boolean columns.")

        for row in source:
            assert all(
                BOOL_PATTERN.match(row[column])
                for column in booleans
                if row[column]
            ), "Boolean value must be either 0, 1 or empty "\
                f"{ {column: row[column] for column in booleans if row[column]} }"

    @pytest.mark.dependency(depends=["good_file"])
    def test_unittype_if_number(self, source: csv.DictReader) -> None:
        """Unit Type is required if corresponding number is provided."""
        if not (numbers := self.numbers):
            pytest.skip(f"{self.template} does not have any number columns.")

        unittypes = [f"UNITTYPEFOR{column}" for column in numbers]
        numbertypes = list(zip(numbers, unittypes))
        for row in source:
            assert all(
                row[number] and row[unittype]
                for number, unittype in numbertypes
                if row[number] or row[unittype]
            ), "Unit Type is required if corresponding number is provided " \
                f"{ {number: (row[number], row[unittype]) for number, unittype in numbertypes if row[number] or row[unittype]} }"
