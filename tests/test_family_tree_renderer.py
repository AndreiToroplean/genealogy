from genealogy.family_tree_renderer import FamilyTreeRenderer


class TestFamilyTree:
    def test_render(self):
        with open("sample_data.txt", encoding="utf-8") as f:
            data = f.read()
        with open("tests/expected_family_tree_renderer_render_output.txt", encoding="utf-8") as f:
            expected = f.read()

        renderer = FamilyTreeRenderer.from_data(data)
        assert renderer.render() == expected
