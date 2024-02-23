"""Tests for ODI Template: TXSTA."""
import csv
from pathlib import Path
from typing import Final

import pytest

from .common import GenericTests, load_header, source_files

OGPO: Final[str] = "OGPO"


# Skip this entire module if there are no TX(S)TA files in source.
pytestmark = pytest.mark.skipif(
    len(source_files(OGPO)) == 0,
    reason=f"No OGPO files found."
)


class TestOGPO(GenericTests):
    """Tests for OGPO files."""
    template: str = OGPO
    primary_key: list[str] = [
        "POSITIONNAME",
    ]
    required: list[str] = [
        "EFFECTIVESTARTDATE",
        "TITLENAME",
    ]
    numbers: list[str] = [
        "TARGETCOMPENSATION",
        "GENERICNUMBER1",
        "GENERICNUMBER2",
        "GENERICNUMBER3",
        "GENERICNUMBER4",
        "GENERICNUMBER5",
        "GENERICNUMBER6",
    ]
    dates: list[str] = [
        "EFFECTIVESTARTDATE",
        "EFFECTIVEENDDATE",
        "GENERICDATE1",
        "GENERICDATE2",
        "GENERICDATE3",
        "GENERICDATE4",
        "GENERICDATE5",
        "GENERICDATE6",
        "CREDITSTARTDATE",
        "CREDITENDDATE",
        "PROCESSINGSTARTDATE",
        "PROCESSINGENDDATE",
    ]
    booleans: list[str] = [
        "GENERICBOOLEAN1",
        "GENERICBOOLEAN2",
        "GENERICBOOLEAN3",
        "GENERICBOOLEAN4",
        "GENERICBOOLEAN5",
        "GENERICBOOLEAN6",
    ]
