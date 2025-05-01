import pandas as pd

def get_peak_hr_after_stride(df: pd.DataFrame, stride_end_time: float, buffer_window: float = 45.0) -> float:
    """Return the max HR in the 45s after a stride."""
    if 'elapsed_time_s' not in df or 'garmin_heart_rate' not in df:
        raise ValueError("Missing required columns.")
    rest_window = df[
        (df['elapsed_time_s'] >= stride_end_time) &
        (df['elapsed_time_s'] < stride_end_time + buffer_window)
    ]
    if rest_window.empty or rest_window['garmin_heart_rate'].isnull().all():
        return None
    return float(rest_window['garmin_heart_rate'].max())


def get_stride_duration(df: pd.DataFrame, stride_start_time: float, stride_end_time: float) -> float:
    """Return duration of a stride in seconds."""
    return float(stride_end_time - stride_start_time)


def get_avg_power(df, start_time: float, end_time: float, source="Garmin") -> float:
    """
    Compute average power over a stride interval from the specified source.

    Args:
        df (pd.DataFrame): Merged dataframe with source-tagged power columns
        start_time (float): Start of stride (elapsed_time_s)
        end_time (float): End of stride
        source (str): 'Garmin' or 'Stryd'

    Returns:
        float: Average power in watts, or None if not available
    """
    col_name = f"{source} Power"

    segment = df[(df["elapsed_time_s"] >= start_time) & (df["elapsed_time_s"] <= end_time)]

    if col_name in segment and not segment[col_name].isnull().all():
        return float(segment[col_name].mean())  # ✅ correct


    return None



