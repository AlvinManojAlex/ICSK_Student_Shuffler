import argparse
import pandas as pd
import os

from write_to_excel import write_data_to_excel
from normalize_data import normalize_data
from class_summary import print_class_summary

def shuffle(students_df, num_classes: int, class_sizes: list):
    """
        Function to shuffle students uniformly
        First, evenly distribute students who are naughty and weak in studies among the classes
        Then distribute the remaining students uniformly
    """

    # Finding the rows with naughty/weak in the 'Remarks' column
    has_naughty, has_weak = find_naughty_weak(students_df)

    # Naughty students and (Naughty + Weak in studies) considered as naughty student in shuffling
    is_naughty = has_naughty
    students_df["isNaughty"] = is_naughty

    # Weak students considered as weak students in shuffling
    is_weak = has_weak & ~has_naughty
    students_df["isWeak"] = is_weak

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

    # Computing ratios of remaining students to maintain that ratio of students in every class
    remaining_ratios = {
        "Male": (remaining_students_df["Gender"] == "Male").mean(),
        "Female": (remaining_students_df["Gender"] == "Female").mean(),
        "Msc": (remaining_students_df["Msc/Isl"] == "Msc").mean(),
        "Isl": (remaining_students_df["Msc/Isl"] == "Isl").mean()
    }

    print("\nDistribution ratios of remaining students")
    for _, idx in enumerate(remaining_ratios):
        print(f"{idx}\t: {100*remaining_ratios[idx]:.3f}%")

    # Function to distribute remaining students according to the ratios
    distribute_according_ratios(remaining_students_df, num_classes, classes, remaining_ratios)

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

def distribute_according_ratios(df, num_classes: int, classes: list, ratios: dict):
    """
        Function to distribute students across classes using desired targets computed from ratios
    """

    # Helper function to get count of attributes in a class
    def get_class_counts(class_students):
        if not class_students:
            return {"Male": 0, "Female": 0, "Msc": 0, "Isl": 0}
        
        tmp = pd.DataFrame(class_students)
        return {
            "Male": (tmp["Gender"] == "Male").sum(),
            "Female": (tmp["Gender"] == "Female").sum(),
            "Msc": (tmp["Msc/Isl"] == "Msc").sum(),
            "Isl": (tmp["Msc/Isl"] == "Isl").sum()
        }
    
    # Pre-compute desired targets using ratios
    desired_per_class = []
    for cls in classes:
        size = cls["size"]
        desired_per_class.append(
            {
                "Male": round(size * ratios["Male"]),
                "Female": round(size * ratios["Female"]),
                "Msc": round(size * ratios["Msc"]),
                "Isl": round(size * ratios["Isl"])
            }
        )
    
    for _, student in df.iterrows():
        best_class_index = None
        best_score = float("-inf")

        for i in range(num_classes):
            cls = classes[i]

            # Skip full classes
            if len(cls["students"]) >= cls["size"]:
                continue

            current_counts = get_class_counts(cls["students"])
            desired = desired_per_class[i]

            score = 0

            # Gender contribution
            gender = student["Gender"]
            gender_deficit = desired[gender] - current_counts[gender]
            score += gender_deficit

            # Stream contribution
            stream = student["Msc/Isl"]
            stream_deficit = desired[stream] - current_counts[stream]
            score += stream_deficit

            # Prefer the class that benefits the most
            if score > best_score:
                best_score = score
                best_class_index = i

        # Assign student to best class found
        if best_class_index is not None:
            classes[best_class_index]["students"].append(student)
        else:
            # Fallback: place in any class with space (should rarely happen)
            for cls in classes:
                if len(cls["students"]) < cls["size"]:
                    cls["students"].append(student)
                    break

def find_naughty_weak(df):
    """
        Helper function to create boolean flags for cases when the student is naughty and/or weak in studies
    """

    has_naughty = df["Remarks"].str.contains("Naughty", case=False, regex=False)
    has_weak = df["Remarks"].str.contains(r"Weak in studies|Slow learner|Scope for improvement|sfi", case=False, regex=True)

    return has_naughty, has_weak

def load(directory: str):
    """
        Load the student data into dataframes
    """

    # Finding all the excel files (.xlsx and .xls (older excel format)) in the directory
    excel_files = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.endswith(".xlsx") or file.endswith(".xls")
    ]

    if not excel_files:
        raise FileNotFoundError(f"No excel files in directory '{directory}'")
        
    # Logging the excel files found
    print("\nFound the following excel files")
    for file in excel_files:
        print(f" - {file}")

    # Loading all excel files into dataframes
    dataframes = []
    for file in excel_files:
        df = pd.read_excel(file)
            
        # drop "Sl. No." column
        df = df.drop(columns=[col for col in df.columns if col.lower().startswith(("sl", "roll"))])
        df = df.dropna(how="all")
        dataframes.append(df)

    # Combining all the data into a single dataframe
    students_df = pd.concat(dataframes, ignore_index=True)
    print(f"\nLoaded {len(students_df)} total students")
        
    return students_df

def check_valid_args(num_classes: int, class_sizes: list, directory: str):
    """
        Checking if the user passed args are valid
    """
    
    if len(class_sizes) != num_classes:
        raise ValueError(f"Expected {num_classes} class sizes, but got {len(class_sizes)} instead")
    
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist")

def run_shuffler(num_classes: int, class_sizes: list, directory: str, output_file: str):
    """
        Entry point for Tkinter .exe usage
    """

    check_valid_args(num_classes, class_sizes, directory)

    print("\nShuffler configuration:")
    print(f"Number of classes\t: {num_classes}")
    print(f"Class sizes: {class_sizes}")
    print(f"Input directory\t\t: {directory}")

    # Load the student data into a dataframe
    students_df = load(directory)

    # Normalize the dataset
    normalize_data(students_df)

    # # Uncomment below for debugging in case of bad gender rows
    # bad_gender_rows = students_df[
    # ~students_df["Gender"].isin(["Male", "Female"])
    # ]

    # print(bad_gender_rows[["Admn. No.", "Student Name", "Gender"]])

    # Shuffle the students
    class_dfs = shuffle(students_df, num_classes, class_sizes)

    print_class_summary(class_dfs)

    # Write the shuffled student data into excel files
    write_data_to_excel(class_dfs, output_file)

def main():
    """
        Uniformly shuffle students such that each class is equally balanced
        in terms of gender ratio, moral science - islamic ratio and weak/naughty students
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

    parser.add_argument(
        "--name",
        type=str,
        default="final_class_distribution",
        help="Name of the output excel file"
    )

    args = parser.parse_args()

    # Getting the user passed arguments
    num_classes = args.num_classes
    class_sizes = args.class_sizes
    directory = args.dir
    output_file = args.name

    # Run the shuffler
    run_shuffler(num_classes, class_sizes, directory, output_file)

if __name__ == "__main__":
    main()