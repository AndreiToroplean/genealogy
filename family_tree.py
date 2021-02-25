import random
from enum import Enum

from person import Person


class FamilyTree:
    def __init__(self):
        self.real_names = {}
        self.people = {}
        self.order = []
        self.gens = []

        data = self._read_data()
        self._create_people(data)

    def _read_data(self):
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
                    self.real_names[nickname] = name
                    continue

                key, parent_id = line.split(":")
                child_id, rel = key.split(",")
                data.append((child_id.strip(), rel.strip(), parent_id.strip()))
        random.shuffle(data)
        return data

    def _create_people(self, data):
        for child_id, rel, parent_id in data:
            if child_id not in self.people:
                child = Person(child_id)
                self.people[child_id] = child
                name = self.real_names[child_id]
                child.name = name
            else:
                child = self.people[child_id]
            if parent_id not in self.people:
                parent = Person(parent_id)
                self.people[parent_id] = parent
                name = self.real_names[parent_id]
                parent.name = name
            else:
                parent = self.people[parent_id]

            child.parents.append(parent)
            child.rels.append(Rel[rel])

            parent.children.append(child)

    def p_dfs(self, person, visited):
        if person in visited: return False
        visited.append(person)

        for parent in person.parents:
            r = self.p_dfs(parent, visited)
            if not r: continue
            self.order.append(parent)
        return True

    def c_dfs(self, person, visited):
        if person in visited: return False
        visited.append(person)

        for child in person.children:
            r = self.c_dfs(child, visited)
            if not r: continue
            self.order.append(child)
            return True

    def top_sort(self):
        visited = []
        while True:
            for node in self.people.values():
                if node not in visited:
                    break

            else:
                break

            self.p_dfs(node, visited)
            self.order.append(node)

        self.order.reverse()

        for i, person in enumerate(self.order):
            for j, pot_child in reversed(list(enumerate(self.order[:i]))):
                if pot_child in person.children:
                    break
            else:
                j = -1

            self.order.insert(j + 1, self.order.pop(i))

    def create_gens(self):
        self.gens = [0 for p in self.order]
        for i, person in enumerate(self.order):
            for child in person.children:
                for j, pot_child in enumerate(self.order[:i]):
                    if pot_child == child:
                        break
                else:
                    continue
                self.gens[i] = max(self.gens[i], self.gens[j] + 1)

    def draw(self):
        self.top_sort()
        self.create_gens()
        for person, gen in zip(self.order, self.gens):
            print(" " * gen * 15 + person.name)


class Rel(Enum):
    F = "father"
    M = "mother"
    AF = "adoptive father"
    AM = "adoptive mother"
