class Value:
    name: str
    amount: float
    acquisition_value: float
    current_value: float

    def __init__(self, name: str, amount: float, acquisition_value: float, current_value: float):
        self.name = name
        self.amount = amount
        self.acquisition_value = acquisition_value
        self.current_value = current_value
