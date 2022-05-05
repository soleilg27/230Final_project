"""
Name: Soleil Gookin
CS230: Section 1
Data: Boston Crime Data: Link to your web application online

Description: This program analyzes data from the BostonCrime dataset. It includes customization options for different districts and variables of the data. This will run
as a webpage on streamlit and will show several maps and graphs of the data. This code primarily manipulates the days of the week and districts, as well as the hour that offenses are committed.
"""
#import necessary python packages
import matplotlib.dates
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import dateutil
from PIL import Image
import pydeck as pdk

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#use read_csv function to read
df = pd.read_csv(r"C:\Users\sk-go\OneDrive - Bentley University\Spring ‘22\CS 230\Python Projects\BostonCrimeData.csv")
bos_dist = pd.read_csv(r"C:\Users\sk-go\OneDrive - Bentley University\Spring ‘22\CS 230\Python Projects\BostonDistricts.csv")

#fix data to exclude missing values and non-applicable values
#there is data in the dataset that has empty cells and this ensures that they are excluded
df = df[df["DISTRICT"] != 'External']
df = df[df["DISTRICT"].notnull()]

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_map_layers_by_district(data, dist_colors_dict):
    #from the data passed in get a list of districts to show
    #.unique() takes dataframe and gets unique list of values from the district column
    districts_to_show = data.DISTRICT.unique()
    layers = []
    #for loop iterates through list created with .unique()
    for dist in districts_to_show:
        #df that inludes only what's in the district
        layerData = data[data["DISTRICT"] == dist]
        #layers adds the points for the district with the distinct color code dictionary in generate map function
        st.write(layerData)
        layers.append(pdk.Layer("ScatterplotLayer", data=layerData, get_position='[Long,Lat]', get_radius = 40, get_color = dist_colors_dict[dist]))
    #returns specific layers based on input of district
    return layers

#generates main map for boston
#dataframe parameter to customize
def generate_map(data):
    #dictionary of codes and corresponding colors
    district_colors = {
        'C11':[235, 61, 52],
        'E5':[235, 98, 52],
        'B2':[235, 98, 52],
        'D4':[235, 98, 52],
        'C6':[52, 235, 52],
        'A1':[52, 153, 235],
        'B3':[52, 61, 235],
        'E18':[134, 52, 235],
        'A7':[226, 52, 235],
        'D14':[144, 242, 124],
        'E13':[250, 214, 147],
        'A15':[23, 97, 8],
    }
    #filters to get applicable columns
    map_df = data.filter(["DISTRICT", "Lat","Long"])
    st.write(map_df)
    #view_state = pdk.ViewState(latitude=map_df["Lat"].mean(), longitude=map_df["Long"].mean(), zoom = 7)
    #view_state is what tells streamlit how to set up the map
    #set location for middle of Boston roughly
    view_state = pdk.ViewState(latitude= 42.340915, longitude= -71.062989, zoom = 10)
    #layer  defines how the points will show up on the map
    #layer = pdk.Layer("ScatterplotLayer", data=map_df, get_position='[Long,Lat]', get_radius = 40, get_color = [165, 200, 245])

    #call get_map_layers_by_district function with the specific filtered df for district and use the corresponding colors for the points
    layers = get_map_layers_by_district(map_df, district_colors)
    tool_tip = {"html": 'Listing:<br><b>{name}</b>', 'style': {'backgroundColor': 'blue', 'color': 'white'}}
    map = pdk.Deck(map_style = 'mapbox://styles/mapbox/dark-v9', initial_view_state=view_state,
                   layers = layers, tooltip=tool_tip)
    #pydeck is used to display the map
    st.pydeck_chart(map)

#this function allows the user to pick the day of the week they want to specify
#preset parameter with whole df as default parameter
def pick_data(week_day, data = df):
    #create dataframe that includes only offenses for the day of the week
    data_day_filt = data.loc[data["DAY_OF_WEEK"] == week_day]
    #returns dataframe
    return data_day_filt

#function to graph the top offenses -NEEDS TO BE CUSTOMIZED
def top_offenses(data, number_to_show = 10):
    #Group the rows by offense description and count occurrence
    df_grouped = data.groupby(["OFFENSE_DESCRIPTION"]).count()
    #Now only grab the offense code column counts and reset the index to OFFENSE_CODE so the sort will work on that
    # Then sort them decending and grap the parameter
    df_sorted = df_grouped['OFFENSE_CODE'].reset_index(name='OFFENSE_CODE').sort_values(['OFFENSE_CODE'],ascending = False).head(number_to_show)

    #correct colun name to frequency
    df_bar_data = df_sorted.rename(columns={'OFFENSE_CODE': 'frequency'})

    #rotate changes angle labels are displayed at
    df_bar_data.plot.bar(x="OFFENSE_DESCRIPTION", y="frequency", rot=65, color='lavender');
    st.header(f'Top {number_to_show} Offenses')
    plt.xlabel('Offense Description')
    plt.ylabel('Frequency')

    #output to streamlit page
    st.pyplot(plt)

    #show raw data
    st.subheader(f"Raw Data for the Top {number_to_show} offenses:")
    st.write(df_bar_data)

#function that allows user to pick which function and returns what they chose
#default parameter of the first district
def pick_district(pick = "Downtown"):
    #include only offenses for the district that the user picked
    indiv_key = bos_dist[bos_dist["DISTRICT_NAME"] == pick]

    #.iloc uses indexing to make new dataframe of specific districts ---------------------------------------------------------
    dist_df = df[df["DISTRICT"] == indiv_key["DISTRICT_NUMBER"].iloc[0]]

    #return district dataframe with offenses only in a certain district
    return dist_df

#takes day of week and dataset and returns datframe
#defualt parameter of df
def df_day(day, data = df):
    day_df = data[data["DAY_OF_WEEK"] == day]
    return day_df

#this function will generate the hours that crimes occur for a specific district
def hour_dst(spec_df):
    #makes lists for the hours of each offense
    hours = [row["HOUR"] for ind, row in spec_df.iterrows()]

    #creates lis with all of the correspinding codes for each offense
    dist_codes = [row["DISTRICT"] for ind, row in spec_df.iterrows()]

    #make dictionary that will have district_code as key and corresponding hour avg as value
    hour_avg = {}

    #make values for dictionary
    for dist in dist_codes:
        hour_avg[dist] = []

    #loop goes through the hour_avg dictionary and adds the averaged hour of offenses
    for i in range(len(hours)):
        hour_avg[dist_codes[i]].append(hours[i])

    #returns dictionary with codes as keys and districts as values
    #will be turned into dictionary with averages in avg_hour_dist
    return hour_avg

#function that takes the average hour dictionary from hour_dst()
def avg_hour_dist(hour_avg):

    #creates dictionary to have the average hours for each district in
    avg_dict = {}

    #goes through the keys of hour_avg and adds averages of the hours to the values
    #keys are the codes and values are the average
    for key in hour_avg:
        avg_dict[key] = np.mean(hour_avg[key])

    #interate through the boston district data and create a dictionary
    #keys are codes and values are district names
    dist_code_nam = {}
    for row in bos_dist.itertuples():
        dist_code_nam[row[1]] = row[2]

    #assign dist all the keys
    dist = avg_dict.keys()
    dist_names = []

    #for loop appends district names in dist to list dist_names to use for bar chart
    for item in dist:
        dist_names.append(dist_code_nam[item])

    #creating list of average hour to use for bar chart
    avg = avg_dict.values()

    fig = plt.figure(figsize = (10, 5))
    # creating the bar plot
    plt.bar(dist_names, avg, color = 'plum', width = 0.4)

    plt.xlabel("Districts", fontsize = 30)
    plt.ylabel("Average Hour of Offenses", fontsize = 30)
    st.header("Bar Chart of The District Average Hour Offenses Are Committed\n")
    plt.xticks(rotation= '75', fontsize = 25)
    plt.yticks(fontsize = 25)
    st.pyplot(plt)

#function to display information on the raw data
def raw_data_display(data):
    st.dataframe(data)

#function takes in a dataframe and returns a pie chart
#similar logic to top_offenses
#default parameter of 5
def make_pie_data(data = df, top_number = 5):
    #Group the rows by offense_description and count occurrence
    df_grouped = data.groupby(["OFFENSE_DESCRIPTION"]).count()
    #Now only grab the OFFENSE_CODE column counts and reset the index to offense_code so the sort will work on that. Then sort them decending and grap the parameter
    df_sorted = df_grouped['OFFENSE_CODE'].reset_index(name='OFFENSE_CODE').sort_values(['OFFENSE_CODE'],ascending = False).head(top_number)
    #st.dataframe(df_sorted)
    #Set the index back to offense_description so that the chart will know those are the x axis and rename OFFENSE_CODE to frequency so the chart will display as such
    df_bar_data = df_sorted.rename(columns={'OFFENSE_CODE': 'frequency'})
    #return value to be used for make_pie
    return df_bar_data
    st.dataframe(df_bar_data)

def make_pie(data):
    #pie chart with percent crimes on each day
    #goes through data frame and makes a list of all the variables in the column
    offense_column = data["OFFENSE_DESCRIPTION"].tolist()
    count_column = data["frequency"].tolist()

    #explodes highest percent out of the pie chart by generating 0 values for the rest
    explode = [.25]
    for i in range(len(offense_column)-1):
        explode.append(0)

    #set style to use for the pie chart
    plt.style.use('_mpl-gallery-nogrid')

    #specifies the colors for the different slices of the pie chart
    colors = plt.get_cmap('Blues')(np.linspace(0.1, 0.8, len(count_column)))
    fig, ax = plt.subplots()

    #autopct specifies fromatting for percentages
    ax.pie(count_column, explode= explode, labels= offense_column,autopct='%1.1f%%',
        shadow=True, startangle=90)
    ax.axis("equal")
    plt.show()
    #display plot to streamlit page
    st.pyplot(plt)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# main function to run program
def main():
    #create sidebar for web page with different choices for analysis
    sidebar_selection = st.sidebar.selectbox("What do you want to learn about?", ("Home", "Mapping", "Charts & Graphing", "Raw Data"))
    if sidebar_selection == "Home":
        #main page/homepage setup
        #st.markdown(f'<div style="color: #4AB0F5">Boston Crime Data 2022</div>',unsafe_allow_html=True)
        st.title("Crime Data Analysis of Boston")
        #import image for home page
        main_bos_image = Image.open('boston_purple_sea.jpg')
        st.image(main_bos_image, caption='Landscape Shot of Boston at Sunset', width = 550)
        #brief intro into the webpage
        st.text("\nThis webpage provides visual representations of Boston crime data analysis for 2022.")
        st.text("<-- For analysis and customization use the sidebar to the left.")
        #display raw data for all of boston
        st.subheader("Boston Crime Raw Data from 2022:\n")
        st.dataframe(df)
    #this code provides customizable maps using generate_map()
    elif sidebar_selection == "Mapping":
        #customize map to a specific district or all of boston
        mapping_sidebar_selection = st.sidebar.selectbox("Pick one:", ("All of Boston", "Individual Districts"))

        #if specific district provide option for filtering based on day of the week
        if mapping_sidebar_selection == "All of Boston":
            pick_day = st.sidebar.checkbox("Filter for Day of The Week")
            #if they didnt pick the check box calls genertae map with entire df
            if not pick_day:
                st.header("Map of Crime Across Greater Boston for 2022")
                #generate map for all of boston
                generate_map(df)
            #if pick day of week prompts for day of week with slider
            elif pick_day:
                #sider option to select what day of the week to map
                all_day_week_slider_mapping = st.sidebar.select_slider(
                        'Select a day of the week to learn more about crime that occurs on that day:',
                        options=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
                st.header(f"Map of Boston for Offenses Occurring on {all_day_week_slider_mapping}")
                #call generate map function using df_day function that returns the day dataframe
                #df_day takes day of week as a parameter
                generate_map(df_day(all_day_week_slider_mapping))
        #pick individual district with selectbox on the sidebar
        elif mapping_sidebar_selection == "Individual Districts":
            #slider allows user to pick the district
            district_pick_2 = st.sidebar.selectbox("What district would you like to learn more about?", bos_dist["DISTRICT_NAME"])

            #checkbox allows user to select if they want to specify a day
            indiv_dis_pick_day = st.sidebar.checkbox(f"Filter for Day of The Week For {district_pick_2}")

            #if dont want individual day, then just run generate map with pick_district which returns dataframe of specific district
            if not indiv_dis_pick_day:
                st.header(f"Map of Crime in {district_pick_2}")
                #pick_district takes in the district pick and returns dataframe of just those offenses
                generate_map(pick_district(district_pick_2))

            #if want to pick specific day:
            elif indiv_dis_pick_day:
                #slider allows user to pick the day of the week
                day_week_slider_mapping_dist = st.sidebar.select_slider(
                        'Select a day of the week to learn more about crime that occurs on that day:',
                        options=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
                st.header(f"Map of Boston for Offenses Occurring on {day_week_slider_mapping_dist}")
                #call generate map function using df_day function that returns the day dataframe
                #input dataframe based on day into generate map; takes two parameters: day of week and the dataframe to reference
                #data frame to reference generated by pick_district
                generate_map(df_day(day_week_slider_mapping_dist, pick_district(district_pick_2)))
    elif sidebar_selection == "Charts & Graphing":

        #checkboxes allows user to pick which visual they would like to see
        type_visual_pie = st.sidebar.checkbox("Top Offenses Pie Chart")
        type_visual_bar = st.sidebar.checkbox("Top Offenses Bar Chart")
        type_visual_bar_hour = st.sidebar.checkbox("Average Hour Per District Bar Chart")

        #code for top offenses bar chart
        if type_visual_bar:
            #for bar chart of top offenses can pick either all of boston or a specific district
            all_of_dist = st.sidebar.selectbox("", ("All of Boston", "District"))
            if all_of_dist == "All of Boston":
                top_num_pick = st.sidebar.select_slider('Select How Many of The Top Offenses You Would Like To See:',
                    options=[3,4,5,6,7,8,9,10])
                #run top offenses with slider pick of number using all of boston data (df)
                top_offenses(df, top_num_pick)
            elif all_of_dist == "District":
                top_num_pick_dist = st.sidebar.select_slider('Select How Many of The Top Offenses You Would Like To See:',
                    options=[3,4,5,6,7,8,9,10])
                district_pick_raw_bar = st.sidebar.selectbox("What district would you like to learn more about?", bos_dist["DISTRICT_NAME"])
                #run top offenses with slider pick of number with specific district data using pick_district() which takes district as parameter
                top_offenses(pick_district(district_pick_raw_bar), top_num_pick_dist)

        #code for top offenses pie chart
        elif type_visual_pie:
                #for pie chart of top offenses can pick either all of boston or a specific district
                all_of_dist_pie = st.sidebar.selectbox(" ", ("All of Boston", "District"))
                if all_of_dist_pie == "All of Boston":
                    top_num_pick_pie_all = st.sidebar.select_slider('Select How Many of The Top Offenses You Would Like To See: ',
                        options=[5,6,7,8,9,10])
                    st.header(f"Pie Chart for The Top {top_num_pick_pie_all} Offenses in Boston")
                    #run make_pie with returned dataframe from make_pie_data
                    #inputs entire df because user selected all of boston
                    make_pie(make_pie_data(df, top_num_pick_pie_all))
                elif all_of_dist_pie == "District":

                    #selectbox allows user to pick the district and slider lets user pick number of top offenses
                    district_pick_raw_pie = st.sidebar.selectbox("What district would you like to learn more about?", bos_dist["DISTRICT_NAME"])
                    top_num_pick_pie = st.sidebar.select_slider('Select How Many of The Top Offenses You Would Like To See: ',
                        options=[5,6,7,8,9,10])
                    st.header(f"Pie Chart for The Top {top_num_pick_pie} Offenses in {district_pick_raw_pie}")
                    #must specify for make_pie_data that the datframe being used if the one of just that district
                    make_pie(make_pie_data(pick_district(district_pick_raw_pie), top_num_pick_pie))

        #code for the visual of the average hour crime occurs in each district
        elif type_visual_bar_hour:

                # #allow user to pick
                # all_of_dist_bar_hour = st.sidebar.selectbox(" ", ("All of Boston", "District"))
                # if all_of_dist_bar_hour == "All of Boston":
                #     avg_hour_dist(df)
                # elif all_of_dist_bar_hour == "District":
                #district_pick_raw_bar_hour = st.sidebar.selectbox("What district would you like to learn more about?", bos_dist["DISTRICT_NAME"])

                avg_hour_dist(hour_dst(df))
    #this portion of code allows user to look at the raw data
    elif sidebar_selection == "Raw Data":
        #checkboxes allow user to pick all of boston or a specific district
        raw_data_pick_all = st.sidebar.checkbox("All of Boston")
        raw_data_pick_dist = st.sidebar.checkbox("Specific District")
        #if they pick district, selectbox allows them to pick which district
        if raw_data_pick_dist:
            district_pick_raw = st.sidebar.selectbox("What district would you like to learn more about?", bos_dist["DISTRICT_NAME"])
            dist_cust = st.sidebar.selectbox(f"Customize Raw for {district_pick_raw}", ("All District Offenses", "Day of Week"))
            #can either do all data from that district or from a specific day of the week for that district
            if dist_cust == "All District Offenses":
                st.header(f"{district_pick_raw} Crime Data Table:")
                raw_data_display(pick_district(district_pick_raw))
            elif dist_cust == "Day of Week":
                day_week_slider = st.sidebar.select_slider(
                    'Select a day of the week to learn more about crime that occurs on that day :',
                    options=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
                st.header(f"{district_pick_raw} Crime Data Table for {day_week_slider}:")
                #several parameters because must get data for both the district and the day of the week for that district
                raw_data_display(pick_data(day_week_slider, pick_district(district_pick_raw)))
        elif raw_data_pick_all:
            all_bos_cust = st.sidebar.selectbox("Customize Raw Data for Boston", ("All Offenses", "Day of Week"))
            if all_bos_cust == "All Offenses":
                #allows user to pick from all offenses and runs raw_data_display to output it
                st.header("Greater Boston Crime Data Table:")
                raw_data_display(df)
            elif all_bos_cust == "Day of Week":
                #allows user to pick day of week for all of boston data with slider
                day_week_slider = st.sidebar.select_slider(
                'Select a day of the week to learn more about crime that occurs on that day:',
                options=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
                st.header(f"Greater Boston Crime  on {day_week_slider} Data Table:")
                raw_data_display(pick_data(day_week_slider, df))

#call main function
main()
