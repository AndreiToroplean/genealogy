from .utils import Rel


class Person:
    NEE = " ne.e "  # Class constant for maiden name separator

    def __init__(self, id, name="", parents=None, children=None):
        self.id = id
        self.first_name = ""
        self.last_name = ""
        self.middle_name = ""
        self.maiden_name = ""
        if name:
            self.name = name
        self.parents: dict[Rel, Person] = parents if parents is not None else {}
        self.children: list[Person] = children if children is not None else []

    def __repr__(self):
        parents_repr = {rel.value: parent.id for rel, parent in self.parents.items()}
        children_repr = [child.id for child in self.children]
        return (
            f"Person(id={self.id!r}, name={self.name!r}, "
            f"parents={parents_repr!r}, children={children_repr!r})"
        )

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
            f"{f'{self.NEE}{self.maiden_name}' if self.maiden_name else ''}"
        )

    @name.setter
    def name(self, value):
        if self.NEE in value:
            name_part, maiden_name = value.split(self.NEE, 1)
            self.maiden_name = maiden_name.strip()
        else:
            name_part = value
            self.maiden_name = ''
        names = name_part.strip().split()
        self.first_name = names[0] if names else ''
        self.last_name = names[-1] if len(names) > 1 else ''
        self.middle_name = ' '.join(names[1:-1]) if len(names) > 2 else ''

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return (
            (self.last_name, self.maiden_name, self.first_name, self.middle_name)
            < (other.last_name, other.maiden_name, other.first_name, other.middle_name)
        )
