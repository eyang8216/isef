"""Professional plot styling utilities for publication-quality figures."""

import plotly.graph_objects as go


def apply_academic_style(fig: go.Figure, title: str = "", height: int = 500) -> go.Figure:
    """Apply consistent academic styling to Plotly figures.

    Args:
        fig: Plotly figure object
        title: Figure title
        height: Figure height in pixels (default 500 for more space)

    Returns:
        Styled figure
    """
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, family="serif", color="#2c3e50"),
            x=0.5,
            xanchor="center",
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="serif", size=12, color="#2c3e50"),
        height=height,
        margin=dict(l=80, r=80, t=80, b=80),  # Generous margins
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="#e0e0e0",
            showline=True,
            linewidth=2,
            linecolor="#2c3e50",
            mirror=True,
            ticks="outside",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="#e0e0e0",
            showline=True,
            linewidth=2,
            linecolor="#2c3e50",
            mirror=True,
            ticks="outside",
            tickfont=dict(size=11),
        ),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#2c3e50",
            borderwidth=1,
            font=dict(size=11),
        ),
    )

    return fig


def get_academic_colorscale(field_type: str = "potential"):
    """Get appropriate colorscale for different field types.

    Args:
        field_type: Type of field ('potential', 'field', 'residual', 'charge')

    Returns:
        Plotly colorscale name
    """
    colorscales = {
        "potential": "Viridis",
        "field": "Plasma",
        "residual": "RdBu",
        "charge": "Reds",
        "generic": "Viridis",
    }
    return colorscales.get(field_type, "Viridis")


def add_export_buttons(fig: go.Figure) -> go.Figure:
    """Add export buttons to figure for download.

    Args:
        fig: Plotly figure object

    Returns:
        Figure with export configuration
    """
    fig.update_layout(
        modebar_add=[
            "v1hovermode",
            "toggleSpikeLines",
            "hoverclosest",
            "hovercompare",
        ]
    )

    return fig
