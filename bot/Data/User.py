

class User:
    def __init__(self, user_id:int, cards:list=[], packs:list=[], cash:int=0):
        self.id:int = user_id
        self.cards:list = cards
        self.packs:list = packs
        self.cash:int = cash

    @classmethod
    def from_json(cls, data:dict):
        return cls(
            user_id = data["id"],
            cards = data["cards"],
            packs = data["packs"],
            cash = data["cash"]
        )

    def to_json(self):
        return {
            "id": self.id,
            "cards": self.cards,
            "packs": self.packs,
            "cash": self.cash
        }