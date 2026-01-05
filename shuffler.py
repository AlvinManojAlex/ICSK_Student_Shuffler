import argparse
import pandas as pd
import os
import random

def shuffle(students_df, num_classes: int, class_sizes: list):
    """
        Function to shuffle students uniformly
        First, evenly distribute students who are naughty and weak in studies among the classes
        Then distribute the remaining students uniformly
    """

    # Total number of students in the dataframe
    total_students = len(students_df)

    # Finding the rows with naughty/weak in the 'Remarks' column
    has_naughty, has_weak = find_naughty_weak(students_df)

    # Naughty students and (Naughty + Weak in studies) considered as naughty student in shuffling
    is_naughty = has_naughty
    students_df["isNaughty"] = is_naughty

    # Weak students considered as weak students in shuffling
    is_weak = has_weak & ~has_naughty
    students_df["isWeak"] = is_weak

    # Computing the distribution of students in the dataframe
    ratios = {
        "boys": (students_df["Gender"] == "Male").sum() / total_students,
        "girls": (students_df["Gender"] == "Female").sum() / total_students,
        "msc": (students_df["Msc/Isl"] == "Msc").sum() / total_students,
        "isl": (students_df["Msc/Isl"] == "Isl").sum() / total_students
    }

    # Shuffling the whole student dataset upfront
    students_df = students_df.sample(frac=1).reset_index(drop=True)

    # Subsetting the dataframes
    naughty_students_df = students_df[students_df["isNaughty"]]
    weak_students_df = students_df[students_df["isWeak"]]
    remaining_students_df = students_df[~students_df["isNaughty"] & ~students_df["isWeak"]]

    # Initialize empty classes
    classes = [
        {
            "size": class_sizes[i],
            "students": []
        }
        for i in range(num_classes)
    ]

    # Function to distribute naughty and weak students evenly among classes
    distribute_evenly(naughty_students_df, num_classes, classes)
    distribute_evenly(weak_students_df, num_classes, classes)
    distribute_evenly(remaining_students_df, num_classes, classes)

    # Converting to dataframe
    return [pd.DataFrame(cls["students"]) for cls in classes]

def distribute_evenly(df, num_classes: int, classes: list):
    """
        Function to distribute students evenly across classes. It will go and assign students in a circular logic
    """
    class_index = 0

    for _, student in df.iterrows():
        # Boolean to check if student is placed
        placed = False

        for _ in range(num_classes):
            # Finding a class to place the student in
            if len(classes[class_index]["students"]) < classes[class_index]["size"]:
                classes[class_index]["students"].append(student)
                placed = True
                class_index = (class_index + 1) % num_classes
                break

            # Increment class_index to check for next class in case you did not find space in the current class
            class_index = (class_index + 1) % num_classes
        
        if not placed:
            # all classes full; but we assume that classroom will have sufficient space, so this case would not trigger
            break

def find_naughty_weak(df):
    """
        Helper function to create boolean flags for cases when the student is naughty and/or weak in studies
    """

    has_naughty = df["Remarks"].str.contains("Naughty", case=False, regex=False)
    has_weak = df["Remarks"].str.contains("Weak in studies", case=False, regex=False)

    return has_naughty, has_weak

def load(num_classes: int, class_sizes: list, directory: str):
    """
        Load the student data into dataframes
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

        # Normalizing the 'Remarks' column
        students_df["Remarks"] = (
            students_df["Remarks"]
            .fillna("")
            .str.strip()
        )

        # Shuffle students
        class_dfs = shuffle(students_df, num_classes, class_sizes)

        print_class_summary(class_dfs)

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

        print(f"Class {i}")
        print(f"Total students\t\t: {total}")
        print(f"Boys / Girls\t\t: {males} / {females}")
        print(f"Msc / Isl\t\t: {msc} / {isl}")
        print(f"Naughty students\t: {naughty}")
        print(f"Weak in studies\t\t: {weak}")
        print("-" * 50)

    print(f"Total students shuffled\t: {total_students_assigned}")

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

    load(num_classes, class_sizes, directory)

if __name__ == "__main__":
    main()