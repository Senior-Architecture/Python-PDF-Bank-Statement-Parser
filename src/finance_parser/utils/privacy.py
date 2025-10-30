import re
import pandas as pd




def mask_value(value: str) -> str:
    """
    Mask sensitive information in a string.

    - Hides part of UPI IDs (e.g., 'user@bank' → 'us****@bank')
    - Masks the first half of long numeric IDs (e.g., cheque or transaction numbers)

    Args:
        value (str): Input string containing sensitive info.

    Returns:
        str: Masked string.
    """
    if not isinstance(value, str) or not value:
        return value

    # Mask UPI IDs
    if "@" in value:
        name, domain = value.split("@", 1)
        return f"{name[:2]}****@{domain}"

    # Mask long numeric IDs
    return re.sub(
        r"\d{4,}",
        lambda m: "*" * (len(m.group(0)) // 2) + m.group(0)[len(m.group(0)) // 2:],
        value
    )



def sanitize_transactions(df: pd.DataFrame, level: str, sensitive_fields: dict) -> pd.DataFrame:
    """
    Apply privacy rules to a transactions DataFrame based on the specified level.

    Privacy levels:
      - full: keep all data
      - masked: drop or mask sensitive fields
      - anonymized: remove all sensitive fields

    The sensitive_fields dict should indicate which columns to mask or drop.

    Args:
        df (pd.DataFrame): The transactions DataFrame.
        level (str): Privacy level ('full', 'masked', 'anonymized').
        sensitive_fields (list): Column names.

    Returns:
        pd.DataFrame: DataFrame with privacy rules applied.
    """
    df = df.copy()

    if level == "full":
        return df

    # Drop or mask fields
    if level == "masked":
        for col in sensitive_fields:
            if col in df.columns:
                df[col] = df[col].apply(mask_value)

    # Anonymized — drop everything sensitive
    if level == "clean":
        df.drop(columns=[c for c in sensitive_fields if c in df.columns], inplace=True)
        return df

    return df
