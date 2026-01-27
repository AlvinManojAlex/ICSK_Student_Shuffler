def normalize_data(df):
    """
        Function to normalize data
        1. Correct "Remarks" column
        2. Fix case of "Msc/Isl" column
        3. Fix case of "Gender" column
        4. Fix case of "House" column
        5. Fix case of "Performance" column
        6. Make "Student Name" as upper case
        7. Standardize "Admn. No." column name
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
        "Gender",
        "House",
        "Performance"
    ]

    # Checking for Msc/Isl
    if "Msc/Isl" in df.columns:
        df["Msc/Isl"] = (
            df["Msc/Isl"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map({
                "msc": "Msc",
                "m.sc": "Msc",
                "isl": "Isl",
                "islamic": "Isl"
            })
        )
    
    # Checking for gender
    if "Gender" in df.columns:
        df["Gender"] = (
            df['Gender']
            .astype(str)
            .str.strip()
            .str.lower()
            .map({
                "boy": "Male",
                "male": "Male",
                "m": "Male",
                "girl": "Female",
                "female": "Female",
                "f": "Female"
            })
        )

    for col in proper_case_columns:
        if col in df.columns:
            df[col] = (
                df[col]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .str.title()
            )

    if "Student Name" in df.columns:
        df["Student Name"] = (
            df["Student Name"]
            .astype(str)
            .str.upper()
        )

    # Possible values for "Admn. No." column
    admn_no_column_rename_map = {
        "admn no": "Admn. No.",
        "admn. no": "Admn. No.",
        "admn no.": "Admn. No.",
        "admn number": "Admn. No.",
        "admission no": "Admn. No.",
        "admission no.": "Admn. No.",
        "admission number": "Admn. No."
    }

    df.columns = [
        admn_no_column_rename_map.get(col.lower(), col)
        for col in df.columns
    ]

    return df