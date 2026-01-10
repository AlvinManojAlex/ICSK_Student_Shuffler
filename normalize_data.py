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
                "isl": "Isl"
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

    return df