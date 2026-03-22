# schema-to-erd

Convert **JSON Schema (Draft 2020-12)** into simple, human-friendly ERD diagrams.

This tool transforms structured JSON Schema definitions into clear entity-relationship diagrams — making them easier to understand for both technical and non-technical users.

---

## ✨ Features

* 🔄 Convert JSON Schema → ERD diagram
* 🧠 Simplified visual output (focused on clarity)
* 📦 Supports standard JSON Schema format
* 🎨 Export diagrams as PNG (via Graphviz)
* 🧩 CLI + Python API support

---

## 📦 Installation

```bash
pip install schema-to-erd
```

> ⚠️ Requires Graphviz installed:
>
> **Mac**
>
> ```bash
> brew install graphviz
> ```
>
> **Ubuntu**
>
> ```bash
> sudo apt install graphviz
> ```

---

## 🚀 Quick Start (CLI)

```bash
schema-to-erd --input schema.json
```

---

## ⚙️ CLI Options

```bash
schema-to-erd --input schema.json --out-file product --format png
```

| Option       | Description                         |
| ------------ | ----------------------------------- |
| `--input`    | Path to JSON schema file (required) |
| `--out-file` | Output file name                    |
| `--format`   | Output format (default: png)        |

---

## 🧪 Example

### Input (`product.schema.json`)

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

---

### Command

```bash
schema-to-erd --input product.schema.json --format png
```

---

### Output

The tool generates a diagram with:

* **Entity:** Product
* **Attributes:**

  * productId (integer)
  * productName (string)

---

## 🐍 Python Usage

```python
from schema_to_erd import build_erd_from_schema

build_erd_from_schema(
    "product.schema.json",
    "product",
    "png"
)
```

---

## 📁 Output Behaviour

```bash
schema-to-erd --input path/to/product.schema.json
```

👉 Output:

```
product.png
```

---

## 🧠 How It Works

* JSON Schema `title` → Entity name
* `properties` → Attributes
* Nested objects / references → Relationships

---

## 🛠️ Development

```bash
git clone https://github.com/khalsz/schema-to-ERD.git
cd schema-to-ERD
pip install -e .
```

---

## 🧪 Testing

```bash
pytest
```

---

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome!

* Open issues
* Suggest improvements
* Submit pull requests

## 👤 Author

Built by Khalsz