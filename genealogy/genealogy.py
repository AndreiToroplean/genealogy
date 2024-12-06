from __future__ import annotations

from genealogy.family_tree_renderer import FamilyTreeRenderer


def main(data_path: str, output_path: str | None = None) -> None:
    with open(data_path) as f:
        data: str = f.read()
    renderer: FamilyTreeRenderer = FamilyTreeRenderer.from_json(data)
    rendered_tree: str = renderer.render()
    print(rendered_tree)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_tree)


def cli() -> None:
    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Generate a family tree.")
    parser.add_argument("data", help="Path to the input data file.")
    parser.add_argument("-o", "--output", help="Path to the output file.")
    args = parser.parse_args()

    main(args.data, args.output)


if __name__ == "__main__":
    cli()
