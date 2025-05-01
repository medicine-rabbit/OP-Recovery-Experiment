import pandas as pd

def detect_stride_end_times(df: pd.DataFrame, cadence_col="garmin_cadence", min_cadence=130, min_duration=3.0) -> list:
    """
    Detects stride segments based on cadence spikes and returns stride end times.

    Args:
        df (pd.DataFrame): DataFrame with 'elapsed_time_s' and cadence
        cadence_col (str): Name of the cadence column
        min_cadence (int): Threshold to consider running vs walking
        min_duration (float): Minimum duration of a stride burst (seconds)

    Returns:
        List[float]: List of stride end times in seconds
    """
    stride_end_times = []
    in_stride = False
    stride_start_time = None

    for i, row in df.iterrows():
        time = row["elapsed_time_s"]
        cadence = row.get(cadence_col, 0) * 2 # Convert per-leg to full SPM

        if cadence >= min_cadence:
            if not in_stride:
                in_stride = True
                stride_start_time = time
        else:
            if in_stride:
                in_stride = False
                stride_duration = time - stride_start_time
                if stride_duration >= min_duration:
                    stride_end_times.append(time)

    return stride_end_times
