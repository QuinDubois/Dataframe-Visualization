# CSS related styles
STYLES = {
    "chart_background": "#424257",
    "chart_grid": "#232345",
    "tick_font": "#CACADD",
    "font": "#CACADD",
    "line_colors": [
        "#21A0A6"
    ],
    "marker_colors": [
        "#FAEA48",
        "#c47e0e",
        "#4951de",
        "#bd51c9",
        "#4cbf39",
        "#c95034",
    ],
    "margins": {
        "r": 10,
        "l": 20,
        "t": 50,
        "b": 10
    }
}

# Flags and color associations
trace_styles = {
    "base": STYLES["line_colors"][0],
    "above average": STYLES["marker_colors"][0],
    "below average": STYLES["marker_colors"][1],
    "deviation above": STYLES["marker_colors"][2],
    "deviation below": STYLES["marker_colors"][3],
    "trending up": STYLES["marker_colors"][4],
    "trending down": STYLES["marker_colors"][5]
}

empty_chart_layout = dict(
    paper_bgcolor=STYLES['chart_background'],
    plot_bgcolor=STYLES['chart_background'],
    autofill=True,
    margin={ "r": 0, "t": 0, "l": 0, "b": 0 }
)
