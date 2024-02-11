class Asset:
    name: str
    value: float
    pl_value: float

    def __init__(self, name: str, value: float, pl_value: float):
        self.name = name
        self.value = value
        self.pl_value = pl_value
