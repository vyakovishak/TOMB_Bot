import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

## sample DataFrames
df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

fig = px.scatter(df1, x='A', y='B')

fig.add_annotation(text="Absolutely-positioned annotation",
                   x=2.5, y=4.5, showarrow=False)

layout = go.Layout(
    template="plotly_white",
    title="<b>O-C diagram</b>",
    font_family="Trebuchet",
    title_font_family="Trebuchet",
    title_font_color="Navy",

    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.83,
        font=dict(
            family="Trebuchet",
            size=20,
            color="black"
        ),
        bgcolor="LightGray",
        bordercolor="Black",
        borderwidth=0
    ),
    xaxis_title=r'<i>T</i>',
    yaxis_title=r'O',
    title_x=0.5,
    font=dict(
        family="Trebuchet",
        size=71,
        color="Black"
    ),
)

fig.layout = layout

fig.show()
