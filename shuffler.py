import argparse
import pandas as pd
import os
import string

def shuffle(students_df, num_classes: int, class_size: int):
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
            "size": class_size,
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
    has_weak = df["Remarks"].str.contains("Weak in studies", case=False, regex=False)

    return has_naughty, has_weak

def load(num_classes: int, directory: str):
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
    
    # Reading of excel files slightly different for test files and actual school files
    if directory == "tests":
        # Loading all excel files into dataframes
        dataframes = []
        for file in excel_files:
            df = pd.read_excel(file)
            dataframes.append(df)
    else:
        # Loading all excel files into dataframes
        dataframes = []
        for file in excel_files:
            df = pd.read_excel(file, header=3)
            
            # drop "Sl. No." column
            df = df.drop(columns=[col for col in df.columns if col.lower().startswith("sl")])
            dataframes.append(df)

    # Combining all the data into a single dataframe
    students_df = pd.concat(dataframes, ignore_index=True)
    print(f"\nLoaded {len(students_df)} total students")

    # Class size
    class_size = len(students_df) / num_classes
        
    # Normalizing the dataset
    students_df = normalize_data(students_df)

    # Shuffle students
    class_dfs = shuffle(students_df, num_classes, class_size)

    print_class_summary(class_dfs)

    # Write the shuffled student data into excel files
    write_data_to_excel(class_dfs)

def normalize_data(df):
    """
        Function to normalize data
        1. Correct "Remarks" column
        2. Fix case of "Msc/Isl" column
        3. Fix case of "Gender" column
        4. Fix case of "House" column
        5. Fix case of "Performance" column
    """

    # Normalizing the "Remarks" column
    if "Remarks" in df.columns:
        df["Remarks"] = (
            df["Remarks"]
            .fillna("")
            .str.strip()
        )

    # Columns that just need proper casing
    proper_case_columns = [
        "Msc/Isl",
        "Gender",
        "House",
        "Performance"
    ]

    for col in proper_case_columns:
        if col in df.columns:
            df[col] = (
                df[col]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .str.title()
            )

    return df

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

def write_data_to_excel(class_dfs):
    """
        Function to write the data into excel sheets with each sheet for the new class
        1. Drop "isNaughty" and "isWeak" boolean columns
        2. Sorts the sheet alphabetically according to "Student Name"
        3. Fills 'Promoted to' column based on 'Promoted from' + class letter
    """

    if not os.path.isdir("shuffling_output"):
        print("\nCreating `shuffling_output` directory to store the result")
        os.makedirs("shuffling_output")
    else:
        print("\nFound `shuffling_output` directory, storing excel file here")

    output_file = "shuffling_output/final_class_distribution.xlsx"

    # Writing data to excel file
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for i, df in enumerate(class_dfs):
            # Sheet name of the format "Class <A, B, C, ...>"
            class_letter = string.ascii_uppercase[i]
            sheet_name = f"Class {class_letter}"

            # Drop `isNaughty` and `isWeak` columns
            df_to_write = df.drop(
                columns=[col for col in ["isNaughty", "isWeak"] if col in df.columns]
            )

            # Populating the `Promoted to` column using the `Promoted from` column
            if "Promoted to" in df_to_write.columns and "Promoted from" in df_to_write.columns:
                def compute_promoted_to(value):
                    if pd.isna(value):
                        return f"?{class_letter}"
                    # Extract number from `Promoted from` (e.g., "5G" → 5)
                    num_part = ''.join(filter(str.isdigit, str(value)))
                    if not num_part:
                        return f"?{class_letter}"
                    return f"{int(num_part)+1}{class_letter}"

                df_to_write["Promoted to"] = df_to_write["Promoted from"].apply(compute_promoted_to)

            # Sort alphabetically by `Student Name` if the column exists
            if "Student Name" in df_to_write.columns:
                df_to_write = df_to_write.sort_values(by="Student Name", ascending=True)

            # Add "Sl. No." as first column
            df_to_write.insert(0, "Sl. No.", range(1, len(df_to_write) + 1))
            
            # Write to Excel
            df_to_write.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )
        
            # Adjusting column width to accomodate the header for the excel sheet
            worksheet = writer.sheets[sheet_name]
            for col_idx, col in enumerate(df_to_write.columns):
                max_len = max(
                    df_to_write[col].astype(str).map(len).max(),
                    len(col)
                )
                worksheet.set_column(col_idx, col_idx, max_len + 2)

    print(f"Excel file written successfully: {output_file}")

def check_valid_args(directory: str):
    """
        Checking if the user passed args are valid
    """
    
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory '{directory}' does not exist")

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
        "--dir",
        type=str,
        help="Directory containing excel files"
    )

    args = parser.parse_args()

    # Getting the user passed arguments
    num_classes = args.num_classes
    directory = args.dir

    check_valid_args(directory)

    print("\nShuffler configuration:")
    print(f"Number of classes\t: {num_classes}")
    print(f"Input directory\t\t: {directory}")

    load(num_classes, directory)

if __name__ == "__main__":
    main()