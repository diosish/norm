import pandas as pd
import re


def normalize_and_separate_by_type(file_path, phone_column_identifier, type_column_identifier, sort_column=None):
    """
    Loads an Excel file, normalizes phone numbers in the specified column,
    separates data by participant type and sorts in alphabetical order.

    Returns:
    - dictionary of participant types with corresponding DataFrames
    - DataFrame with valid records (general file)
    - DataFrame with invalid records
    """
    try:
        # Read Excel file using openpyxl
        df = pd.read_excel(file_path, engine='openpyxl')

    except Exception as e:
        raise Exception(f"Error loading file: {str(e)}")

    # Determine the phone column (by name or index)
    if isinstance(phone_column_identifier, int) or (
            isinstance(phone_column_identifier, str) and phone_column_identifier.isdigit()):
        column_index = int(phone_column_identifier)
        if column_index < 0 or column_index >= len(df.columns):
            raise Exception(f"Phone column index {column_index} out of range (0-{len(df.columns) - 1})")
        phone_column = df.columns[column_index]
    else:
        phone_column = phone_column_identifier
        if phone_column not in df.columns:
            raise Exception(
                f"Phone column '{phone_column}' not found in file. Available columns: {', '.join(df.columns)}")

    # Determine the participant type column (by name or index)
    if isinstance(type_column_identifier, int) or (
            isinstance(type_column_identifier, str) and type_column_identifier.isdigit()):
        column_index = int(type_column_identifier)
        if column_index < 0 or column_index >= len(df.columns):
            raise Exception(f"Type column index {column_index} out of range (0-{len(df.columns) - 1})")
        type_column = df.columns[column_index]
    else:
        type_column = type_column_identifier
        if type_column not in df.columns:
            raise Exception(
                f"Type column '{type_column}' not found in file. Available columns: {', '.join(df.columns)}")

    # Create new column for error marking
    df['_number_valid'] = True
    df['_error_reason'] = ''

    # Apply normalization function to each row
    for idx, row in df.iterrows():
        df.loc[idx, phone_column] = normalize_phone(row, phone_column)

    # Separate into two DataFrames - valid and invalid numbers
    valid_df = df[df['_number_valid']].copy()
    invalid_df = df[~df['_number_valid']].copy()

    # Remove service columns
    for df_clean in [valid_df, invalid_df]:
        if '_number_valid' in df_clean.columns:
            df_clean.drop('_number_valid', axis=1, inplace=True)

    # In valid DF remove error reason, keep it in invalid
    if '_error_reason' in valid_df.columns:
        valid_df.drop('_error_reason', axis=1, inplace=True)

    # Determine sort column (if not specified, use first column)
    if sort_column is None or sort_column not in valid_df.columns:
        sort_column = valid_df.columns[0]  # First column by default

    # Separate data by participant type
    type_dfs = {}
    unique_types = valid_df[type_column].dropna().unique()

    for participant_type in unique_types:
        # Filter data by type and create a copy
        type_df = valid_df[valid_df[type_column] == participant_type].copy()

        # Sort data by specified column
        if sort_column in type_df.columns:
            type_df = type_df.sort_values(by=sort_column)

        # Save DataFrame to dictionary
        type_dfs[str(participant_type)] = type_df

    return type_dfs, valid_df, invalid_df


def normalize_phone(row, phone_column):
    """
    Normalizes a phone number to 79998887766 format.
    Sets validation flags in the row.
    """
    phone = row[phone_column]
    original_phone = str(phone) if not pd.isna(phone) else ""

    if pd.isna(phone) or not original_phone.strip():
        row['_number_valid'] = False
        row['_error_reason'] = 'Empty number'
        return phone

    # Convert phone to string
    phone_str = str(phone).strip()

    # Remove everything except digits and + sign
    # First save + if it exists at the beginning
    starts_with_plus = phone_str.startswith('+')
    phone_digits = re.sub(r'[^\d]', '', phone_str)

    # Minimum number of digits for a valid number
    if len(phone_digits) < 7:
        row['_number_valid'] = False
        row['_error_reason'] = f'Not enough digits: {len(phone_digits)}'
        return original_phone

    # Process international formats
    if starts_with_plus:
        # If number starts with +, it's international format

        # If already starts with +7, +8 -> remove + and process as usual
        if phone_digits.startswith('7') or phone_digits.startswith('8'):
            # pass - process below
            pass
        # Other international codes
        elif len(phone_digits) >= 9:  # Minimum length: country code (1-3 digits) + number (min. 7 digits)
            # Replace country code with 7, keep only significant part of number

            # Determine country code length (usually 1-3 digits)
            # This is a heuristic - assume that national number has 9-10 digits
            if len(phone_digits) >= 11:
                # If number is long, assume country code is 1-2 digits
                return '7' + phone_digits[-10:] if len(phone_digits[-10:]) == 10 else '7' + phone_digits[-9:]
            else:
                # For shorter numbers, assume country code is 1-3 digits
                country_code_len = len(phone_digits) - 9 if len(phone_digits) - 9 > 0 else 1
                return '7' + phone_digits[country_code_len:]

    # Process standard formats
    if len(phone_digits) == 11:
        # If first digit is 8 or other (except 7), replace with 7
        if phone_digits[0] != '7':
            return '7' + phone_digits[1:]
        # If already starts with 7, leave as is
        return phone_digits
    elif len(phone_digits) == 10:
        # Add 7 at the beginning for 10-digit numbers (without country code)
        return '7' + phone_digits
    elif len(phone_digits) > 11:
        # Too long number, mark as potentially problematic
        row['_number_valid'] = False
        row['_error_reason'] = f'Number too long: {len(phone_digits)} digits'
        # But still try to process, extracting the main part
        return '7' + phone_digits[-10:]
    else:
        # For shorter numbers (7-9 digits) add 7 at the beginning
        # But mark them as potentially problematic
        if len(phone_digits) < 10:
            row['_number_valid'] = False
            row['_error_reason'] = f'Short number: {len(phone_digits)} digits'
        return '7' + phone_digits