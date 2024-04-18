import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import tools.prints as prints
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker as ticker
import subprocess


def fetch_goals_per_player_per_position(team):
    header = f"Type of goals by {team.name}:"
    figures = []
    frames = []
    for game in team.get_all_games():
        for event in game.events:
            data = event.high_level_dict()
            if data["name"] == "Goal" and data["team"] == team:
                if not isinstance(data["player"], str):
                    data["role"] = data["player"].role
                frames.append(data)
    df = pd.DataFrame(frames)
    df.fillna("Unreported", inplace=True)
    df.replace('', "Unreported", inplace=True)

    attack_df = df[df["role"] == "Attack"]
    mid_df = df[df["role"] == "midfield"]
    defence_df = df[df["role"] == "Defender"]

    if not attack_df.empty:
        figures.append(fetch_split_bar_chart(attack_df[["player", "type"]], f"{header} Attackers"))
    if not mid_df.empty:
        figures.append(fetch_split_bar_chart(mid_df[["player", "type"]], f"{header} Midfielders"))
    if not defence_df.empty:
        figures.append(fetch_split_bar_chart(defence_df[["player", "type"]], f"{header} Defenders"))
    return figures


def fetch_split_bar_chart(input_df, title):
    df = input_df.groupby(['type', 'player']).size().unstack(fill_value=0)
    ax = df.plot(kind='bar', stacked=True, figsize=(10, 6))

    # Adding labels and title
    plt.xlabel('Goal Type')
    plt.ylabel('Number of Contributions')
    plt.title(title)

    # Show legend
    plt.legend(title='Player')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Add counts for each player's type of goal inside their colored part of the column
    prev = {}
    for i in range(len(df)):
        prev[i] = 0

    for i, col in enumerate(df.columns):
        x = 0
        for j, val in enumerate(df[col]):
            if val != 0:
                plt.text(x, prev[j] + val / 2, str(val), ha='center', va='center', color='black')
                prev[j] += val
            x += 1

    # Set y-axis to display only whole numbers
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # Show plot
    plt.tight_layout()
    value = plt.gcf()
    plt.close()
    return value


def legal_df(df, info):
    if df.empty:
        prints.error("export_bar", f"No data after filtering: {info}")
        return False
    return True


def export_heatmap(df, key, title, hightlight: str = ""):
    if legal_df(df, title):
        scattergram_goals_time(df, 5, key, title, hightlight).show()


def export_assist(df, title):
    bar_chart(df, title)
    plt.show()


def fetch_heatmap(df, key, title, hightlight: str = ""):
    if legal_df(df, title):
        return scattergram_goals_time(df, 5, key, title, hightlight)


def export_series(series, title):
    value_counts = series.value_counts()

    # Plot as a bar chart
    ax = value_counts.plot(kind='bar')

    # Add labels and title
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title(title)

    # Add counts on top of each bar
    for i, v in enumerate(value_counts):
        ax.text(i, v + 0.1, str(v), ha='center')
    plt.xticks(rotation=15, ha='right')

    value = plt.gcf()
    plt.close()
    return value


def bar_chart(df, title, key="how"):
    if not legal_df(df, title):
        return
    how_counts = df[key].value_counts()
    colors = ['#1f77b4', '#ff7f0e']
    rep_colors = colors * (len(how_counts) // len(colors)) + colors[:len(how_counts) % len(colors)]
    ax = how_counts.plot(kind='bar', color=rep_colors[:len(how_counts)])

    # Adding labels and title
    plt.xlabel('Type')
    plt.ylabel('Count')
    plt.title(title)

    # Adding the counts on top of each bar
    for p, color in zip(ax.patches, rep_colors):
        ax.annotate(str(p.get_height()),
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 5), textcoords='offset points',
                    color=color)
    plt.xticks(rotation=45, ha='right')
    for label, color in zip(ax.get_xticklabels(), rep_colors[:len(how_counts)]):
        label.set_color(color)

    value = plt.gcf()
    plt.close()
    return value


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

    # Create the heatmap
    sns.heatmap(pivot_df, cmap="viridis", annot=True, fmt=".0f", linewidths=0.5)

    # Annotate the row and column totals
    for i in range(pivot_df.shape[0]):
        plt.text(pivot_df.shape[1] + 0.5, i + 0.5, str(int(pivot_df.iloc[i, :].sum())),
                 ha='center', va='center', fontweight='bold', color='black')

    for j in range(pivot_df.shape[1]):
        plt.text(j + 0.5, -0.25, str(int(pivot_df.iloc[:, j].sum())),
                 ha='center', va='center', fontweight='bold', color='black')

    plt.xlabel("Minute")
    plt.ylabel(key.title())
    plt.title(header, y=1.05)
    plt.yticks(rotation=0)

    # Highlight rows where key is "current" with a red box
    if highlight:
        highlight_row = pivot_df.index == highlight
        # Adding the red box
        for i, cond in enumerate(highlight_row):
            if cond:
                plt.gca().add_patch(plt.Rectangle((0, i), pivot_df.shape[1], 1,
                                                  fill=False, edgecolor='red', lw=2))

    plt.tight_layout()
    value = plt.gcf()
    plt.close()
    return value


def fetch_team_player_usage(team):
    frames = []
    for game in team.get_all_games():
        t = game.team_to_type(team)
        for player in game.teams[t]["lineup"][0]:
            frames.append({"name": player})
    df = pd.DataFrame(frames)
    return bar_chart(df, f"Starting players for {team.name}", "name")


def file_friendly_name(name):
    name = name.replace("/", "_")
    name = name.replace(".", "")
    return name


def export_team_pdf(tournament, team):
    figures = []

    # Counts the number of times the players have been in the XI
    figures.append(fetch_team_player_usage(team))

    # Create a DataFrame with events
    frames = []
    for t in tournament.team:
        for player in tournament.team[t].players:
            df = player.events_to_df()
            df["name"] = player.name
            df["team"] = t
            frames.append(df)

    df = pd.concat(frames, ignore_index=True)
    df.fillna("Unreported", inplace=True)
    df.replace('', "Unreported", inplace=True)

    # Goals scored in the league
    goals_scored_df = df[df["type"] == "Goal"]

    figures.append(fetch_heatmap(goals_scored_df,
                                 "team",
                                 f"Goals scored in {tournament.name}",
                                 team.name))

    # Goals scored by each player in the team
    goals_scored_team_df = goals_scored_df[goals_scored_df["team"] == team.name]
    figures.append(fetch_heatmap(goals_scored_team_df,
                                 "name",
                                 f"Goals scored by {team.name}"))

    # Type of goals by the team
    type_of_goal_team_df = goals_scored_df[["team", "by", "how"]]
    type_of_goal_team_df = type_of_goal_team_df[type_of_goal_team_df["team"] == team.name]
    figures.append(bar_chart(type_of_goal_team_df,
                             f"Type of goals by {team.name}"))

    # Type of goals per "role"
    for figure in fetch_goals_per_player_per_position(team):
        figures.append(figure)

    # Type of assists by the team
    assist_df = df[df["type"] == "Assist"]
    assist_df = assist_df[["team", "by", "how"]]
    assist_df = assist_df[assist_df["team"] == team.name]
    figures.append(bar_chart(assist_df, f"Type of assists by {team.name}"))

    # Assist graph
    figures.append(team.graphs["assists"].export_graph(team.name))

    # Goals conceded in the league
    goals_conceded_df = df[df["type"] == "ConcededGoal"]
    figures.append(fetch_heatmap(goals_conceded_df,
                                 "team",
                                 f"Goals conceded in {tournament.name}",
                                 team.name))

    # Type of goals against the team
    type_of_conceded_df = goals_conceded_df[["team", "by", "how", "assist"]]
    type_of_conceded_df = type_of_conceded_df[type_of_conceded_df["team"] == team.name]
    figures.append(bar_chart(type_of_conceded_df,
                             f"Goals against {team.name}"))

    # Type of assists against the team
    type_of_conceded_df = type_of_conceded_df[type_of_conceded_df["team"] == team.name]
    figures.append(bar_chart(type_of_conceded_df,
                             f"Assists against {team.name}",
                             key="assist"))

    # Creates PDF
    pdf_file = f"{file_friendly_name(tournament.name)} - {file_friendly_name(team.name)}.pdf"
    with PdfPages(pdf_file) as pdf:
        for figure in figures:
            if figure:
                pdf.savefig(figure, bbox_inches='tight', dpi=300)
        plt.close(figure)

    # Displays the PDF and deletes it once user is finsihed with it
    pdf_process = subprocess.Popen([pdf_file], shell=True)
    prints.info(sender="Export:", message=f"Waiting for '{pdf_file}' to be closed", newline=True)
    pdf_process.wait()
    os.remove(f"{pdf_file}")
