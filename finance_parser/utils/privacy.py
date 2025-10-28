import re
import pandas as pd




def mask_value(value: str) -> str:
    """Mask sensitive strings (UPI IDs, cheque numbers, txn IDs)."""
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
    """Apply privacy transformations to a DataFrame based on level and field rules."""
    df = df.copy()

    if level == "full":
        return df

    # Drop or mask fields
    if level == "masked":
        for col, lvl in sensitive_fields.items():
            if col in df.columns:
                if lvl == 1:
                    df.drop(col, axis=1, inplace=True)
                else:
                    df[col] = df[col].apply(mask_value)

    # Anonymized — drop everything sensitive
    if level == "anonymized":
        all_sensitive = list(set(sensitive_fields.get("to_mask", []) + sensitive_fields.get("to_drop", [])))
        df.drop(columns=[c for c in all_sensitive if c in df.columns], inplace=True)
        return df

    return df
