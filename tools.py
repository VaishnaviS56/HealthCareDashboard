import matplotlib

matplotlib.use("Agg")
import os
import uuid
import matplotlib.pyplot as plt
import pandas as pd
from langchain_core.tools import tool
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = None

def init_df_for_tools(file_path):
    global df
    df = pd.read_csv(file_path)

def create_chart_path():
    return os.path.join(
        OUTPUT_DIR,
        f"{uuid.uuid4()}.png"
    )

def is_numeric(column):
    return pd.api.types.is_numeric_dtype(df[column])


def validation_error(message):
    return {
        "error": message
    }

def is_temporal_or_ordered(column):
    
    name = column.lower()

    temporal_keywords = [
        "year",
        "month",
        "date",
        "time",
        "quarter",
        "week",
        "day"
    ]

    return any(
        keyword in name
        for keyword in temporal_keywords
    )

from textwrap import fill

def wrap_label(text, width=25):
    return fill(str(text), width=width)

@tool
def plot_line_chart(x_col, y_col):
    """
    Create a line chart.

    Use for:
    - trends over time
    - changes across an ordered sequence

    X-axis:
    - temporal or ordered column

    Y-axis:
    - numerical column

    Avoid:
    - identifiers
    - unordered categorical columns
    """

    if x_col not in df.columns:
        return validation_error(f"{x_col} does not exist")

    if y_col not in df.columns:
        return validation_error(f"{y_col} does not exist")

    if not is_numeric(y_col):
        return validation_error(
            f"Line chart requires numeric y column. {y_col} is {df[y_col].dtype}"
        )
    
    if not is_temporal_or_ordered(x_col):
        return validation_error(
            f"{x_col} is not a temporal or ordered column"
        )

    output_path = create_chart_path()

    plt.figure(figsize=(12, 6))

    plt.plot(df[x_col], df[y_col])

    plt.xticks(rotation=45)

    plt.xlabel(wrap_label(x_col))
    plt.ylabel(wrap_label(y_col))
    plt.title(
        wrap_label(
            f"{y_col} vs {x_col}",
            width=40
        )
    )

    plt.tight_layout(pad=2)

    plt.savefig(output_path)
    plt.close()

    return {
        "image_path": output_path,
        "chart_type": "line",
        "columns": [x_col, y_col]
    }
@tool
def plot_scatter_chart(x_col, y_col):
    """
    Create a scatter plot.

    Use for:
    - relationships between two numerical variables
    - correlation exploration

    X-axis:
    - numerical column

    Y-axis:
    - numerical column

    Avoid:
    - identifiers
    - categorical columns
    """

    if x_col not in df.columns:
        return validation_error(f"{x_col} does not exist")

    if y_col not in df.columns:
        return validation_error(f"{y_col} does not exist")

    if not is_numeric(x_col):
        return validation_error(
            f"Scatter chart requires numeric x column. {x_col} is {df[x_col].dtype}"
        )

    if not is_numeric(y_col):
        return validation_error(
            f"Scatter chart requires numeric y column. {y_col} is {df[y_col].dtype}"
        )

    output_path = create_chart_path()

    plt.figure(figsize=(10, 6))

    plt.scatter(
        df[x_col],
        df[y_col]
    )

    plt.xlabel(wrap_label(x_col))
    plt.ylabel(wrap_label(y_col))

    plt.title(
        wrap_label(
            f"{y_col} vs {x_col}",
            width=40
        )
    )

    plt.tight_layout(pad=2)

    plt.grid(alpha=0.3)

    plt.savefig(output_path)
    plt.close()

    return {
        "image_path": output_path,
        "chart_type": "scatter",
        "columns": [x_col, y_col]
    }

@tool
def plot_bar_chart(category_col, value_col):
    """
    Create a bar chart.

    Use for:
    - comparing categories
    - comparing averages across groups
    - ranking categories

    Category Axis:
    - categorical column

    Value Axis:
    - numerical column

    Good examples:
    - state vs vaccination_rate
    - district vs literacy_rate
    - region vs infant_mortality_rate

    Avoid:
    - identifiers
    - categories with very large numbers of unique values
    """

    if category_col not in df.columns:
        return validation_error(f"{category_col} does not exist")

    if value_col not in df.columns:
        return validation_error(f"{value_col} does not exist")

    if is_numeric(category_col):
        return validation_error(
            f"Bar chart category column should be categorical. {category_col} is numeric."
        )

    if not is_numeric(value_col):
        return validation_error(
            f"Bar chart value column must be numeric. {value_col} is {df[value_col].dtype}"
        )

    if df[category_col].nunique() > 50:
        return validation_error(
            f"{category_col} has too many categories for a useful bar chart."
        )

    output_path = create_chart_path()

    grouped = (
        df.groupby(category_col)[value_col]
        .mean()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(14, 7))

    plt.bar(
        grouped.index.astype(str),
        grouped.values
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.xlabel(
        wrap_label(category_col)
    )

    plt.ylabel(
        wrap_label(value_col)
    )

    plt.title(
        wrap_label(
            f"{value_col} by {category_col}",
            width=40
        )
    )

    plt.tight_layout(pad=2)

    plt.savefig(output_path)
    plt.close()

    return {
        "image_path": output_path,
        "chart_type": "bar",
        "columns": [category_col, value_col]
    }

@tool
def plot_pie_chart(category_col):
    """
    Create a pie chart.

    Use for:
    - showing proportions of a whole
    - displaying composition across a small number of categories

    Input:
    - categorical column

    Good examples:
    - gender
    - region
    - disease_category

    Prefer:
    - 2 to 8 categories

    Avoid:
    - identifiers
    - many categories
    - categories where comparison is more important than composition
    """

    if category_col not in df.columns:
        return validation_error(f"{category_col} does not exist")

    if is_numeric(category_col):
        return validation_error(
            f"Pie chart requires a categorical column. {category_col} is numeric."
        )

    unique_categories = df[category_col].nunique()

    if unique_categories > 8:
        return validation_error(
            f"{category_col} has too many categories for a useful pie chart."
        )

    output_path = create_chart_path()

    counts = df[category_col].value_counts()

    plt.figure(figsize=(8, 8))

    plt.pie(
        counts.values,
        labels=counts.index.astype(str),
        autopct="%1.1f%%"
    )

    plt.title(
        wrap_label(
            f"{category_col} Distribution",
            width=40
        )
    )

    plt.tight_layout(pad=2)

    plt.savefig(output_path)
    plt.close()

    return {
        "image_path": output_path,
        "chart_type": "pie",
        "columns": [category_col]
    }
