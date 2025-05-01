from fitparse import FitFile
import pandas as pd

def parse_fit_file(filepath, prefix=None):
    fitfile = FitFile(str(filepath))
    records = []

    for record in fitfile.get_messages('record'):
        fields = {field.name: field.value for field in record if field.value is not None}
        records.append(fields)

    df = pd.DataFrame(records)
    if prefix:
        df = df.add_prefix(prefix + "_")

    return df

def generate_prefixed_merged_df(garmin_path, stryd_path):
    """
    Load Garmin and Stryd .fit files, apply field prefixes, and merge by time.

    Returns:
        pd.DataFrame: Combined dataframe with Garmin and Stryd columns preserved
    """
    df_garmin = parse_fit_file_with_prefix(garmin_path, "Garmin")
    df_stryd = parse_fit_file_with_prefix(stryd_path, "Stryd")

    if "Garmin_timestamp" in df_garmin:
        df_garmin["elapsed_time_s"] = (
            df_garmin["Garmin_timestamp"] - df_garmin["Garmin_timestamp"].iloc[0]
        ).dt.total_seconds()

    if "Stryd_timestamp" in df_stryd:
        df_stryd["elapsed_time_s"] = (
            df_stryd["Stryd_timestamp"] - df_stryd["Stryd_timestamp"].iloc[0]
        ).dt.total_seconds()

    merged = pd.merge_asof(
        df_garmin.sort_values("elapsed_time_s"),
        df_stryd.sort_values("elapsed_time_s"),
        on="elapsed_time_s",
        direction="nearest"
    )

    return merged


def parse_fit_file_with_prefix(filepath, source_label):
    """
    Parse a .fit file and tag each field with a source-specific prefix.

    Args:
        filepath (str or Path): Path to the .fit file
        source_label (str): Prefix to attach to each field name (e.g., 'Garmin', 'Stryd')

    Returns:
        pd.DataFrame: Parsed and prefixed dataframe
    """
    fitfile = FitFile(str(filepath))
    records = []

    for record in fitfile.get_messages("record"):
        row = {field.name: field.value for field in record if field.value is not None}
        records.append(row)

    df = pd.DataFrame(records)

    if not df.empty:
        df.rename(columns=lambda col: f"{source_label} {col}" if col != "timestamp" else f"{source_label}_timestamp", inplace=True)

    return df

def generate_prefixed_merged_df(garmin_path, stryd_path):
    """
    Load Garmin and Stryd .fit files, apply field prefixes, and merge by time.

    Returns:
        pd.DataFrame: Combined dataframe with Garmin and Stryd columns preserved
    """
    df_garmin = parse_fit_file_with_prefix(garmin_path, "Garmin")
    df_stryd = parse_fit_file_with_prefix(stryd_path, "Stryd")

    if "Garmin_timestamp" in df_garmin:
        df_garmin["elapsed_time_s"] = (
            df_garmin["Garmin_timestamp"] - df_garmin["Garmin_timestamp"].iloc[0]
        ).dt.total_seconds()

    if "Stryd_timestamp" in df_stryd:
        df_stryd["elapsed_time_s"] = (
            df_stryd["Stryd_timestamp"] - df_stryd["Stryd_timestamp"].iloc[0]
        ).dt.total_seconds()

    merged = pd.merge_asof(
        df_garmin.sort_values("elapsed_time_s"),
        df_stryd.sort_values("elapsed_time_s"),
        on="elapsed_time_s",
        direction="nearest"
    )

    return merged


