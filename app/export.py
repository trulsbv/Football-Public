import tools.plot as plot
import tools.prints as prints
import pandas as pd
import matplotlib.pyplot as plt


def export_scored_goals_team(df: pd.DataFrame, team: str, freq: int = 5) -> None:
    """
    Creates a scattergram with each of the player's goals per freq for the given team

    Input:
        * df: as a DataFrame with all events
        * freq: int frequency
    """
    prints.error("SHOULD BE DELETED")
    exit()
    df = plot.filter_dataframe(df, keep=("team", team))
    keys = ["type", "time", "team", "name"]
    export_scored_goals(df, "name", keys, freq,
                        f"{team} - Goals scored per {freq}-minute interval (by player)")


def export_conceded_goals_team(df: pd.DataFrame, team: str, freq: int = 5) -> None:
    """
    Creates a scattergram with each of the player's goals per freq for the given team

    Input:
        * df: as a DataFrame with all events
        * freq: int frequency
    """
    prints.error("SHOULD BE DELETED")
    exit()
    print(df)
    df = plot.filter_dataframe(df, keep=("team", team))
    keys = ["type", "time", "team", "name"]
    export_conceded_goals(df, "name", keys, freq,
                          f"{team} - Goals conceded per {freq}-minute interval (by player)")


def export_scored_goals_league(df: pd.DataFrame, freq: int = 5, league: str = None) -> None:
    """
    Creates a scattergram with each of the team's goals per freq for the given team

    Input:
        * df as a DataFrame with all events
        * freq int frequency
        * league (optional) to give the header and filename context
    """
    prints.error("SHOULD BE DELETED")
    exit()
    keys = ["type", "time", "team", "name"]
    export_scored_goals(df, "team", keys, freq,
                        f"{league} - Goals scored per {freq}-minute interval (by team)")


def export_conceded_goals_league(df: pd.DataFrame, freq: int = 5, league: str = None) -> None:
    """
    Creates a scattergram with each of the team's goals per freq for the given team

    Input:
        * df as a DataFrame with all events
        * freq int frequency
        * league (optional) to give the header and filename context
    """
    prints.error("SHOULD BE DELETED")
    exit()
    keys = ["type", "time", "team", "name"]
    export_conceded_goals(df, "team", keys, freq,
                          f"{league} - Goals conceded per {freq}-minute interval (by team)")


def export_scored_goals(df, key: str, keys: list, freq: int, msg: str) -> None:
    prints.error("SHOULD BE DELETED")
    exit()
    DF = plot.filter_dataframe(df, keys=keys, keep=("type", "Goal"))
    plot.scattergram_goals_time(DF, freq, key, msg)


def export_conceded_goals(df, key: str, keys: list, freq: int, msg: str) -> None:
    prints.error("SHOULD BE DELETED")
    exit()
    DF = plot.filter_dataframe(df, keys=keys, keep=("type", "ConcededGoal"))
    plot.scattergram_goals_time(DF, freq, key, msg)


def legal_df(df, info):
    if df.empty:
        prints.error("export_bar", f"No data after filtering: {info}")
        return False
    return True


def export_heatmap(df, key, title):
    if legal_df(df, title):
        plot.scattergram_goals_time(df, 5, key, title)


def export_series(series, title):
    value_counts = series.value_counts()

    # Plot as a bar chart
    ax = value_counts.plot(kind='bar')

    # Add labels and title
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Frequency of Values in Series')

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
    plt.xlabel('Type of assist')
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
