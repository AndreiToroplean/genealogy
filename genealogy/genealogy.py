import argparse

from genealogy.family_tree import FamilyTree


def main():
    parser = argparse.ArgumentParser(description="Generate a family tree.")
    parser.add_argument("data", help="Path to the input data file.")
    parser.add_argument("-o", "--output", help="Path to the output file.")
    args = parser.parse_args()

    with open(args.data) as f:
        data = f.read()
    fam_tree = FamilyTree(data)
    fam_tree.draw()
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(fam_tree.as_str)


if __name__ == "__main__":
    main()
