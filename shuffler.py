import argparse
import os

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

if __name__ == "__main__":
    main()