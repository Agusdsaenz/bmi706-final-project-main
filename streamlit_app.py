import altair as alt
import pandas as pd


df = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-Hospital.csv')


selected_states = ['MA', 'NY']
selected_hospitals = ['BOSTON MEDICAL CENTER', 'MASSACHUSETTS GENERAL HOSPITAL', 'CAMBRIDGE HEALTH ALLIANCE']


colors = ['purple', 'green', 'blue']
hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}

def apply_color(row):
    return hospital_to_color.get(row['Facility Name'], 'grey')

df['Color'] = df.apply(apply_color, axis=1)



df_filtered = df[df['State'].isin(selected_states)].copy()
df_filtered['Score'] = pd.to_numeric(df_filtered['Score'], errors='coerce')
df_sorted = df_filtered.groupby('State').apply(lambda x: x.sort_values(by='Score', ascending=False)).reset_index(drop=True)

base = alt.Chart(df_sorted).encode(
    y=alt.Y('Score:Q', axis=alt.Axis(title='Medicare Spending per Beneficiary'), scale=alt.Scale(domain=[0.6, 1.4])),
    x=alt.X('Facility Name:N', axis=alt.Axis(title='Hospitals', labels=False), sort='-y'),  
    tooltip=['Facility Name', 'Score']
).properties(
    width=450
)

dots = base.mark_circle(size=50).encode(
    color=alt.Color('Color:N', legend=None),
    opacity=alt.value(1),
    order=alt.Order('Score:Q', sort='descending')
)

final_chart = dots.facet(
    column=alt.Column('State:N', header=alt.Header(labelOrient='bottom', titleOrient='bottom')),
    spacing=55
).configure_axis(
    labelFontSize=12,  
    titleFontSize=14
)

final_chart

complications_deaths_df = pd.read_csv('Complications_and_Deaths-Hospital.csv')
payment_value_care_df = pd.read_csv('Payment_and_Value_of_Care-Hospital.csv')
filtered_measures = [
    "Rate of complications for hip/knee replacement patients",
    "Death rate for heart attack patients",
    "Death rate for heart failure patients",
    "Death rate for pneumonia patients"
]
complications_deaths_filtered_df = complications_deaths_df[
    complications_deaths_df['Measure Name'].isin(filtered_measures)
]


measure_name_mapping = {
    "Rate of complications for hip/knee replacement patients": "Payment for hip/knee replacement patients",
    "Death rate for heart attack patients": "Payment for heart attack patients",
    "Death rate for heart failure patients": "Payment for heart failure patients",
    "Death rate for pneumonia patients": "Payment for pneumonia patients"
}
complications_deaths_filtered_df['Payment Measure Name'] = complications_deaths_filtered_df['Measure Name'].map(measure_name_mapping)


complications_deaths_filtered_df['Facility ID'] = complications_deaths_filtered_df['Facility ID'].astype(str)
payment_value_care_df['Facility ID'] = payment_value_care_df['Facility ID'].astype(str)

complications_deaths_filtered_df.dropna(subset=['Facility Name'], inplace=True)
payment_value_care_df.dropna(subset=['Facility Name'], inplace=True)

complications_deaths_filtered_df['Facility Name'] = complications_deaths_filtered_df['Facility Name'].str.strip()
payment_value_care_df['Facility Name'] = payment_value_care_df['Facility Name'].str.strip()


merged_df = complications_deaths_filtered_df.merge(
    payment_value_care_df,
    how='inner',
    left_on=['Facility ID', 'Payment Measure Name'],
    right_on=['Facility ID', 'Payment Measure Name']
)
print (complications_deaths_filtered_df.head())

merged_df.drop(['State_y'], axis=1, inplace=True)
merged_df.rename(columns={'State_x': 'State'}, inplace=True)

merged_df.drop(['Facility Name_y'], axis=1, inplace=True)
merged_df.rename(columns={'Facility Name_x': 'Facility Name'}, inplace=True)


print(merged_df.head())
merged_df.to_csv('merged_df_corrected.csv', index=False)

filtered_df2 = merged_df[merged_df['State'].isin(selected_states)]

filtered_df2 = filtered_df2.dropna(subset=['Score', 'Payment'])

filtered_df2['Payment'] = pd.to_numeric(filtered_df2['Payment'].str.replace('[\$,]', '', regex=True), errors='coerce')


filtered_df2['Score'] = pd.to_numeric(filtered_df2['Score'], errors='coerce')

print (filtered_df2.head())

simplified_plot = alt.Chart(filtered_df2).mark_point(filled=True, size=60).encode(
    x=alt.X('Score:Q', axis=alt.Axis(title='Score')),
    y=alt.Y('Payment:Q', axis=alt.Axis(title='Payment ($)')),
    tooltip=['Facility Name:N', 'Score:Q', 'Payment:Q']
).properties(
    title='Simplified Debug Plot',
    width=600,
    height=400
)

simplified_plot

row_count = len(filtered_df2)

score_range = (filtered_df2['Score'].min(), filtered_df2['Score'].max()) if row_count > 0 else "Dataframe is empty"
payment_range = (filtered_df2['Payment'].min(), filtered_df2['Payment'].max()) if row_count > 0 else "Dataframe is empty"

print (score_range)
print (payment_range)

colors = ['red', 'green', 'blue'] 
hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}
filtered_df2['Color'] = filtered_df2['Facility Name'].map(hospital_to_color).fillna('lightgrey')

filtered_df2.to_csv('filtered.csv', index=False)

scatter_plots = []
for state in selected_states:
    for measure in filtered_measures:
        df_state_measure = filtered_df2[
            (filtered_df2['State'] == state) & 
            (filtered_df2['Measure Name'] == measure)
        ]
        
        scatter_plot = alt.Chart(df_state_measure).mark_point(filled=True, size=60).encode(
            x=alt.X('Score:Q', axis=alt.Axis(title='Score')),
            y=alt.Y('Payment:Q', axis=alt.Axis(title='Payment ($)')),
            color=alt.Color('Color:N', legend=None),
            tooltip=['Facility Name:N', 'Score:Q', 'Payment:Q']
        ).properties(
            title=f'{state} - {measure}',
            width=180,
            height=180
        )
        
        scatter_plots.append(scatter_plot)


grid_chart = alt.vconcat(*[
    alt.hconcat(*scatter_plots[i:i + len(filtered_measures)]) for i in range(0, len(scatter_plots), len(filtered_measures))
])


grid_chart