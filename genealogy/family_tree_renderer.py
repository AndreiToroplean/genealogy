from genealogy.family_tree import FamilyTree


class FamilyTreeRenderer:
    def __init__(self, family_tree_data: str):
        self.family_tree = FamilyTree.from_data(family_tree_data)

    def render(self) -> str:
        return self.family_tree.as_str
