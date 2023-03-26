import beautiful_date as BD



from financial_planner.Bank import Bank, Bankrupt
from financial_planner.DateUnit import DateUnit

class Simulation:

    def __init__(self, bank: Bank) -> None:
        self.bank = bank

    def run(self, start_date: BD.BeautifulDate, end_date: BD.BeautifulDate, show_progress: bool = False):
        date = start_date
        progress_fail = False
        if show_progress:            
            try:
                from tqdm import tqdm
            except ImportError:
                print(f"ERROR: Progress bar requested, but tqdm not installed!")
                progress_fail = True
        if not show_progress or progress_fail:
            def nothing(stuff):
                return stuff
            tqdm = nothing
        total_days = (end_date - date).days
        for day_index in tqdm(range(total_days)):
            date = start_date + (day_index * BD.days)
            try:
                self.bank.process_date(date, start_date)
            except Bankrupt:
                print(f"Went bankrupt on {date}!")
                break
            self.bank.mature(date)
            
            