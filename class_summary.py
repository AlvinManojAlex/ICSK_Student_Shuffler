def print_class_summary(class_dfs):
    """
        Helper function to print the distribution of the classes after shuffling
    """

    total_students_assigned = 0

    for i, df in enumerate(class_dfs, start=1):
        total = len(df)
        total_students_assigned += total

        males = (df["Gender"] == "Male").sum()
        females = (df["Gender"] == "Female").sum()

        msc = (df["Msc/Isl"] == "Msc").sum()
        isl = (df["Msc/Isl"] == "Isl").sum()

        naughty = df["isNaughty"].sum()
        weak = df["isWeak"].sum()

        print()
        print("-" * 50)
        print(f"\nClass {i}")
        print(f"Total students\t\t: {total}")
        print(f"Boys / Girls\t\t: {males} / {females}")
        print(f"Msc / Isl\t\t: {msc} / {isl}")
        print(f"Naughty students\t: {naughty}")
        print(f"Weak in studies\t\t: {weak}")

    print(f"\nTotal students shuffled\t: {total_students_assigned}")