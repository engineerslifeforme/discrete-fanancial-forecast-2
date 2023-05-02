# Transactions

```{list-table} Transaction Fields
:header-rows: 1

* - Field Name
  - Date Type
  - Required
  - Default
  - Description
* - name
  - str
  - Yes
  - N/A
  - Name of transaction
* - amount
  - Decimal
  - No
  - $0.00
  - Amount incurred in transaction
* - tax_rate
  - See [Tax Rates](#tax-rates)
  - No
  - No taxes
  - Taxes to be paid on transaction
* - interest_rate
  - float
  - No
  - 0.0
  - Yearly percent change in transaction
```

## Tax Rates

`income` will determine taxes based on income earned
for the year, e.g.:

``` yaml
tax_rate: income
```

A constant tax rate can also be used:

``` yaml
tax_rate: 0.07 # for 7%
```