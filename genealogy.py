from family_tree import FamilyTree


def main():
    fam_tree = FamilyTree()
    fam_tree.draw()
    with open("drawn_tree.txt", "w", encoding="utf-8") as f:
        f.write(fam_tree.as_str)


if __name__ == "__main__":
    main()
