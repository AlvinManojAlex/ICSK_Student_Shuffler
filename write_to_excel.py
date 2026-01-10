import os
import string
import pandas as pd

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