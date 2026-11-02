# schema-to-erd

Convert **JSON Schema (Draft 2020-12)** into simple, human-friendly entity-relationship diagrams (ERDs).

`schema-to-erd` transforms JSON Schema definitions into clear diagrams that help technical and non-technical users understand data structures, entities, attributes, and relationships.

## ✨ Features

- Convert JSON Schema into ERD diagrams.
- Generate simplified, readable diagrams.
- Support standard JSON Schema definitions.
- Export diagrams in supported Graphviz formats, such as PNG.
- Use the tool from the command line or as a Python API.

## 📦 Installation

Install the package from PyPI:

```bash
pip install schema-to-erd
```

### System requirement: Graphviz

The package requires Graphviz to be installed on your system.

**macOS**

```bash
brew install graphviz
```

**Ubuntu/Debian**

```bash
sudo apt update
sudo apt install graphviz
```

For other operating systems, see the [Graphviz download page](https://graphviz.org/download/).

## 🚀 Quick Start: Command Line

Given a JSON Schema file named `product.json`, generate an ERD with:

```bash
schema-to-erd --input product.json
```

By default, the tool generates `product.png` in the current working directory.

### CLI options

You can customise the output filename and format:

```bash
schema-to-erd --input product.json --out-file product-erd --format png
```

| Option       | Required | Description                                                            |
| ------------ | -------- | ---------------------------------------------------------------------- |
| `--input`    | Yes      | Path to JSON schema file                                               |
| `--out-file` | No       | Output file name without the extension. Defaults to the input filename |
| `--format`   | No       | Output format (Default: png)                                           |

For example, to generate an SVG diagram:

```bash
schema-to-erd --input product.json --out-file product-erd --format svg
```

The available formats depend on your Graphviz installation and the formats supported by the package.

## 🐍 Python API

You can also use `schema-to-erd` directly in your Python projects.

### Basic usage

```python
from schema_to_erd import build_erd_from_schema

build_erd_from_schema("product.json")
```

This uses the default settings and generates `product.png` in the current working directory.

### Custom output filename and format

Use keyword arguments to specify the output filename and format:

```python
from schema_to_erd import build_erd_from_schema

build_erd_from_schema(
    json_file="product.json",
    output="product-erd",
    fmt="svg",
)
```

This generates `product-erd.svg`.

### Function parameters

| Option       | Required | Default                          | Description                         |
| ------------ | -------- | -------------------------------- | ----------------------------------- |
| `--input`    | Yes      | -                                | Path to JSON schema file            |
| `--out-file` | No       | Input filename without extension | Output file without the extension.  |
| `--format`   | No       | "png".                           | Output format (default: png)        |

The function generates a diagram file rather than returning the diagram itself.

## 🧪 Example

### Input: `product.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Product",
  "type": "object",
  "properties": {
    "productId": {
      "type": "integer"
    },
    "productName": {
      "type": "string"
    }
  }
}
```

### Generate the diagram

```bash
schema-to-erd --input product.json
```

### Expected diagram contents

The generated ERD represents the `Product` entity with these attributes:

- `productId` — integer
- `productName` — string

## 🧠 How It Works

The tool interprets JSON Schema structures to construct an ERD:

- **Schema `title`** — used as the entity name.
- **`properties`** — represented as entity attributes.
- **Nested objects and references** — used to identify relationships where supported by the implementation.

## 🛠️ Development

To work on the source code:

```bash
git clone https://github.com/khalsz/schema-to-ERD.git
cd schema-to-ERD
```

If you use `uv`:

```bash
uv sync --group dev
```

Alternatively, install the project in editable mode using pip:

```bash
pip install -e ".[dev]"
```

The pip command assumes your development dependencies are defined in the `dev` optional-dependency group.

## 🧪 Testing

Run the test suite with:

```bash
uv run pytest
```

Or, if you have installed the development dependencies in your active environment:

```bash
pytest
```

## 📄 License

This project is licensed under the MIT License. See the repository's license file for details.

## 🤝 Contributing

Contributions are welcome!

- Open an issue to report a bug or suggest an improvement.
- Submit a pull request with your proposed changes.

## 👤 Author

Built by Khalsz.