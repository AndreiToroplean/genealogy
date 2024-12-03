from .utils import Rel


class Person:
    def __init__(self, id):
        self.id = id
        self.parents: dict[Rel, Person] = {}
        self.children: list[Person] = []
        self.first_name = ""
        self.last_name = ""
        self.middle_name = ""
        self.maiden_name = ""

    def set_names_from_str(self, name_str):
        names = name_str.split()
        last = names.pop()
        if last.startswith("(") and last.endswith(")"):
            self.maiden_name = last[1:-1]
            self.last_name = names.pop()
        else:
            self.last_name = last
        self.first_name = names.pop(0)
        self.middle_name = " ".join(names)

    @property
    def name(self):
        return (
            f"{self.first_name}"
            f"{' ' + self.middle_name if self.middle_name else ''}"
            f" {self.last_name}"
            f"{f' ne.e {self.maiden_name}' if self.maiden_name else ''}"
        )

    def __repr__(self):
        return (
            f"Person({{'Name': {self.name}, "
            f"'Parents': {[(p.name, rel) for rel, p in self.parents.items()]}, "
            f"'Children': {[c.name for c in self.children]}}})"
        )

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return (
            (self.last_name, self.maiden_name, self.first_name, self.middle_name)
            < (other.last_name, other.maiden_name, other.first_name, other.middle_name)
        )
