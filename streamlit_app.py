import altair as alt
import pandas as pd


df = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-Hospital.csv')


selected_states = ['MA', 'NY']
selected_hospitals = ['BOSTON MEDICAL CENTER', 'MASSACHUSETTS GENERAL HOSPITAL', 'CAMBRIDGE HEALTH ALLIANCE']

colors = ['red', 'green', 'blue']
hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}


def apply_color(row):
    return hospital_to_color.get(row['Facility Name'], 'black')

df['Color'] = df.apply(apply_color, axis=1)


df_filtered = df[df['State'].isin(selected_states)]

df_filtered['Score'] = pd.to_numeric(df_filtered['Score'], errors='coerce')

df_filtered = df_filtered.dropna(subset=['Score'])



medians = df_filtered.groupby(['State', 'Facility Name'])['Score'].median().reset_index(name='Median_Score')
q1 = df_filtered.groupby(['State', 'Facility Name'])['Score'].quantile(0.25).reset_index(name='Q1_Score')
q3 = df_filtered.groupby(['State', 'Facility Name'])['Score'].quantile(0.75).reset_index(name='Q3_Score')


df_filtered = df_filtered.merge(medians, on=['State', 'Facility Name'], how='left')
df_filtered = df_filtered.merge(q1, on=['State', 'Facility Name'], how='left')
df_filtered = df_filtered.merge(q3, on=['State', 'Facility Name'], how='left')


base = alt.Chart(df_filtered).encode(
    x=alt.X('Facility Name:N', axis=alt.Axis(title='Hospitals')),
    y=alt.Y('Score:Q', axis=alt.Axis(title='Score')),
    color='Color:N',
    tooltip=['Facility Name', 'Score']
).properties(width=400)

points = base.mark_circle(size=50).encode(
    opacity=alt.value(1)
)

median_line = base.mark_rule(color='gold', size=2).encode(
    y='Median_Score:Q'
)

q1_line = base.mark_rule(color='purple', size=2).encode(
    y='Q1_Score:Q'
)

q3_line = base.mark_rule(color='turquoise', size=2).encode(
    y='Q3_Score:Q'
)


final_chart = points + median_line + q1_line + q3_line


final_chart = final_chart.facet(
    column='State:N'
).configure_facet(spacing=10)

final_chart