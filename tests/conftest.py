"""Fixtures for SAP Commissions PyTests."""
import pytest


def pytest_generate_tests(metafunc: pytest.Metafunc):
    # This hook is called for every test function/method that needs to be parametrized
    cls = metafunc.cls
    if cls and hasattr(cls, '_source_files'):
        files = cls._source_files(cls)
        if 'file' in metafunc.fixturenames:
            metafunc.parametrize(
                argnames="file",
                argvalues=files,
                indirect=True,
                ids=lambda f: f.name,
            )
        if 'source' in metafunc.fixturenames:
            metafunc.parametrize(
                argnames="source",
                argvalues=files,
                indirect=True,
                ids=lambda f: f.name,
            )
