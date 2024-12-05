from __future__ import annotations

import argparse

from genealogy.family_tree_renderer import FamilyTreeRenderer


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Generate a family tree.")
    parser.add_argument("data", help="Path to the input data file.")
    parser.add_argument("-o", "--output", help="Path to the output file.")
    args: argparse.Namespace = parser.parse_args()

    with open(args.data) as f:
        data: str = f.read()
    renderer: FamilyTreeRenderer = FamilyTreeRenderer.from_json(data)
    rendered_tree: str = renderer.render()
    print(rendered_tree)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(rendered_tree)


if __name__ == "__main__":
    main()
