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



medians = df_filtered.groupby(['State', 'Facility Name'])['Score'].median().reset_index()
q1 = df_filtered.groupby(['State', 'Facility Name'])['Score'].quantile(0.25).reset_index()
q3 = df_filtered.groupby(['State', 'Facility Name'])['Score'].quantile(0.75).reset_index()


base = alt.Chart(df_filtered).encode(
    y=alt.Y('Score:Q', axis=alt.Axis(labels=False)),
    x=alt.X('Facility Name:N', axis=alt.Axis(title='Hospitals', labels=False)),  
    tooltip=['Facility Name', 'Score']
).properties(width=400)


box_plot = base.mark_boxplot().encode(
    color=alt.value('lightgray'),
    opacity=alt.value(0.5)
)

points = base.mark_circle(size=50).encode(
    color=alt.Color('Color:N', legend=None),
    opacity=alt.value(1)
)


combined_chart = box_plot + points


median_line = base.mark_rule(color='gold', size=2).encode(
    y='median(Score):Q'
)

q1_line = base.mark_rule(color='purple', size=2).encode(
    y='q1(Score):Q'
)

q3_line = base.mark_rule(color='turquoise', size=2).encode(
    y='q3(Score):Q'
)


final_chart = combined_chart + median_line + q1_line + q3_line


final_chart = final_chart.facet(
    column=alt.Column('State:N', header=alt.Header(labelOrient='bottom', titleOrient='bottom')),
    spacing=5
).configure_facet(columns=2)


final_chart
