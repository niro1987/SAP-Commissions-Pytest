# SAP Incentive Management ODI, XDL File Types PyTests

Test for various SAP Incentive Management ODI.XDL file templates. Below is the reference to help doc

[SAP Incentive Management XDL File Templates](https://help.sap.com/docs/SAP_Commissions/0e4b0e05f53e4f87a21c5ccfca72fea6/726cf84c7c231014a804993ce4041860.html)

## Installation

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/niro1987/sapcommissions-pytests
    ```

2. Install requirements:
   
    ```bash
    python -m pip install -r requirements.txt
    ```

## Usage

1. Place your ODI files in the `source` directory.  [Added Samples in Source folder - Delete and replace with your files]
2. Currently TXSTA and TXTA is available for Unit Testing. To add other file types.. Go to fixtures\headers folder with adding your file types and custom file types
3. Run tests.

    ```bash
    python -m pytest
    ```

A detailed report is generated at `./report.html`.

### Visual Studio Code

    The repository is configured to work with VSCode. Open Test Explorer using the icon
    on the Activity Bar. Running tests this way will not generate an html report.

## Contribute

I encourage anyone to write additional tests for their respective ODI templates. Fork
the repository to make your changes and open a pull request to get your changes merged.

Each test files should include a pytest marker to exlude the entire module if
no files for the specific template are found in the source folder.

```py
from .common import source_files

pytestmark = pytest.mark.skipif(
    len(source_files('TEMPLATE')) == 0,
    reason=f"No files found for this ODI template."
)
```

Inherrit from `common.GenericTests` to include tests that any ODI template should pass.
`GenericTests` expects some class variables to be included, see example below.

```py
from .common import GenericTests

class TestMyTemplate(GenericTests)
    """Tests for MyTemplate."""

    template: str = "MY_TEMPLATE"
    primary_key: list[str] = [] # Columns that make the row unique in the file.
    required: list[str] = [] # Columns that are required to be filled.
    numbers: list[str] = [] # Number columns, joined by UNITTYPEFOR... columns.
    dates: list[str] = [] # Date columns, MM/DD/YYYY format.
    booleans: list[str] = [] # Boolean columns, can only contain NULL, 0 or 1.
```
