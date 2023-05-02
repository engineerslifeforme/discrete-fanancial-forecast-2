# Accounts

```{list-table} Account Fields
:header-rows: 1

* - Field Label
  - Data Type
  - Optional
  - Default
  - Description
* - name
  - str
  - No
  - N/A
  - Name of account
* - balance
  - Decimal
  - Yes
  - $0.00
  - Starting balance of account
* - transactions
  - dict
  - Yes
  - None
  - See [Transactions](#transactions)
* - interest_rate
  - float
  - Yes
  - 0.0
  - Yearly percent change in balance
```

## Transactions

```{note}
In this format the destination of the transaction
is implied by the hierarchy
```

Transactions can be captured in the following form:

``` yaml
transactions:
  income:
    monthly:
      - name: Test
        amount: 100.00
```

`income` can also be `expense`

`monthly` can also be:

- `biweekly`
- `yearly`
- `daily`
- `weekly`
