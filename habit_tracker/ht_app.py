import streamlit as st
from crud import *
import plotly.express as px
import pandas as pd
from datetime import datetime
import time
import logic

#Setting the base of the app
Habit.reset_done()
st.set_page_config(page_title= "Habit Tracker", page_icon= "🌱", layout= "centered",)
st.markdown(f"<h1 style='text-align:center;'>Habit Tracker</h1>", unsafe_allow_html=True)

today = datetime.today().strftime('%d/%m/%Y')
tab1, tab2, tab3, tab4,tab5, tab6 = st.tabs(["Home", "Habits", "Category", "Analyse Habit", "Reward", "Suggest"])

with tab1:
    if "streak" not in st.session_state:
        st.session_state["streak"] = 0
    streak = None if st.session_state["streak"] == 0 else 1
    if "day_streak" not in st.session_state:
        st.session_state["daystreak"] = 0
    daystreak =st.session_state["daystreak"]
    daystreak = Stat.streak(daystreak)
    if "daystreak_delta" not in st.session_state:
        st.session_state["daystreak_delta"] = 0
    
    daystreak_delta = st.session_state["daystreak_delta"]
    habit_list = Habit.show_today_habit()
    habit_list_all = Habit.show_habit()
    random_number = np.random.randint(0,1000)
    st.markdown(f"<h5 style='font-size:18px; text-align:center;'>Today : {today}.</h5>", unsafe_allow_html=True)

    if not habit_list:
        st.info("You don't have habit for today")
    for name, habit_id, done in habit_list:
        done= False if done == 0 else True

        new_done = st.checkbox(name, value= done, key=f"habit_{habit_id}")
        if new_done != bool(done):
            if new_done:
                Habit.mark_done(habit_id)
                st.success("Done")
                time.sleep(0.7)
                st.rerun()
                

            else:
                Habit.unmark_done(habit_id)
                st.error("Undone")
                time.sleep(0.7)
                st.rerun()
            


    progress_bar = Stat.progress_bar()
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Habits", len(habit_list))
    col2.metric("Completed", f"{len(progress_bar)} / {len(habit_list)}",)
    col3.metric("Streak", f"{daystreak} day(s)",)
    col3.text(f"Best Streak : {Stat.longest_daystreak()} day(s)")
    if len(habit_list) > 0:
        st.progress(len(progress_bar) / len(habit_list))
    else:
        st.progress(0)
    with st.container(border = True):
        sentence_list = logic.app.word()
        st.markdown(f"<t2 style='text-align:center; bold = true'>{sentence_list}</t2>", unsafe_allow_html=True)
with tab2:
    st.title("Weekly Habit Agenda")
    df = Stat.habits_by_day()
    days = Days.show_days()
    day_index = st.slider("Select the day",min_value=1, max_value=7, value=1, label_visibility= "hidden", key= 18)
    selected_day = days[day_index-1]

    st.subheader(f"Habits for {selected_day}")
    df_filtre = df[df["Days"] == selected_day]
    if len(df_filtre) == 0:
        st.warning("No habit for this day")
    else:
        st.dataframe(df_filtre, width='stretch', hide_index = True)

    habit_list_all = Habit.show_habit()
    habit_name_list = habit_list_all['Habit'].tolist()
    habit_id = habit_list_all['HabitID']
    
    st.divider()
    habit_select = st.selectbox("Action", ["Add habit", "Modify habit", "Delete habit", "All habit"], placeholder ="Choose an option", index= None)
    st.divider()
    if habit_select == "Add habit":
        choice = st.selectbox("Action", ["Daily", "Weekly"] )
        if choice == "Daily":
            habit_name = st.text_input("Habit name:")
            if habit_name:
                habit_row = habit_list_all.loc[habit_list_all['Habit'] == habit_name]
                error = None
                if not habit_row.empty:  # DataFrame result is not empty
                    habit_row = habit_row.iloc[0]
                    error = st.error("This name is already taken, please try another name")
                else:
                    pass
            else :
                pass

            habit_desc = st.text_input("Describe your habit:")
            days =  ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            category_list = Category.show_category()
            categories = category_list['Name'].tolist() + ["Personnalized"]
            category = st.selectbox("Select Category:", categories)
            category_row = category_list.loc[category_list['Name'] == category].iloc[0]
            categories_desc = category_row['Description']
            if category == "Personnalized":
                category_name = st.text_input("What's the category name ?")
                category_desc = st.text_input(f"{category_name}- Add a describe :")
                if st.button("Save"):
                    Category.add_category(category_name, category_desc)
                    st.rerun()

            else : 
                category_id= category_row['CategoryID']
                st.text(f"Description : {categories_desc}")
            if st.button("Save Habit"):
                if not error:
                    Habit.add_habit(habit_name, habit_desc, category_id, days)
                    st.success("Habit saved!")
                    time.sleep(0.07)
                    st.rerun()      
                else:
                    st.warning("Please choose another name")

        elif choice == "Weekly":
            habit_name = st.text_input("Habit name:")
            if habit_name:
                habit_row = habit_list_all.loc[habit_list_all['Habit'] == habit_name]
                error = None
                if not habit_row.empty:  # DataFrame result is not empty
                    habit_row = habit_row.iloc[0]
                    error = st.error("This name is already taken, please try another name")
                else:
                    pass
            else:
                pass
            habit_desc = st.text_input("Describe your habit:")
            days = st.multiselect("Select days:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

            category_list = Category.show_category()
            categories = category_list['Name'].tolist() + ["Personnalized"]
            category = st.selectbox("Select Category:", categories)
            category_row = category_list.loc[category_list['Name'] == category].iloc[0]
            categories_desc = category_row['Description']
            if category == "Personnalized":
                category_name = st.text_input("What's the category name ?")
                category_desc = st.text_input(f"{category_name}- Add a describe :")
                if st.button("Save"):
                    Category.add_category(category_name, category_desc)
                    st.rerun()

            else : 
                category_id= category_row['CategoryID']
                st.text(f"Description : {categories_desc}")
                if st.button("Save Habit"):
                    if not error:
                        Habit.add_habit(habit_name, habit_desc, category_id, days)
                        st.success("Habit saved!")
                        time.sleep(0.07)
                        st.rerun()      
                    else:
                        st.warning("Please choose another name")

    if habit_select == "Modify habit":
        
        category_list = Category.show_category()
        modif_habit = st.selectbox("Which habit do you want to modify?", habit_list_all['Habit'].tolist() , placeholder ="Choose an option", index = None)
        habit_row = habit_list_all.loc[habit_list_all['Habit'] == modif_habit]
        col1, col2, col3, col4 = st.columns(4)
        habit_new_name = col1.text_input("New habit name:", value= modif_habit, placeholder = "Enter the habit name")
        if habit_new_name:
                habit_row_new_name = habit_list_all.loc[habit_list_all['Habit'] == modif_habit].iloc[0]
                error = None
                if habit_new_name != modif_habit:
                    if not habit_row_new_name.empty:  # DataFrame result is more than 1 because the habit who is modifying is counted in
                        habit_row_verif = habit_row.iloc[0]
                        error = st.error("This name is already taken, please try another name")
                else:
                    pass
        habit_id = habit_row['HabitID']
        habit_desc = habit_row['Description'].iloc[0]
        old_category = habit_row['Category'].iloc[0]
        old_category = str(old_category) if old_category else "Enter a category"
        categories = category_list['Name'].tolist() + ["Personnalized"]
        habit_new_desc = col2.text_input("New description:", placeholder = habit_desc or "Enter a description")
        days = col4.multiselect("Select days:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],)
        category = col3.selectbox("Select Category:", categories, placeholder = old_category, index= None)

        if category == "Personnalized":
            category_name = st.text_input("What's the category name ?")
            category_desc = st.text_input(f"{category_name}- Add a describe :")
            if st.button("Save"):
                Category.add_category(category_name, category_desc)
                st.rerun()
        if category and category != "Personnalized":
            category_row = category_list.loc[category_list['Name'] == category].iloc[0]

            if not category_row.empty: 
                category = category_list
                category_id = category_row['CategoryID']
                st.text(category_id)
                category_desc = category_row['Description']
                if habit_desc:
                    col2.text(f"Description : {habit_desc}")
                if category_desc:
                    col3.text(f"Description : {category_desc}")
        if st.button("Save Habit"):
            if not error:
                Habit.modify_habit(habit_new_name,habit_new_desc, category_id, habit_id ,days)
                st.success("Habit saved!")
                time.sleep(0.07)
                st.rerun()
            else:
                st.warning("Please choose another habit name")

    if habit_select == "Delete habit":
        modif_habit = st.selectbox("Which habit do you want to delete?", habit_name_list)
        habit_id = int(habit_list_all.loc[habit_list_all['Habit'] == modif_habit, 'HabitID'].values[0])
        st.text(f"Do you want to delete {modif_habit}({habit_id}) ?")
        if st.toggle("Are you really sure ?"):                                  
            if st.button("Delete Habit", key =3):
                Habit.delete_habit(habit_id)
                st.success("You habit as been deleted")
                time.sleep(0.07)
                st.rerun()
    if habit_select == "All habit":
        df_grouped_by_day = Habit.show_habit()
        st.dataframe(df_grouped_by_day, width='stretch', hide_index= True)
        
with tab3:
    category_list = Category.show_category()
    categories = category_list['Name'].tolist()
    st.dataframe(category_list, hide_index= True, width='stretch')
    #st.data_editor(category_list, disabled= ("CategoryID",), on_change= Habit.modify_habit(habit_new_name :, category_id, days))

    cat_select = st.selectbox("Action", ["Add category","Modify category","Delete category"], placeholder ="Choose an option", index= None)
    st.divider()
    if cat_select == "Add category":
        category_name= st.text_input("Category name :", placeholder= "Enter the category")
        if category_name:
            category_row = category_list.loc[category_list['Name'] == category_name]
            error = None
            if not category_row.empty:
                error : st.error("This name is already taken, please try another name")
        else:
            pass
        category_desc= st.text_input("Describe your category:", placeholder= "Enter a description")
        if st.button("Save"):
            if error is not None:
                Category.add_category(category_name,category_desc)
                st.success("Your category has been added successfully.")
            else:
                st.warning("This name is already taken, please try another name")

    if cat_select == "Modify category":
        category_name = st.selectbox("What's the category", categories, key=2)
        category_row = category_list.loc[category_list["Name"] == category_name]
        category_desc  = category_row["Description"].iloc[0]
        col1, col2 = st.columns(2)
        new_category_name= col1.text_input("New category name :", value= category_name)
        if new_category_name != category_name:
            category_row = category_list.loc[category_list["Name"] == new_category_name]
            error = None
            if not category_row.empty :
                Error = st.error('This name is already taken, please try another name')
            else:
                pass
        else: 
            pass
        new_category_desc= col2.text_area("Describe your new category:", value = category_desc)
        if st.button("Save"):
            if error != None:
                Category.modify_category(new_category_name,new_category_desc,category_name)
                st.success("Your category has been added successfully.")
            else:
                st.warning("Please choose another habit name")
    if cat_select == "Delete category":
        category_name = st.selectbox("What's the category", categories, key=2)
        category_id = category_list.loc[category_list['Name'] == category_name, 'CategoryID'].values[0]
        count = Category.delete_category_validation(category_id)
        st.text(f"Do you want to delete {category_name} ?")
        if st.toggle("Are you really sure ?"):
            if st.button("Delete Category", key =5):
                if count > 0:
                    st.error(f"You still have {count} habit assosiated with this category, please modify them before deleting")
                else:
                    Category.delete_category(category_id)
                    st.success("You category has been deleted")
with tab4:
    df = Stat.most_done()
    st.title("Analytics.")
    st.divider()
    st.markdown(f"Your best day streak : {Stat.longest_daystreak()} ")


    st.divider()
    days_back = st.select_slider("Select period (days):", list(range(1, 61)), value=30)

    if not df.empty:
            # Make sure DateDone is in datetime format
        df['DateDone'] = pd.to_datetime(df['DateDone'])

            # Calculate the start date for filtering
        start_date = pd.Timestamp.today() - pd.Timedelta(days=days_back)

            # Filter the DataFrame
        df_filtered = df[df['DateDone'] >= start_date]

        if df_filtered.empty:
                st.info(f"No habits done in the last {days_back} days.")
        else:
                # Group by habit name and count the "done" entries
            df_grouped = df_filtered.groupby('Name').size().reset_index(name='DoneCount')

                # Plot the grouped data
            fig = px.bar(
                df_grouped,
                x='Name',
                y='DoneCount',
                title=f"Habits done in the last {days_back} days",
                color='Name'
                )
            st.plotly_chart(fig, width='stretch')
    else:
        st.info("No data available.")
    
    st.divider()
    #longest streak by habit plot
    fig = Stat.longest_streak()
    st.plotly_chart(fig, width='stretch')

    st.divider()
    #plot with habit done by day
    days_back_2 = st.select_slider("Select period (days):", list(range(1, 61)), value=30, key=3)
    fig = Stat.most_productive_days()
    st.plotly_chart(fig, width='stretch')


    st.divider()
    #multiple plot
    col1,col2 = st.columns(2)
    col3,col4 =st.columns(2)
    with col1:
        st.plotly_chart(Stat.day_with_the_most_habit())
    with col2:
        st.plotly_chart(Stat.category_with_the_most_habit())
    with col3:
        st.plotly_chart(Stat.category_the_most_done())
    with col4:
        st.plotly_chart(Stat.days_the_most_done())
    
    
with tab5:
    st.title("Reward")
    st.divider()
    col1, col2, col3, col4 = st.columns(4, vertical_alignment= "center")
    with col1:
        reward_data = Stat.longest_daystreak()
        if reward_data >= 5:
            icon = st.markdown(f"<h1 style='text-align:center; opacity: 1; '>🚨</h1>", unsafe_allow_html=True)
            legend =st.markdown(f"<h5 style='text-align:center; opacity: 1; '>5 days streak</h5>", unsafe_allow_html=True)
        else:
            icon = st.markdown(f"<h1 style='text-align:center; opacity: 0.1; '>🚨</h1>", unsafe_allow_html=True)
            legend = st.markdown(f"<h5 style='text-align:center; opacity: 0.1; '>5 days streak</h5>", unsafe_allow_html=True)
    with col2:
        reward_data = Stat.longest_daystreak()
        if reward_data >= 15:
            icon = st.markdown(f"<h1 style='text-align:center; opacity: 1; '>🚨</h1>", unsafe_allow_html=True)
            legend =st.markdown(f"<h5 style='text-align:center; opacity: 1; '>15 days streak</h5>", unsafe_allow_html=True)
        else:
            icon = st.markdown(f"<h1 style='text-align:center; opacity: 0.1; '>🚨</h1>", unsafe_allow_html=True)
            legend = st.markdown(f"<h5 style='text-align:center; opacity: 0.1; '>15 days streak</h5>", unsafe_allow_html=True)

    with col3:
        reward_data = Stat.longest_daystreak()
        if reward_data >= 25:
            icon = st.markdown(f"<h1 style='text-align:center; opacity: 1; '>🚨</h1>", unsafe_allow_html=True)
            legend =st.markdown(f"<h5 style='text-align:center; opacity: 1; '>25 days streak</h5>", unsafe_allow_html=True)
        else:
            icon = st.markdown(f"<h1 style='text-align:center; opacity: 0.1; '>🚨</h1>", unsafe_allow_html=True)
            legend = st.markdown(f"<h5 style='text-align:center; opacity: 0.1; '>25 days streak</h5>", unsafe_allow_html=True)
    with col4:
        reward_data = True
        if reward_data >= 50:
            icon = st.markdown(f"<h1 style='text-align:center; opacity: 1; '>🚨</h1>", unsafe_allow_html=True)
            legend =st.markdown(f"<h5 style='text-align:center; opacity: 1; '>50 days streak</h5>", unsafe_allow_html=True)
        else:
            icon = st.markdown(f"<h1 style='text-align:center; opacity: 0.1; '>🚨</h1>", unsafe_allow_html=True)
            legend = st.markdown(f"<h5 style='text-align:center; opacity: 0.1; '>50 days streak</h5>", unsafe_allow_html=True)

    st.divider()

    with tab6:
        st.title("Productivity suggestion")
        st.divider()

        