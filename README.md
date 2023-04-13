# Purpose

Assist in financial planning

# Usage

I separated the CLI to another repo, will link soon.

## Setup

While in the repo directory:

```
pip install -r requirements.txt
pip install -e .
```

## Example

`example.yml`:

```yaml
accounts:
  - name: Checking
    balance: 5.00
```

**Note:** This will be very boring with no income and defaulting to
0% interest.

## Tips

# Repeated Values

Use a variable to set repeats for easy modification:

```yaml
IMPORTANT_DATE: 2023-06-01
---
...
end_date: {{ IMPORTANT_DATE }}
```

# Goals

- Variable Time Scale prediction
- CLI independent from GUI

# Issues

1. Mortgages do not hit precisely $0 for some reason