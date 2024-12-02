class Person:
    def __init__(self, id):
        self.id = id
        self.parents = []
        self.rels = []
        self.children = []
        self.first_name = ""
        self.last_name = ""
        self.middle_name = ""
        self.maiden_name = ""

    @property
    def name(self):
        return (
            f"{self.first_name}"
            f"{' ' + self.middle_name if self.middle_name else ''}"
            f" {self.last_name}"
            f"{f' ne.e {self.maiden_name}' if self.maiden_name else ''}"
        )

    @name.setter
    def name(self, name):
        names = name.split()
        last = names.pop()
        if last.startswith("(") and last.endswith(")"):
            self.maiden_name = last[1:-1]
            self.last_name = names.pop()
        else:
            self.last_name = last
        self.first_name = names.pop(0)
        self.middle_name = " ".join(names)

    def __repr__(self):
        return f"Person({{'Name': {self.name}, " \
               f"'Parents': {[(p.name, rel) for p, rel in zip(self.rels, self.parents)]}, " \
               f"'Children': {[c.name for c in self.children]}}})"

    def __eq__(self, other):
        return self.id == other.id
