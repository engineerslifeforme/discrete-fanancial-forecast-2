from financial_planner.cli import create_simulation

def test_create_simulation():
    sim = create_simulation("""
accounts:
  - name: Wells Fargo Checking
    interest_rate: 0.01
    balance: 50000.00
    transactions:
      monthly_income:
        - name: Pay Day
          amount: 5000.00
""")
    assert(len(sim.bank.accounts[0].transactions) == 1)
    assert(len(sim.bank.accounts[0].transactions[0].name) == "Pay Day")