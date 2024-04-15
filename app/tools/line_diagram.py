import plotly.express as px
import pandas as pd

# Creating a DataFrame from a dictionary
lyn = {
    'minutes': ['0-30', '30-60', '60-90'],
    'goals': [20, 45, 32]
}
vif = {
    'minutes': ['0-30', '30-60', '60-90'],
    'goals': [15, 25, 31]
}

df_lyn = pd.DataFrame(lyn)
df_vif = pd.DataFrame(vif)
print(df_lyn)
print(df_vif)

# Add a 'team' column to differentiate between Lyn and VIF
df_lyn['team'] = 'Lyn'
df_vif['team'] = 'VIF'

# Concatenate the two DataFrames
df_combined = pd.concat([df_lyn, df_vif])
print(df_combined)

hellund = [
    {
        "type": "goal",
        "assist": None,
        "time": 89
    },
    {
        "type": "substitution",
        "time": 55
    }
]

per = [
    {
        "type": "goal",
        "assist": "Paal",
        "time": 89
    },
    {
        "type": "yellow card",
        "time": 22
    }
]

hel_df = pd.DataFrame(hellund)
per_df = pd.DataFrame(per)
df_combined = pd.concat([hel_df, per_df])
print(df_combined)

exit()

# Create the plot
fig = px.line(df_combined, x='minutes', y='goals', color='team',
              line_group='team', labels={'goals': 'Goals', 'minutes': 'Minutes'},
              title='Goals Over Time')

# save to file: fig.write_html("goals_chart.html")

# Optionally, display the plot
fig.show()
