# schema-to-erd

Convert JSON schema into **simple, human-friendly ERD diagrams**.

Most ERD tools are built for database engineers and produce overly complex diagrams.
**schema-to-erd** is designed for **non-technical users**, making relationships easy to understand at a glance.

---

## ✨ Features

* 📊 Convert JSON schema → ERD diagram
* 🧠 Simplified visual output (non-technical friendly)
* ⚡ Lightweight and fast
* 🎨 Supports multiple output formats (e.g. PNG, SVG)
* 🧩 CLI + Python API support

---

## 📦 Installation

```bash
pip install schema-to-erd
```

> ⚠️ Requires Graphviz installed on your system:
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

### With options

```bash
schema-to-erd --input schema.json --out-file my_diagram --format png
```

---

## 🧪 Example

### Input (`schema.json`)

```json
{
  "users": {
    "id": "int",
    "name": "string"
  },
  "orders": {
    "id": "int",
    "user_id": "int"
  }
}
```

### Command

```bash
schema-to-erd --input schema.json --format png
```

### Output

```
users ────────┐
              │
              ▼
           orders
```

*(Actual output will be a rendered diagram image)*

---

## 🐍 Python Usage

You can also use it programmatically:

```python
from schema_to_erd import build_erd_from_schema

build_erd_from_schema(
    "schema.json",
    "output",
    "png"
)
```

---

## ⚙️ CLI Options

| Option       | Description                         |
| ------------ | ----------------------------------- |
| `--input`    | Path to JSON schema file (required) |
| `--out-file` | Output file name                    |
| `--format`   | Output format (default: png)        |

---

## 📁 Output

If no output file is specified:

```bash
schema-to-erd --input path/to/file.schema.json
```

👉 Output will be:

```
file.png
```

---

## 🧠 Design Philosophy

This project was built to solve a real problem:

> Non-technical users struggle to understand traditional ER diagrams.

So instead of:

* complex graph structures ❌
* overwhelming technical details ❌

We focus on:

* clarity ✅
* simplicity ✅
* usability ✅

---

## 🛠️ Development

Clone the repo:

```bash
git clone https://github.com/khalsz/schema-to-ERD.git
cd schema-to-ERD
```

Install locally:

```bash
pip install -e .
```

Run:

```bash
schema-to-erd --input example.json
```

---

## 🧪 Running Tests (if added)

```bash
pytest
```

---

## 📄 License

MIT License

---

## 🤝 Contributing

Contributions are welcome!

* Open issues
* Suggest improvements
* Submit pull requests

---

## 🌟 Future Improvements

* Schema diff visualization
* Web-based preview
* Support for SQL schemas
* More layout customization

---

## 👤 Author

Built by Khalsz

---

## ⭐ Support

If you find this useful, consider starring the repo!
