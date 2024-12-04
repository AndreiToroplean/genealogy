from genealogy.family_tree import FamilyTree


class TestFamilyTree:
    def test_repr(self):
        with open("sample_data.json", encoding="utf-8") as f:
            data = f.read()
        with open("tests/expected_family_tree_repr_output.txt", encoding="utf-8") as f:
            expected = f.read()

        family_tree = FamilyTree.from_json(data)
        assert repr(family_tree) == expected
