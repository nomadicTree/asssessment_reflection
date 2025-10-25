from dataclasses import dataclass

@dataclass
class Topic:
    code: str
    name: str

    def label(self):
        return f"{self.code}: {self.name}"