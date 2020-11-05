class Job:
    def __init__(self, title, code, opportunity, companies, remote, locations, salary):
        self.title      = title
        self.code       = code
        self.opportunity= opportunity
        self.companies  = companies
        self.remote     = remote
        self.locations  = locations
        self.salary     = salary


class Salary:
    def __init__(self, code=None, currency=None, min_amount=None, max_amount=None, periodicity=None, visible=None):
        self.code       = code
        self.currency   = currency
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.periodicity= periodicity
        self.visible    = visible