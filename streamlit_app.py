import altair as alt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


state_spending = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-State.csv')
hospital_spending = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-Hospital.csv')
complications_deaths_df = pd.read_csv('Complications_and_Deaths-Hospital.csv')
payment_value_care_df = pd.read_csv('Payment_and_Value_of_Care-Hospital.csv')



# Sidebar Selections
# Aggregate unique states and hospitals for selection
all_states = sorted(pd.concat([state_spending['State'], hospital_spending['State']]).unique())

# Initially, select up to 2 States
selected_states = st.sidebar.multiselect('Select up to 2 States', all_states, default=['MA', 'NY'])
if len(selected_states) > 2:
    st.sidebar.warning('Please select no more than 2 states.')

# Dynamically filter hospitals based on selected states
filtered_hospitals_df = pd.concat([hospital_spending, complications_deaths_df, payment_value_care_df])
filtered_hospitals = sorted(filtered_hospitals_df[filtered_hospitals_df['State'].isin(selected_states)]['Facility Name'].unique())

# Select up to 4 Hospitals from the filtered list
selected_hospitals = st.sidebar.multiselect('Select up to 3 Hospitals', filtered_hospitals, default=filtered_hospitals[:min(3, len(filtered_hospitals))])
if len(selected_hospitals) > 3:
    st.sidebar.warning('Please select no more than 3 hospitals.')

# Filter data based on selections
state_spending_filtered = state_spending[state_spending['State'].isin(selected_states)]
hospital_spending_filtered = hospital_spending[hospital_spending['State'].isin(selected_states) & hospital_spending['Facility Name'].isin(selected_hospitals)]


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
    orientation='h',
    marker=dict(
        color=state_spending_sorted['Score'],  # Assign a color based on the 'Score' value
        colorscale='Blues',
        line=dict(color='rgba(173, 216, 230, 1.0)', width=6)
    )
))

fig_bar.update_layout(
    xaxis_title='Score',
    yaxis_title='State',
    width=1000,
    height=600,  
    margin=dict(l=50, r=50, t=50, b=50),  
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
    geo_scope='usa',  
    width=1200,
    height=800
)

#Task 2 

df = pd.read_csv('Medicare_Hospital_Spending_Per_Patient-Hospital.csv')

selected_states = ['MA', 'NY']
selected_hospitals = ['BOSTON MEDICAL CENTER', 'MASSACHUSETTS GENERAL HOSPITAL', 'CAMBRIDGE HEALTH ALLIANCE']


colors = ['blue', 'orange', 'yellow']
light_gray_scale = alt.Scale(domain=['blue', 'orange', 'yellow', '#D3D3D3'], range=['blue', 'orange', 'yellow', '#D3D3D3'])

hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}
df['IsSelected'] = df['Facility Name'].apply(lambda x: x in selected_hospitals)


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
    width=450
)


dots = base.mark_circle().encode(
    color=alt.Color('Color:N', scale=light_gray_scale, legend=None),
    opacity=alt.value(1),
    order=alt.Order('Score:Q', sort='descending'),
    size=alt.condition(
        alt.datum.IsSelected,  
        alt.value(150),        
        alt.value(50)          
    )
)

median_line = alt.Chart(df_sorted).mark_rule(color='red', size=2).encode(
    y='median(Score):Q'
)



final_chart = alt.layer(dots, median_line ).facet(
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


colors = ['blue', 'orange', 'yellow'] 
hospital_to_color = {hospital: color for hospital, color in zip(selected_hospitals, colors)}
hospital_colors = alt.Scale(domain=['blue', 'orange', 'yellow', 'lightgrey'], range=['blue', 'orange', 'yellow', 'lightgray'])
filtered_df2['Color'] = filtered_df2['Facility Name'].map(hospital_to_color).fillna('lightgrey')

filtered_df2.to_csv('filtered.csv', index=False)


selected_hospital_sizes = {hospital: 150 for hospital in selected_hospitals}  
filtered_df2['DotSize'] = filtered_df2['Facility Name'].map(selected_hospital_sizes).fillna(50)  

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
            size=alt.Size('DotSize:Q', legend=None),
            opacity=alt.value(0.4),
            tooltip=['Facility Name:N', 'Score:Q', 'Payment:Q']
        ).properties(
            title=f"{state} - {measure_titles[measure]}",
            width=170,
            height=180  
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


avg_payment_score = filtered_df2.groupby('Facility Name').agg({
    'Payment': 'mean',
    'Score': 'mean'
}).reset_index()


avg_payment_score = avg_payment_score[avg_payment_score['Facility Name'].isin(selected_hospitals)]


avg_payment_score['Index'] = avg_payment_score['Facility Name'].apply(lambda x: selected_hospitals.index(x))


hospital_colors = alt.Scale(domain=selected_hospitals, range=colors)


bar_chart_payment = alt.Chart(avg_payment_score).mark_bar(size=30).encode(
    x=alt.X('Index:O', axis=alt.Axis(labels=False, title=None), sort=selected_hospitals),  
    y=alt.Y('Payment:Q', title='Average Payment ($)'),
    color=alt.Color('Facility Name:N', scale=hospital_colors, legend=alt.Legend(title="Hospital")), 
    tooltip=['Facility Name:N', 'Payment:Q']
).properties(
    title='Average Payments for MI+HF+Pneumonia+Hip/Knee',
    width=250,
    height=250
)


bar_chart_score = alt.Chart(avg_payment_score).mark_bar(size=30).encode(
    x=alt.X('Index:O', axis=alt.Axis(labels=False, title=None), sort=selected_hospitals), 
    y=alt.Y('Score:Q', title='Average Risk Score'),
    color=alt.Color('Facility Name:N', scale=hospital_colors, legend=alt.Legend(title="Hospital")),  
    tooltip=['Facility Name:N', 'Score:Q']
).properties(
    title='Average Risk Score MI+HF+Pneumonia+Hip/Knee',
    width=250,
    height=250
)


bar_charts = alt.hconcat(
    bar_chart_payment, bar_chart_score, spacing=50
).resolve_scale(
    color='independent'
)

# Combine all the charts into one Streamlit app

st.title("Medicare Beneficiary Spending Analysis")

# Make the map and bar chart have the same height
desired_height = 500
fig.update_layout(height=desired_height, width= 700)
fig_bar.update_layout(height=desired_height)

st.header("Medicare Spending Score per State")

col1, col2 = st.columns([2.5,1]) 

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.plotly_chart(fig_bar, use_container_width=True)

st.header("Medicare Spending per Beneficiary by Hospital and State")
st.altair_chart(final_chart, use_container_width=True)

st.header ('Payment versus complication for Pneumonia, Heart Attack, Heart Failure and Hip/Knee replacement')
st.altair_chart(grid_chart, use_container_width=True)

st.header ('Complications vs Payments')
st.altair_chart(bar_charts,use_container_width=True )

