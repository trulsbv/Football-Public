import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
import settings


def filter_dataframe(dataframe: pd.DataFrame, keys: list[str] = None, keep: tuple = None):
    """
    dataframe: DataFrame
    keys: list with keys from DF, ["type", "time", "name"] will return DF with only those columns
    keep: tuple  with a key from DF and what that key should be
    """
    if keys:
        dataframe = dataframe[keys]
    if keep:
        dataframe = dataframe[dataframe[keep[0]] == keep[1]]
    return dataframe


def scattergram_goals_time(dataframe: pd.DataFrame,
                           interval: int,
                           key: str,
                           header: str = ""):
    """
    Input:
        dataframe: DataFrame with type, time and name
                        type  time                name
                        Goal  45.0         Lyle Foster
        interval: int
        key: str with the data to group by, team for the whole team, name for individual player
    """
    goal_counts = (
        dataframe.groupby(
            [key, pd.cut(dataframe["time"], np.arange(0, (90 + interval), interval))]
        )
        .size()
        .reset_index(name="goal_count")
    )

    # Pivot the data to have players as rows and time intervals as columns
    pivot_df = goal_counts.pivot(
        index=key, columns="time", values="goal_count"
    ).fillna(0)

    # Convert column labels from intervals to strings
    pivot_df.columns = [str(col) for col in pivot_df.columns]

    # Plotting a heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_df, cmap="viridis", annot=True, fmt=".0f", linewidths=0.5)
    plt.xlabel("Minute")
    plt.ylabel(key.title())
    plt.title(header)
    plt.yticks(rotation=0)
    plt.tight_layout()

    folder = f"{os.getcwd()}/{settings.FOLDER}/plots"
    if not os.path.isdir(folder):
        os.mkdir(folder)

    # Save or display the plot
    plt.savefig(f"files/plots/{header}.png")  # Save the plot as an image
    plt.show()  # Display the plot
