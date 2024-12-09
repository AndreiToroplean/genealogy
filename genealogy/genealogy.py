from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

from genealogy.family_tree_renderer import FamilyTreeRenderer


def cli() -> None:
    """Command-line interface entry point for the genealogy tool."""
    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Generate a family tree.")
    parser.add_argument("data", help="Path to the input data file (a .json or .yml file).")
    parser.add_argument("-o", "--output", help="Path to the output text file.")
    parser.add_argument("-i", "--image", help="Path to save the output image.")
    args = parser.parse_args()

    main(args.data, args.output, args.image)


def main(data_path: str, output_path: str | None = None, image_output_path: str | None = None) -> None:
    """Generate a visualization of a family tree using ASCII art.
    
    :param data_path: Path to input YML or JSON file with family data.
        See "sample_data.yaml" for an example.
    :param output_path: Optional path to save the rendered tree to.
    :param image_output_path: Optional path to save the rendered tree as an image.
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
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_tree)
    if image_output_path:
        write_to_image(rendered_tree, image_output_path)
    if not output_path and not image_output_path:
        print(rendered_tree)


def write_to_image(text: str, output_path: str) -> None:
    """Write the given text to an image file.

    :param text: The text to write to the image.
    :param output_path: The path to save the image to.
    """
    try:
        font = ImageFont.truetype("DejaVuSansMono.ttf", 32)
    except IOError:
        font = ImageFont.load_default()

    lines = text.split('\n')

    # Calculate the size of the image
    test_string = "Aj|╷╵┐└"
    bbox = font.getbbox(test_string)
    line_height = bbox[3] - bbox[1]
    
    # Calculate maximum width and total height
    max_width = max(font.getlength(line) for line in lines)
    total_height = len(lines) * line_height

    # Add padding
    padding = 64
    max_width = int(max_width) + padding * 2
    total_height = int(total_height) + padding * 2

    # Create image with dark grey background
    image = Image.new('RGB', (max_width, total_height), color=(30, 30, 30))
    draw = ImageDraw.Draw(image)

    # Draw text in white
    y_text = padding
    for line in lines:
        draw.text((padding, y_text), line, font=font, fill=(255, 255, 255))
        y_text += line_height

    image.save(output_path)


if __name__ == "__main__":
    cli()
