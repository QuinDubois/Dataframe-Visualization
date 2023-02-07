import pandas as pd
import numpy as np


# Aggregate process
def aggregate_dataframe(df, time_field, data_field, agg_type) -> pd.DataFrame:
    temp_df = df
    agg_df = pd.DataFrame()
    agg_field = time_field

    if time_field != 'year':
        agg_field = 'year'
        temp_df['year'] = pd.DatetimeIndex(df[time_field]).year

    if agg_type == 'mean':
        agg_df = temp_df.groupby(agg_field).mean().reset_index()

    # TODO: Solve some of the commented out code below being weird.

    # if the dataset is of even length, round down to the next closest median.
    if agg_type == "median":
        # if len(temp_df.index) % 2 == 0:
        #     sorted_df = temp_df.sort_values(by=[data_field], ascending=True)
        #     agg_df = sorted_df.groupby(agg_field).apply(
        #         lambda x: x[x[agg_field] == x[agg_field].iloc[0:(int(len(x) - 1))].median()])
        # else:
        #     agg_df = temp_df.groupby(agg_field).apply(
        #         lambda x: x[x[agg_field] == x[agg_field].median()])
        agg_df = temp_df.groupby(agg_field).median().reset_index()

    if agg_type == "max":
        # agg_df = temp_df.groupby(agg_field).apply(lambda x: x[x[agg_field] == x[agg_field].max()])
        agg_df = temp_df.groupby(agg_field).max().reset_index()

    if agg_type == "min":
        # agg_df = temp_df.groupby(agg_field).apply(lambda x: x[x[agg_field] == x[agg_field].min()])
        agg_df = temp_df.groupby(agg_field).min().reset_index()

    return agg_df


# Data Sorter for Control plot
def data_sort(df, time_field, data_field, trend_size, deviation_coefficient, control_options, trend_toggle):
    avg = np.average(df[data_field])
    std = np.std(df[data_field])
    segments = []

    for key in control_options:
        if key == 'above average':
            df[key + ' mask'] = np.where(df[data_field].values >= avg, 1, 0)
        if key == 'below average':
            df[key + ' mask'] = np.where(df[data_field].values < avg, 1, 0)
        if key == 'deviation above':
            df[key + ' mask'] = np.where(df[data_field].values >= avg + (std * deviation_coefficient), 1, 0)
        if key == 'deviation below':
            df[key + ' mask'] = np.where(df[data_field].values < avg - (std * deviation_coefficient), 1, 0)

        if key in ['trending up', 'trending down']:
            segments = trend_by_slope(df, data_field, trend_size)

    return df, segments


def trend_by_slope(df, data_field, trend_size):
    min_change = trend_size
    curr_changes = 0
    last_sign = 1
    last_change_idx = 0
    bounds_idx = [0]
    cumulative_slope = [0]

    df['row'] = np.arange(len(df))

    for i in range(1, df.shape[0]):
        segment = df.iloc[0:i + 1, :]

        slope = calc_slope(segment, data_field)
        cumulative_slope.append(slope)

        # compare the current cumulative slope with the previous, and keep track of whether it increased or decreased
        # as well as how many times it has changed in that direction, and where it last changed direction
        if abs(cumulative_slope[i]) < abs(cumulative_slope[i - 1]):
            if last_sign == 1:
                curr_changes = 0
            if curr_changes == 0:
                last_change_idx = i
            curr_changes += 1
            last_sign = -1

        elif abs(cumulative_slope[i]) > abs(cumulative_slope[i - 1]):
            if last_sign == -1:
                curr_changes = 0
            if curr_changes == 0:
                last_change_idx = i
            curr_changes += 1
            last_sign = 1

        # if we meet the minimum amount of times the slope changes in a direction, mark the last time it changed
        # and reset the change counter
        if curr_changes == min_change:
            curr_changes = 0
            bounds_idx.append(last_change_idx)

    # add the last point in the dataset to the bounds just to ensure we encapsulate all points
    bounds_idx.append(df.shape[0] - 1)

    return bounds_idx


def calc_slope(df, data_field):
    slope = np.polyfit(df['row'], df[data_field], 1)
    return slope[0]
