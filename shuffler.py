import argparse
import pandas as pd
import os
import random

def initialize_classes(num_classes: int, class_sizes: list):
    """
        Initializing classes according to its class size along with shuffled students
    """
    
    classes = []
    
    for i in range(num_classes):
        classes.append({
            "size": class_sizes[i],
            "students": []
        })

    return classes

def distribute_round_robin(df, num_classes: int, classes: list):
    num_classes = len(classes)
    class_index = 0

    shuffled_df = df.sample(frac=1).reset_index(drop=True)

    for _, row in shuffled_df.iterrows():
        placed = False

        for _ in range(num_classes):
            if len(classes[class_index]["students"]) < classes[class_index]["size"]:
                classes[class_index]["students"].append(row)
                placed = True
                class_index = (class_index + 1) % num_classes
                break

            class_index = (class_index + 1) % num_classes

        if not placed:
            # All classes are full — stop distributing
            break

def balanced_shuffle(students_df, num_classes, class_sizes):
    """
        Helper function to shuffle students
    """
    classes = initialize_classes(num_classes, class_sizes)

    # Buckets
    naughty_df = students_df[students_df["Remarks"] == "Naughty"]
    weak_df = students_df[students_df["Remarks"] == "Weak in studies"]
    normal_df = students_df[students_df["Remarks"].isna() | (students_df["Remarks"] == "")]

    # Further split by gender and subject
    def split_and_distribute(df):
        for gender in ["Male", "Female"]:
            for subject in ["Msc", "Isl"]:
                subset = df[
                    (df["Gender"] == gender) &
                    (df["Msc/Isl"] == subject)
                ]
                if not subset.empty:
                    distribute_round_robin(subset, num_classes, classes)

    # Distribute in priority order
    split_and_distribute(naughty_df)
    split_and_distribute(weak_df)
    split_and_distribute(normal_df)

    return classes

def shuffle(num_classes: int, class_sizes: list, directory: str):
    """
        Uniformly and randomly distribute students across all classes
    """

    if directory == "tests":
        # Finding all the excel files (.xlsx and .xls (older excel format)) in the directory
        excel_files = [
            os.path.join(directory, file)
            for file in os.listdir(directory)
            if file.endswith(".xlsx") or file.endswith(".xls")
        ]

        if not excel_files:
            raise FileNotFoundError(f"No excel files in directory '{directory}'")

        # Logging the excel files found
        print("Found the following excel files")
        for file in excel_files:
            print(f" - {file}")

        # Loading all excel files into dataframes
        dataframes = []
        for file in excel_files:
            df = pd.read_excel(file)
            dataframes.append(df)

        # Combining all the data into a single dataframe
        students_df = pd.concat(dataframes, ignore_index=True)
        print(f"Loaded {len(students_df)} total students")

        classes = balanced_shuffle(students_df, num_classes, class_sizes)

        # Convert each class to a DataFrame
        class_dfs = []
        for i, cls in enumerate(classes):
            df = pd.DataFrame(cls["students"])
            class_dfs.append(df)

        total_assigned = sum(len(c["students"]) for c in classes)
        print(f"Total assigned students: {total_assigned}")

        print_class_summary(class_dfs)

def print_class_summary(class_dfs):
    """
        Helper function to print the distribution of the classes after shuffling
    """

    for i, df in enumerate(class_dfs, start=1):
        total = len(df)

        males = (df["Gender"] == "Male").sum()
        females = (df["Gender"] == "Female").sum()

        msc = (df["Msc/Isl"] == "Msc").sum()
        isl = (df["Msc/Isl"] == "Isl").sum()

        naughty = (df["Remarks"] == "Naughty").sum()
        weak = (df["Remarks"] == "Weak in studies").sum()

        print(f"Class {i}")
        print(f"Total students\t\t: {total}")
        print(f"Boys / Girls\t\t: {males} / {females}")
        print(f"Msc / Isl\t\t: {msc} / {isl}")
        print(f"Naughty students\t: {naughty}")
        print(f"Weak in studies\t\t: {weak}")
        print("-" * 50)

def check_valid_args(num_classes: int, class_sizes: list, directory: str):
    """
        Checking if the user passed args are valid
    """

    if len(class_sizes) != num_classes:
        raise ValueError(f"Expected {num_classes} class sizes, but got {len(class_sizes)} instead")
    
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist")

def main():
    """
        Uniformly shuffle students such that each class is equally balanced in terms of gender ratio, moral science - islamic ratio and weak/naughty students
    """

    parser = argparse.ArgumentParser(
        description="Shuffle students uniformly into their next classes"
    )

    parser.add_argument(
        "num_classes",
        type=int,
        help="Number of classes"
    )

    parser.add_argument(
        "class_sizes",
        type=int,
        nargs="+",
        help="Number of students in each class"
    )

    parser.add_argument(
        "--dir",
        type=str,
        help="Directory containing excel files"
    )

    args = parser.parse_args()

    # Getting the user passed arguments
    num_classes = args.num_classes
    class_sizes = args.class_sizes
    directory = args.dir

    check_valid_args(num_classes, class_sizes, directory)

    print("Shuffler configuration:")
    print(f"Number of classes: {num_classes}")
    print(f"Class sizes: {class_sizes}")
    print(f"Input directory: {directory}")

    shuffle(num_classes, class_sizes, directory)

if __name__ == "__main__":
    main()