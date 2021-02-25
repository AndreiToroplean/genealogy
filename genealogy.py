import random
from enum import Enum


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
        return f"{self.first_name}{' ' + self.middle_name if self.middle_name else ''} {self.last_name}" \
               f"{f' ne.e {self.maiden_name}' if self.maiden_name else ''}"

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


class Rel(Enum):
    F = "father"
    M = "mother"
    AF = "adoptive father"
    AM = "adoptive mother"


real_names = {}
data = []
is_data = False
with open("data.txt") as f:
    for line in f:
        if line.strip().startswith("#"):
            continue

        if not line.strip():
            is_data = True
            continue

        if not is_data:
            nickname, name = line.split(":")
            real_names[nickname] = name
            continue

        key, parent_id = line.split(":")
        child_id, rel = key.split(",")
        data.append((child_id.strip(), rel.strip(), parent_id.strip()))

random.shuffle(data)

people = {}
for child_id, rel, parent_id in data:
    if child_id not in people:
        child = Person(child_id)
        people[child_id] = child
        name = real_names[child_id]
        child.name = name
    else:
        child = people[child_id]
    if parent_id not in people:
        parent = Person(parent_id)
        people[parent_id] = parent
        name = real_names[parent_id]
        parent.name = name
    else:
        parent = people[parent_id]

    child.parents.append(parent)
    child.rels.append(Rel[rel])

    parent.children.append(child)


def p_dfs(person):
    if person in visited: return False
    visited.append(person)

    for parent in person.parents:
        r = p_dfs(parent)
        if not r: continue
        order.append(parent)
    return True


def c_dfs(person):
    if person in visited: return False
    visited.append(person)

    for child in person.children:
        r = c_dfs(child)
        if not r: continue
        order.append(child)
    return True


def top_sort(people, dfs):
    global visited, order
    visited = []
    order = []
    while True:
        for node in people.values():
            if node not in visited:
                break

        else:
            break

        dfs(node)
        order.append(node)

    return order


def create_gens(order):
    gens = [0 for p in order]
    for i, person in enumerate(order):
        for child in person.children:
            for j, pot_child in enumerate(order[:i]):
                if pot_child == child:
                    break
            else:
                continue
            gens[i] = max(gens[i], gens[j] + 1)
    return gens


p_order = top_sort(people, p_dfs)
p_order.reverse()
p_gens = create_gens(p_order)

c_order = top_sort(people, c_dfs)
c_gens = create_gens(c_order)

for o, g in zip(p_order, p_gens):
    print(" " * g * 15 + o.name)

print("=" * 80)
for o, g in zip(c_order, c_gens):
    print(" " * (g * 15) + o.name)
