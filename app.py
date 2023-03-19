# The import statements:
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import os.path
from streamlit_lottie import st_lottie
import requests
import plotly.express as px


# Set page title:
st.set_page_config( page_title='Environmental Impact of Food Production'
                  , page_icon=':ear_of_corn:'
                  #, layout='wide'
                  )

# Load data:
@st.cache()
def load_data(path):
    data = pd.read_csv(path)
    return data

water_use = load_data('data/water_use.csv')
production = load_data('data/productions.csv')
ems_origin = load_data('data/emissions_with_origin.csv')
ems_global = load_data('data/Global_emissions.csv')

# Load food chain image:
supply_chain = Image.open(os.path.join('assets', 'supply_chain.png'))

# Load Lottie File:
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_food = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_p1bmwqtk.json")

# st_lottie(lottie_food, height = 350, key = 'food')

# Define KPI(s):
#land_use=int(ems_origin['Land use'].sum())
#animal_feed=round(ems_origin['Animal feed'].mean(),1)
#farm=':star:' * int(round(average_rating,0))
#processing=round(emf_origin['Total'].mean(),2)
#transport=
#packaging=
#retail=



#------------------------------------------------------------------ SIDEBAR ------------------------------------------------------------
st.sidebar.markdown("## How food we produce is affecting our planet's health? 🌱🌍")

st.sidebar.write(""" What are the food products with the biggest environmental inpact? Choose the product's origin to find out. """)

origin=st.sidebar.multiselect("Product's Origin:"
                             , options=production['Origin'].unique()
                             , default=production['Origin'].unique()
                             )

st.sidebar.image(supply_chain, use_column_width=True)

#----------------------------------------------------------------- DASHBOARD -----------------------------------------------------------
# Page title:
st.title('Environmental Impact of Food Production')
st.markdown('##')

st.write(""" Here, you can investigate which are the products whose production emits more greenhouse gases and
associate their environmental impact with each supply chain step, their worldwide productions and the water use.""")

st.markdown(' #### Top 10 Emitters')
st.markdown('Chart below selects ten products that produce the most emissions (kg CO2 per kg of product). '
            'Those are divided according to your product origin selection: animal, vegetal-based or both. ')

# Emissions barchart:
top10 = ems_origin.query("Origin==@origin").sort_values("Total_emissions")[-10:]

# Emissions barchart
top10 = ems_origin.query("Origin==@origin").sort_values("Total_emissions")[-10:]

fig_bar_emissions = px.bar(top10
                          , y='Food product'
                          , x='Total_emissions'
                           )
fig_bar_emissions.update_layout(height=450,plot_bgcolor="rgba(0,0,0,0)")
fig_bar_emissions.update_traces(marker_color=['#F59B70' if x == 'Animal' else '#2B9237' for x in top10.Origin],showlegend=False)
st.plotly_chart(fig_bar_emissions)

st.markdown("Comparing top animal and vegetal-based emmiter: Beef produces more than 3 times more emissions than dark chocolate!")

st.markdown(" #### Environmental Impact & Production Map")
st.markdown('Select product to find out impact from farm to fork. Emissions are measured as kg of CO2 per kg of product.')

# Dropdown menu product_options:
options = ems_origin.query("Origin==@origin")['Food product'].unique()
product_options = st.selectbox('Select product:', options)

#-----------------------------------------KPI's SPACE----------------------------------------



#-----------------------------------------KPI's SPACE----------------------------------------

st.markdown('Map provides an overview of worldwide production of selected food product in tonnes.')

# Year slider:
# min_year = production['Year'].min()
# max_year = production['Year'].max()
year = st.slider('Select Year:', min_value=2009, max_value=2019, step=1)

# World map:
df = production.query("Item==@product_options & Year==@year")

fig_map = px.choropleth(df, locations="Area", locationmode='country names',
                        color='Value', hover_name="Value"
                        , color_continuous_scale='Peach'
                        )
# fig_map.update_layout(geo_scope = 'europe')
st.plotly_chart(fig_map)


st.markdown('#### Emissions Ratio')
st.markdown('Global greenhouse gas emissions from food production, in percentage. '
            'Food production is responsible for 26% of global emissions.')

# Emissions sunburst:
fig_emissions = px.sunburst(ems_global
, path = ['Emissions', 'Group','Subgroup']
, values = 'Percentage of food emissions'
, color = 'Group'
, color_discrete_sequence = px.colors.sequential.Peach_r
).update_traces(hovertemplate = '%{label}<br>' + 'Global Emissions: %{value}%', textinfo = "label + percent entry")
st.plotly_chart(fig_emissions)

st.markdown('#### Water-use')
st.markdown('Freshwater withdrawals per kg of product, in liters')

# Water-use sunburst:
df_water = water_use.query("Origin==@origin")

fig = px.sunburst(df_water
, path=['Origin', 'Category', 'Product']
, values='Water Used'
, color='Category'
, color_discrete_sequence = px.colors.sequential.Teal_r
).update_traces(hovertemplate = '%{label}<br>' + 'Water Used: %{value} L')
st.plotly_chart(fig)
