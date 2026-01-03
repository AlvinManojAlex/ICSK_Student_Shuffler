import argparse
import pandas as pd
import random
import os

def create_test_excel(total_students: int, num_naughty_students: int, num_weak_students: int, boys_to_girls_ratio: float, msc_to_isl_ratio: float):
    """
        Creating a excel test file according to the specifications
    """

    # Generate random admission numbers
    admn_numbers = random.sample(range(100000, 999999), total_students)

    # Generate student names
    student_names = [f"Student {i+1}" for i in range(total_students)]

    # Assigning gender to the random student
    num_boys = int(total_students * boys_to_girls_ratio)
    num_girls = total_students - num_boys
    genders = ["Male"] * num_boys + ["Female"] * num_girls
    random.shuffle(genders)

    # Msc/Isl assignment
    num_msc = int(total_students * msc_to_isl_ratio)
    num_isl = total_students - num_msc
    subjects = ["Msc"] * num_msc + ["Isl"] * num_isl
    random.shuffle(subjects)

    # Remarks : "Weak" or "Naughty"
    remarks = [""] * total_students
    indices = list(range(total_students))
    random.shuffle(indices)

    for i in indices[:num_naughty_students]:
        remarks[i] = "Naughty"

    for i in indices[num_naughty_students:num_naughty_students + num_weak_students]:
        remarks[i] = "Weak in studies"

    # Create a dataframe
    df = pd.DataFrame({
        "Admn no.": admn_numbers,
        "Student name": student_names,
        "Gender": genders,
        "Msc/Isl": subjects,
        "Remarks": remarks
    })

    # Write to the test excel file in the tests directory
    output_dir = "tests"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "students_test_data.xlsx")
    df.to_excel(output_file, index=False)

    print(f"Excel file '{output_file}' created successfully.")

def check_valid_args(total_students: int, num_naughty_students: int, num_weak_students: int, boys_to_girls_ratio: float, msc_to_isl_ratio: float):

    """
        Checking if the user passed args are valid
    """

    if num_naughty_students + num_weak_students > total_students:
        raise ValueError("Total number of naughty and weak students more than the total number of students")
    
    if not (0 <= boys_to_girls_ratio <= 1 and 0 <= msc_to_isl_ratio <= 1):
        raise ValueError("Ratios must be between 0 and 1")

def main():
    parser = argparse.ArgumentParser(
        description="Create a test excel file with specifications like total number of students, naughty students, weak students, gender ratio and msc_to_isl ratio"
    )

    parser.add_argument(
        "total_students",
        type=int,
        help="Total number of students"
    )

    parser.add_argument(
        "num_naughty_students",
        type=int,
        help="Number of naughty students"
    )

    parser.add_argument(
        "num_weak_students",
        type=int,
        help="Number of weak students"
    )

    parser.add_argument(
        "boys_to_girls_ratio",
        type=float,
        help="Boys-to-Girls ratio (e.g., 0.2, 0.55, 0.8)"
    )

    parser.add_argument(
        "msc_to_isl_ratio",
        type=float,
        help="Moral science-to-Islamic studies ratio (e.g., 0.2, 0.55, 0.8)"
    )

    # parse the args
    args = parser.parse_args()

    total_students = args.total_students
    num_naughty_students = args.num_naughty_students
    num_weak_students = args.num_weak_students
    boys_to_girls_ratio = args.boys_to_girls_ratio
    msc_to_isl_ratio = args.msc_to_isl_ratio

    check_valid_args(total_students, num_naughty_students, num_weak_students, boys_to_girls_ratio, msc_to_isl_ratio)

    print("Creating test excel file with the provided specifications ...")
    # print(f"Total Students: {total_students}")
    # print(f"Naughty Students: {num_naughty_students}")
    # print(f"Weak Students: {num_weak_students}")
    # print(f"boys-to-girls ratio: {boys_to_girls_ratio}")
    # print(f"Moral science-to-Islamic studies ratio: {msc_to_isl_ratio}")

    create_test_excel(total_students, num_naughty_students, num_weak_students, boys_to_girls_ratio, msc_to_isl_ratio)

if __name__ == "__main__":
    main()