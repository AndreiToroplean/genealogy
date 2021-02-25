class Person:
    def __init__(self):
        self.fathers = []
        self.mothers = []
        self.children = []
        self.name = ""

    def __repr__(self):
        return f"Person({{'Name': {self.name}, " \
               f"'Fathers': {[f.name for f in self.fathers]}, " \
               f"'Mothers': {[m.name for m in self.mothers]}, " \
               f"'Children': {[c.name for c in self.children]}}})"

    def __eq__(self, other):
        return self.name == other.name


with open("data.txt") as f:
    data_str = f.read()

data_str = data_str.splitlines()

data = []
for relation_str in data_str:
    if relation_str.strip().startswith("#"):
        continue

    key, parent = relation_str.split(":")
    child, rel = key.split(",")
    data.append((child.strip(), rel.strip(), parent.strip()))

people = {}
for relation in data:
    child, rel, parent = relation

    if child not in people:
        people[child] = Person()
        people[child].name = child
    if parent not in people:
        people[parent] = Person()
        people[parent].name = parent

    if rel.upper() == "F":
        people[child].fathers.append(people[parent])
    elif rel.upper() == "M":
        people[child].mothers.append(people[parent])
    else:
        raise Exception("Wrong relation, must be 'F', or 'M'.")

    people[parent].children.append(people[child])


def p_dfs(person):
    if person in visited: return False
    visited.append(person)

    for mother in person.mothers:
        r = p_dfs(mother)
        if not r: continue
        order.append(mother)
    for father in person.fathers:
        r = p_dfs(father)
        if not r: continue
        order.append(father)
    return True


def c_dfs(person):
    if person in visited: return False
    visited.append(person)

    for child in person.children:
        r = c_dfs(child)
        if not r: continue
        order.append(child)
    return True


def top_sort(dfs):
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


p_order = top_sort(p_dfs)
p_order.reverse()
p_gens = create_gens(p_order)

c_order = top_sort(c_dfs)
c_gens = create_gens(c_order)


for o, g in zip(p_order, p_gens):
    print(" " * g * 15 + o.name)
print("=" * 80)
for o, g in zip(c_order, c_gens):
    print(" " * (g * 15) + o.name)

# lambda t: t.replace("╚", " ").replace("║", " ").replace("═", " ").replace("╬", " ").replace("╦", " ").replace("╗", " ").replace("╣", " ")
