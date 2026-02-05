# Fetch Quotes

A simple CLI tool to fetch random quotes from the [Quotable API](https://github.com/lukePeavey/quotable).

## Usage

```bash
# Fetch a single random quote
python main.py

# Fetch multiple quotes
python main.py -n 5

# Fetch quotes by category
python main.py -c wisdom
python main.py -c technology -n 3
```

## Options

| Option | Description |
|--------|-------------|
| `-c, --category` | Quote category (e.g., technology, wisdom, humor) |
| `-n, --count` | Number of quotes to fetch (default: 1) |

## Requirements

- Python 3.8+
- requests

## Sample Output

```
"The only way to do great work is to love what you do."
  — Steve Jobs
  Tags: inspirational, work
```
