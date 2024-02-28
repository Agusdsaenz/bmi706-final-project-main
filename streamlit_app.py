import altair as alt
import pandas as pd
import plotly.graph_objects as go
import plotly.graph_objects as go
import streamlit as st

### Task 1 : Medicare beneficiary spending per state and hospital 

# Upload data
state_spending = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-State.csv')

# Exclude rows where Score is 'Not Available'
state_spending = state_spending[state_spending['Score'] != 'Not Available']

# Convert the Score column to numeric values
state_spending['Score'] = pd.to_numeric(state_spending['Score'])
# Exclude rows where Score is 'Not Available'
state_spending = state_spending[state_spending['Score'] != 'Not Available']

# Convert the Score column to numeric values
state_spending['Score'] = pd.to_numeric(state_spending['Score'])

# Sort by Score
state_spending_sorted = state_spending.sort_values('Score', ascending=False)

# Choropleth map
fig = go.Figure(data=go.Choropleth(
    locations=state_spending['State'],  # State abbreviations
    z=state_spending['Score'],  # Data values
    locationmode='USA-states',
    colorscale='Blues',
    colorbar=dict(
        title='Spending Score',  # Title for the colorbar
        x=1,  # Position of the colorbar (1 is the default, which is the right side)
        len=0.75,  # Length of the colorbar (as a fraction of the plot height)
        thickness=20,  # Thickness of the colorbar
    )
))

fig.update_layout(
    title_text='Medicare Spending Score per Beneficiary',
    geo_scope='usa',  # limit map scope to USA
    width=1200,
    height=800
)

# Bar chart

fig_bar = go.Figure(go.Bar(
    x=state_spending_sorted['Score'],  # Data values
    y=state_spending_sorted['State'],  # State abbreviations
    orientation='h',  # Horizontal bar chart
    marker=dict(color='rgba(58, 71, 80, 0.6)', line=dict(color='rgba(58, 71, 80, 1.0)', width=3))
))

fig_bar.update_layout(
    title_text='Medicare Spending Score per State',
    xaxis_title='Spending Score',
    yaxis_title='State',
    width=400,
    height=600,  # Adjust the height based on the number of states to ensure readability
    margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins to fit state names if necessary
)

fig = go.Figure(data=go.Choropleth(
    locations=state_spending['State'],  # State abbreviations
    z=state_spending['Score'],  # Data values
    locationmode='USA-states',
    colorscale='Blues',
    colorbar=dict(
        title='Spending Score',  
        x=1,  
        len=0.25,  
        thickness=10,  
    )
))

fig.update_layout(
    title_text='Medicare Spending Score per Beneficiary',
    geo_scope='usa',  
    width=1200,
    height=800
)


df = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-Hospital.csv')

selected_states = ['MA', 'NY']
selected_hospitals = ['BOSTON MEDICAL CENTER', 'MASSACHUSETTS GENERAL HOSPITAL', 'CAMBRIDGE HEALTH ALLIANCE']


colors = ['purple', 'green', 'blue']
light_gray_scale = alt.Scale(domain=['purple', 'green', 'blue', '#D3D3D3'], range=['purple', 'green', 'blue', '#D3D3D3'])

hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}

def apply_color(row):
    if row['Facility Name'] in hospital_to_color: 
        return hospital_to_color[row['Facility Name']]  
    else:
        return "#D3D3D3" 

df['Color'] = df.apply(apply_color, axis=1)


df_filtered = df[df['State'].isin(selected_states)].copy()
df_filtered['Score'] = pd.to_numeric(df_filtered['Score'], errors='coerce')
df_sorted = df_filtered.groupby('State').apply(lambda x: x.sort_values(by='Score', ascending=False)).reset_index(drop=True)

base = alt.Chart(df_sorted).encode(
    y=alt.Y('Score:Q', axis=alt.Axis(title='Medicare Spending per Beneficiary'), scale=alt.Scale(domain=[0.6, 1.4])),
    x=alt.X('Facility Name:N', axis=alt.Axis(title='Hospitals', labels=False), sort='-y'),  
    tooltip=['Facility Name', 'Score']
).properties(
    width=550
)


dots = base.mark_circle().encode(
    color=alt.Color('Color:N', scale=light_gray_scale, legend=None),
    opacity=alt.value(1),
    order=alt.Order('Score:Q', sort='descending')
)

final_chart = dots.facet(
    column=alt.Column('State:N', header=alt.Header(labelOrient='bottom', titleOrient='bottom')),
    spacing=40
).configure_axis(
    labelFontSize=12,  
    titleFontSize=14
)

### Task 3 - Payment per disease associated with complication rate 

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



merged_df.to_csv('merged_df_corrected.csv', index=False)

filtered_df2 = merged_df[merged_df['State'].isin(selected_states)]

filtered_df2 = filtered_df2.dropna(subset=['Score', 'Payment'])

filtered_df2['Payment'] = pd.to_numeric(filtered_df2['Payment'].str.replace('[\$,]', '', regex=True), errors='coerce')


filtered_df2['Score'] = pd.to_numeric(filtered_df2['Score'], errors='coerce')


colors = ['red', 'green', 'blue'] 
hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}
hospital_colors = alt.Scale(domain=['red', 'green', 'blue', 'lightgrey'], range=['red', 'green', 'blue', 'lightgray'])
filtered_df2['Color'] = filtered_df2['Facility Name'].map(hospital_to_color).fillna('lightgrey')

filtered_df2.to_csv('filtered.csv', index=False)



scatter_plots = []
measure_titles = {
    "Rate of complications for hip/knee replacement patients": "Hip/Knee Replacement",
    "Death rate for heart attack patients": "Heart Attack",
    "Death rate for heart failure patients": "Heart Failure", 
    "Death rate for pneumonia patients": "Pneumonia"
}


for state in selected_states:
    for measure in filtered_measures:
        df_state_measure = filtered_df2[
            (filtered_df2['State'] == state) & 
            (filtered_df2['Measure Name'] == measure)
        ]
        
        
        max_payment = df_state_measure['Payment'].max()
        y_scale = alt.Scale(domain=(0, max_payment * 1.2))  
        
        scatter_plot = alt.Chart(df_state_measure).mark_point(filled=True, size=60).encode(
            x=alt.X('Score:Q', axis=alt.Axis(title='Complications')),
            y=alt.Y('Payment:Q', axis=alt.Axis(title='Payment ($)'), scale=y_scale),
            color=alt.Color('Color:N', scale=hospital_colors, legend=None),
            tooltip=['Facility Name:N', 'Score:Q', 'Payment:Q']
        ).properties(
            title=f"{state} - {measure_titles[measure]}",
            width=200,
            height=200  
        )
        
        scatter_plots.append(scatter_plot)


h_spacing = 50 
v_spacing = 100 

grid_chart = alt.vconcat(
    *[
        alt.hconcat(
            *scatter_plots[i:i + len(filtered_measures)], 
            spacing=h_spacing
        ) 
        for i in range(0, len(scatter_plots), len(filtered_measures))
    ],
    spacing=v_spacing
)

# Combine all the charts into one Streamlit app

st.title("Medicare Beneficiary Spending Analysis")

col1, col2 = st.columns([3, 2])  # Adjust the ratio as needed for your charts

with col1:
    st.header("Medicare Spending Score per Beneficiary (USA)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.header("Medicare Spending Score per State")
    st.plotly_chart(fig_bar, use_container_width=True)

st.header("Medicare Spending per Beneficiary by Hospital and State")
st.altair_chart(final_chart, use_container_width=True)

st.altair_chart(grid_chart)