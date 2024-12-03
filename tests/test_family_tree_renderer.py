from genealogy.family_tree_renderer import FamilyTreeRenderer


class TestFamilyTree:
    def test_as_str(self):
        with open("sample_data.txt", encoding="utf-8") as f:
            data = f.read()
        with open("tests/expected_family_tree_as_str.txt", encoding="utf-8") as f:
            expected = f.read()

        renderer = FamilyTreeRenderer(data)
        assert renderer.render() == expected