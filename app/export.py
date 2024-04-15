import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import settings
import tools.prints as prints
from matplotlib.backends.backend_pdf import PdfPages


def legal_df(df, info):
    if df.empty:
        prints.error("export_bar", f"No data after filtering: {info}")
        return False
    return True


def export_heatmap(df, key, title, hightlight: str = ""):
    if legal_df(df, title):
        return scattergram_goals_time(df, 5, key, title, hightlight)


def export_series(series, title):
    value_counts = series.value_counts()

    # Plot as a bar chart
    ax = value_counts.plot(kind='bar', label="TBV")

    # Add labels and title
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title(title)

    # Add counts on top of each bar
    for i, v in enumerate(value_counts):
        ax.text(i, v + 0.1, str(v), ha='center')
    plt.xticks(rotation=15, ha='right')

    # Show the plot
    plt.show()


def export_assists(df, title):
    if not legal_df(df, title):
        return
    df.fillna("Unreported", inplace=True)
    how_counts = df["how"].value_counts()

    # Plotting the bar chart
    ax = how_counts.plot(kind='bar')

    # Adding labels and title
    plt.xlabel('Type')
    plt.ylabel('Count')
    plt.title(title)

    # Adding the counts on top of each bar
    for p in ax.patches:
        ax.annotate(str(p.get_height()),
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 5), textcoords='offset points')
    plt.xticks(rotation=15, ha='right')

    # Display the plot
    plt.show()


def filter_dataframe(dataframe: pd.DataFrame, keys: list[str] = None, keep: tuple = None):
    """
    dataframe: DataFrame
    keys: list with keys from DF, ["type", "time", "name"] will return DF with only those columns
    keep: tuple  with a key from DF and what that key should be
    """
    print("UNUSED? filter_dataframe")
    exit()
    if keys:
        dataframe = dataframe[keys]
    if keep:
        dataframe = dataframe[dataframe[keep[0]] == keep[1]]
    return dataframe


def scattergram_goals_time(dataframe: pd.DataFrame,
                           interval: int,
                           key: str,
                           header: str = "",
                           highlight: str = ""):
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

    # Highlight rows where key is "current" with a red box
    if highlight:
        highlight_row = pivot_df.index == highlight
        # Adding the red box
        for i, cond in enumerate(highlight_row):
            if cond:
                plt.gca().add_patch(plt.Rectangle((0, i), pivot_df.shape[1], 1, fill=False, edgecolor='red', lw=2))

    plt.tight_layout()

    folder = f"{os.getcwd()}/{settings.FOLDER}/plots"
    if not os.path.isdir(folder):
        os.mkdir(folder)
    return plt.gcf()
    # Save or display the plot
    #  plt.savefig(f"files/plots/{header}.png")  # Save the plot as an image
    plt.show()  # Display the plot


def export_game_pdf(tournament, team):
    frames = []
    for t in tournament.team:
        for player in tournament.team[t].players:
            df = player.events_to_df()
            df["name"] = player.name
            df["team"] = t
            frames.append(df)

    df = pd.concat(frames, ignore_index=True)
    df.fillna("Unreported", inplace=True)

    # Goals scored
    goals_scored_df = df[df["type"] == "Goal"]
    goal_per_team_fig = export_heatmap(goals_scored_df,
                                       "team",
                                       f"Goals scored in {tournament.name}",
                                       team.name)
    goals_scored_team_df = goals_scored_df[goals_scored_df["team"] == team.name]
    goal_per_player_fig = export_heatmap(goals_scored_team_df,
                                         "name",
                                         f"Goals scored by {team.name}")
    pdf_file = "multiple_plots.pdf"
    with PdfPages(pdf_file) as pdf:
        pdf.savefig(goal_per_team_fig, bbox_inches='tight')
        pdf.savefig(goal_per_player_fig, bbox_inches='tight')

    plt.close(goal_per_team_fig)
    plt.close(goal_per_player_fig)

    import subprocess
    subprocess.Popen([pdf_file], shell=True)

    return
    goals_scored_team_df = goals_scored_df[goals_scored_df["team"] == team.name]
    goal_per_player_pdf = export_heatmap(goals_scored_team_df,
                                         "name",
                                         f"Goals scored for {team.name}")
