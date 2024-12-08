from __future__ import annotations

import os

from genealogy.family_tree_renderer import FamilyTreeRenderer


def cli() -> None:
    """Command-line interface entry point for the genealogy tool."""
    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Generate a family tree.")
    parser.add_argument("data", help="Path to the input data file (a .json or .yml file).")
    parser.add_argument("-o", "--output", help="Path to the output file.")
    args = parser.parse_args()

    main(args.data, args.output)


def main(data_path: str, output_path: str | None = None) -> None:
    """Generate a visualization of a family tree using ASCII art.
    
    :param data_path: Path to input YML or JSON file with family data.
        See "sample_data.yaml" for an example.
    :param output_path: Optional path to save the rendered tree to.
    """
    with open(data_path) as f:
        data: str = f.read()
    renderer: FamilyTreeRenderer
    if os.path.splitext(data_path)[1].lower() == ".yml":
        renderer = FamilyTreeRenderer.from_yaml(data)
    elif os.path.splitext(data_path)[1].lower() == ".json":
        renderer = FamilyTreeRenderer.from_json(data)
    else:
        raise ValueError("Data file must be in JSON or YAML format.")
    rendered_tree: str = renderer.render()
    print(rendered_tree)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_tree)


if __name__ == "__main__":
    cli()
