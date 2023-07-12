import pandas as pd
from pandas.api.types import is_numeric_dtype
import plotly.graph_objects as go
import statsmodels.api as sm
import datetime

from resources.style_imports import STYLES, trace_styles


# Simple temporal line plot.
def plot_timeseries(df: pd.DataFrame = None, time_field='time', data_field='value') -> go.Figure:
    if df is None:
        return default_chart()
    else:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df[time_field].values,
            y=df[data_field].values,
            mode='lines',
            line=dict(color=STYLES["line_colors"][0]),
            name=data_field
        ))

        fig = style_chart(fig, data_field)
        return fig


# Control plotting function
def plot_control(df, time_field, data_field, segments, control_list, trend_toggle):
    if df is None:
        return default_chart()
    else:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df[time_field],
            y=df[data_field],
            mode='lines',
            line_color=STYLES['line_colors'][0],
            showlegend=False
        ))

        print_trend = True

        for key in control_list:
            if key in ['trending up', 'trending down'] and print_trend:
                fig = plot_trends(fig, df, segments, data_field, time_field, trend_toggle, control_list)
                print_trend = False
            else:
                if key not in ['trending up', 'trending down']:
                    key_filter = key + ' mask'
                    df_by_filter = df.loc[df[key_filter] == 1]
                    fig.add_trace(go.Scatter(
                        x=df_by_filter[time_field],
                        y=df_by_filter[data_field],
                        mode='markers',
                        name=key,
                        marker_color=trace_styles[key],
                        showlegend=True
                    ))

        fig = style_chart(fig, data_field)
        return fig


def plot_trends(fig, df, segments, data_field, time_field, trend_toggle, control_list):
    for start_idx, end_idx in zip(segments[:-1], segments[1:]):
        segment = df.iloc[start_idx:end_idx + 1, :].copy()

        # Serialize the temporal column if it isn't already numeric
        if not is_numeric_dtype(segment[time_field]):
            segment['serial_time'] = [(d - datetime.datetime(1970, 1, 1)).days for d in segment[time_field]]
        else:
            segment['serial_time'] = segment[time_field]

        # Fit serialized time values in order to display trends properly
        x = sm.add_constant(segment['serial_time'])
        model = sm.OLS(segment[data_field], x).fit()
        segment['fitted_values'] = model.fittedvalues

        fit_color = trace_styles['trending up'] if model.params['serial_time'] > 0 \
            else trace_styles['trending down']

        trend_name = "Trending Up" if model.params['serial_time'] > 0 else "Trending Down"

        # Determine whether the current segment should be printed or not.
        if trend_toggle:
            if ('trending up' in control_list and model.params['serial_time'] > 0) \
                    or ('trending down' in control_list and model.params['serial_time'] <= 0):
                fig = add_trend_trace(fig, time_field, segment, trend_name, fit_color)
        else:
            if model.f_pvalue < 0.05:
                if ('trending up' in control_list and model.params['serial_time'] > 0) \
                        or ('trending_down' in control_list and model.params['serial_time'] <= 0):
                    fig = add_trend_trace(fig, time_field, segment, trend_name, fit_color)

    # Ensure duplicate legend items get removed
    legend_names = set()
    fig.for_each_trace(
        lambda trace:
        trace.update(showlegend=False) if (trace.name in legend_names) else legend_names.add(trace.name)
    )

    return fig


def default_chart() -> go.Figure:
    fig = go.Figure({'data': {'x': [0], 'y': [0]}})
    fig = style_chart(fig, 'data')
    return fig


def add_trend_trace(fig: go.Figure, time_field, segment, trend_name, fit_color) -> go.Figure:
    fig.add_trace(go.Scatter(
        x=segment[time_field],
        y=segment['fitted_values'],
        mode='lines',
        line=dict(color=fit_color),
        name=trend_name,
    ))
    return fig


# In order to keep the charts visually consistent, all generalized style options will be changed here.
def style_chart(fig: go.Figure, data_field) -> go.Figure:
    fig.update_layout(
        {
            'yaxis': {
                'title': data_field,
                'tickfont': {'color': STYLES["tick_font"]},
                'gridcolor': STYLES["chart_grid"],
                'fixedrange': True
            },
            'xaxis': {
                'title': "time",
                'tickfont': {'color': STYLES["tick_font"]},
                'gridcolor': STYLES["chart_grid"],
                'fixedrange': False
            },
            'hovermode': "closest",
            'legend': dict(orientation="v"),
            'autosize': True,
            'paper_bgcolor': STYLES["chart_background"],
            'plot_bgcolor': STYLES["chart_background"],
            'font': {'color': STYLES["font"]},
            'margin': STYLES["margins"]
        }
    )

    return fig
