import streamlit as st
import streamlit_calendar as st_c
from crud import HabitDAO,CategoryDAO,HabitLogDAO, StatDAO
from logic import HabitService,HabitLogService, CategoryService, Utils, HabitNotFound
from exception import HabitNotFound,CategoryNotFound, DatabaseError
import analytics
from database.database import db_conn
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time
import numpy as np

#Setting the base of the app
st.set_page_config(page_title= "Habit Tracker", page_icon= "🌱", layout= "centered",)
st.markdown(f"<h1 style='text-align:center;'>Habit Tracker</h1>", unsafe_allow_html=True)
with db_conn() as conn:
    #DAO
    habit_dao = HabitDAO(conn)
    habit_log_dao = HabitLogDAO(conn)
    analytics_dao = StatDAO(conn)
    category_dao = CategoryDAO(conn)
    #SERVICE
    habit_service = HabitService(habit_dao)
    habit_log_service = HabitLogService(habit_log_dao)
    category_service = CategoryService(category_dao)

    #APP INIT
    habit_log_service.sync_habit_log()

    #DATA
    habit_list = habit_service.get_today_habit()
    habit_list_all = habit_service.get_habit()
    today_logs=habit_log_dao.fetch_today_habit_logs()
    habit_logs = habit_log_dao.fetch_all_habits_logs()
    habit_name_list = [habit["name"] for habit in habit_list]
    #habit_description_list = [habit["description"] for habit in habit_list]
    habit_name_all_list = [habit["name"] for habit in habit_list_all]
    category_df = category_service.get_category_df()
    error = None

    
    
    #DATE
    today_date_string = datetime.today().strftime('%d/%m/%Y')
    today_datetime_date = datetime.today().date()


    #app init
    if "last_date" not in st.session_state:
        st.session_state.last_date = today_datetime_date
    
    if st.session_state.last_date != today_datetime_date:
        for key in list(st.session_state.keys()):
            if isinstance(key,str) and key.startswith("habit_"):
                del st.session_state[key]
        st.session_state.last_date = today_datetime_date
    
    
    tab1, tab2, tab3, tab4,tab5= st.tabs(["Home", "Habits", "Category", "Analyse Habit", "Reward"])

    with tab1:

        rows = analytics_dao.get_habit_streak()
        daystreak = analytics.current_daystreak(rows,today_datetime_date)
        longuest_streak = analytics.longuest_daystreak(rows)
        random_number = np.random.randint(0,1000)
        st.markdown(f"<h5 style='font-size:18px; text-align:center;'>Today : {today_date_string}.</h5>", unsafe_allow_html=True)
        
        try:
            for habit in habit_list:
                habit_id = habit["habit_id"]
                name = habit["name"]
                done = bool(habit["done"])
                key = f"habit_{habit_id}"

                if key not in st.session_state:
                    st.session_state[key] = done

                new_done = st.checkbox(name,key= key)
                if new_done != done:
                    habit_service.update_done(habit_id, done = int(new_done))
                    if new_done == True:
                        st.success("Done")
                    else:
                        st.error("Undone")
                    st.rerun()
        except HabitNotFound as e:
            st.warning(f"{e}")
        except DatabaseError as e:
            st.warning(f"{e}")


        done, total, rate = analytics.daily_completion_rate(habit_logs, today_datetime_date)
        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Habits", len(habit_list))
        col2.metric("Completed", f"{done} / {len(habit_list)}",)
        col3.metric("Streak", f"{daystreak} day(s)",)
        col3.text(f"Best Streak : {longuest_streak} day(s)")
        if len(habit_list) == 0:
            st.progress(0)
        else:
            st.progress(rate/100)
        with st.container(border = True):
            sentence_list = Utils.words()
            st.markdown(f"<t2 style='text-align:center; bold = true'>{sentence_list}</t2>", unsafe_allow_html=True)
        with tab2:
            st.title("Weekly Habit Agenda")
            days = Utils.get_days()
            day_index = st.slider("Select the day",min_value=1, max_value=7, value=1, label_visibility= "hidden", key= 18)
            selected_day = days[day_index-1]
            habit_by_day = habit_service.get_habit_by_day_df(selected_day)

            st.subheader(f"Habits for {selected_day}")
            try:
                st.dataframe(habit_by_day.rename(columns= {"name" : "Habit", "description": "Description","category_name" :"Category"}),width='stretch', hide_index = True)

            except HabitNotFound as e:
                st.warning(e)
            except DatabaseError as e:
                st.warning(e)
            
            try:
                st.divider()
                habit_select = st.selectbox("Action", ["Add habit", "Modify habit", "Delete habit", "All habit"], placeholder ="Choose an option", index= None)
                st.divider()
                if habit_select == "Add habit":
                    choice = st.selectbox("Action", ["Daily", "Weekly"] )
                    if choice == "Daily":
                        add_habit_name = st.text_input("Habit name:")
                        if add_habit_name:
                            error = None
                            if add_habit_name in habit_name_all_list:
                                error = st.error("This name is already taken, please try another name")


                        habit_desc = st.text_input("Describe your habit:")
                        days =  ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                        
                        if category_df is not None and not category_df.empty :

                            category_mapping = dict(zip(category_df["category_id"], category_df["category_name"]))
                            category_mapping[-1] = "Personnalized"

                            selected_category = st.selectbox("Select Category:", options=list(category_mapping.keys()),format_func=lambda x: category_mapping[x])
                            if selected_category != -1 and selected_category is not None :
                                category_desc = category_df.loc[category_df["category_id"] == selected_category, "description"].iloc[0] # pyright: ignore[reportAttributeAccessIssue]
                                st.text(f"Description : {category_desc}")
                                if selected_category != -1:
                                    if st.button("Save Habit", disabled= False if (habit_desc and selected_category and habit_name_list is not None) else True):
                                        if not error:
                                            habit_service.add_habit(add_habit_name, habit_desc, selected_category, days)
                                            st.success("Habit saved!")
                                            time.sleep(0.07)
                                            st.rerun()      
                            else:
                                st.warning("Please choose another name")
                        else:
                            st.warning("You don't have any category, please create one")
                            selected_category = st.selectbox("Select Category:",["Personnalized"])

                        if selected_category == -1:
                            category_name = st.text_input("What's the category name ?")
                            category_desc = st.text_input(f"{category_name}- Add a describe :")
                            if st.button("Save"):
                                category_service.add_category(category_name, category_desc)
                                st.rerun()

                    elif choice == "Weekly":
                        add_habit_name = st.text_input("Habit name:")
                        if add_habit_name:
                            error = None
                            if add_habit_name in habit_name_all_list:
                                error = st.error("This name is already taken, please try another name")

                        habit_desc = st.text_input("Describe your habit:")
                        days = st.multiselect("Select days:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

                        if category_df is not None and not category_df.empty :

                            category_mapping = dict(zip(category_df["category_id"], category_df["category_name"]))
                            category_mapping[-1] = "Personnalized"

                            selected_category = st.selectbox("Select Category:", options=list(category_mapping.keys()),format_func=lambda x: category_mapping[x])
                            if selected_category != -1 and selected_category is not None :
                                category_desc = category_df.loc[category_df["category_id"] == selected_category, "description"]
                                st.text(f"Description : {category_desc}")
                                if selected_category != -1:
                                    if st.button("Save Habit", disabled= False if (habit_desc and selected_category and add_habit_name is not None) else True):
                                        if not error:
                                            habit_service.add_habit(add_habit_name, habit_desc, selected_category, days)
                                            st.success("Habit saved!")
                                            time.sleep(0.07)
                                            st.rerun()      
                            else:
                                st.warning("Please choose another name")
                        else:
                            st.warning("You don't have any category, please create one")
                            selected_category = st.selectbox("Select Category:",["Personnalized"])

                if habit_select == "Modify habit":
                    
                    modif_habit = st.selectbox("Which habit do you want to modify?", habit_name_all_list , placeholder ="Choose an option", index = None)
                    if modif_habit:
                        habit_row = next(filter(lambda h: h["name"] == modif_habit, habit_list_all),None)
                        if habit_row:
                            habit_id = habit_row['habit_id']
                            habit_desc = habit_row['description']
                            old_category = habit_row['category_name']
                            old_category = str(old_category) if old_category else "Enter a category"
                            categories = category_df['category_name'].tolist() + ["Personnalized"]


                            col1, col2, col3, col4 = st.columns(4)
                            habit_new_name = col1.text_input("New habit name:", value= modif_habit, placeholder = "Enter the habit name")
                            habit_new_desc = col2.text_input("New description:", placeholder = habit_desc or "Enter a description")
                            category = col3.selectbox("Select Category:", categories, placeholder=old_category, index=None)
                            days = col4.multiselect("Select days:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],)

                            if habit_new_name:
                                    habit_row_new_name = habit_list_all[habit_row["name"] == modif_habit]
                                    error = None
                                    if habit_new_name != modif_habit:
                                        if not habit_row_new_name.empty and habit_row is not None:  # DataFrame result is more than 1 because the habit who is modifying is counted in
                                            habit_row_verif = habit_row.iloc[0]
                                            error = st.error("This name is already taken, please try another name")
                                    else:
                                        pass
                        
                            if category == "Personnalized":
                                category_name = st.text_input("What's the category name ?")
                                category_desc = st.text_input(f"{category_name}- Add a describe :")
                                if st.button("Save"):
                                    category_service.add_category(category_name, category_desc)
                                    st.rerun()
                            if category and category != "Personnalized":
                                category_row = category_df.loc[category_df['category_name'] == category]

                                if category_row:
                                    category_id = category_row['category_id']
                                    category_desc = category_row['description']
                                    if habit_desc:
                                        col2.text(f"Description : {habit_desc}")
                                    if category_desc is not None:
                                        col3.text(f"Description : {category_desc}")
                            category_id = None
                            if st.button("Save Habit"):
                                if not error:
                                    habit_service.update_habit(habit_new_name,habit_new_desc, category_id, habit_id ,days)
                                    st.success("Habit saved!")
                                    time.sleep(0.07)
                                    st.rerun()
                                else:
                                    st.warning("Please choose another habit name")

                if habit_select == "Delete habit":
                    modif_habit = st.selectbox("Which habit do you want to delete?", habit_name_list)
                    habit_row = next(filter(lambda h: h["name"] == modif_habit, habit_list_all), None)
                    if habit_row:
                        habit_id  = habit_row["habit_id"]
                        st.text(f"Do you want to delete {modif_habit}({habit_id}) ?")
                        if st.toggle("Are you really sure ?"):                                  
                            if st.button("Delete Habit", key =3):
                                habit_service.delete_habit(habit_id)
                                st.success("You habit as been deleted")
                                time.sleep(0.07)
                                st.rerun()
                if habit_select == "All habit":
                    df_grouped_by_day = habit_service.get_habit()
                    st.dataframe(df_grouped_by_day, width='stretch', hide_index= True)
            except HabitNotFound as e:
                st.warning(e)
            except DatabaseError as e:
                st.warning(e)
                
        with tab3:
            categories = category_df['category_name'].tolist()
            st.dataframe(category_df.rename(columns= {"category_id" : "ID","category_name" : "Category", "description": "Description",}), hide_index= True, width='stretch')

            cat_select = st.selectbox("Action", ["Add category","Modify category","Delete category"], placeholder ="Choose an option", index= None)
            st.divider()
            if cat_select == "Add category":
                category_name= st.text_input("Category name :", placeholder= "Enter the category")
                if category_name:
                    category_row = category_df.loc[category_df['category_name'] == category_name]
                    error = None
                    if not category_row.empty:
                        error = st.error("This name is already taken, please try another name")

                category_desc= st.text_input("Describe your category:", placeholder= "Enter a description")
                if st.button("Save"):
                    if error is None:
                        category_service.add_category(category_name,category_desc)
                        st.success("Your category has been added successfully.")
                    else:
                        st.warning("This name is already taken, please try another name")

            if cat_select == "Modify category":
                category_name = st.selectbox("What's the category", categories, key=2)
                category_row = category_df[category_df["category_name"] == category_name]
                category_desc  = category_row["description"].iloc[0]
                col1, col2 = st.columns(2)
                new_category_name= col1.text_input("New category name :", value= category_name)
                if new_category_name != category_name:
                    category_row = category_df[category_df["category_name"] == new_category_name]
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
                        category_service.add_category(new_category_name,new_category_desc)
                        st.success("Your category has been added successfully.")
                    else:
                        st.warning("Please choose another habit name")
            if cat_select == "Delete category":
                category_name = st.selectbox("What's the category", categories, key=2)
                category_id = category_df.loc[category_df['category_name'] == category_name, 'category_id'].values[0]
                delete_category_validation = category_df["category_id"].count()
                st.text(f"Do you want to delete {category_name} ?")
                if st.toggle("Are you really sure ?", key = 500):
                    if st.button("Delete Category", key =5):
                        if delete_category_validation > 0:
                            st.error(f"You still have {delete_category_validation} habit assosiated with this category, please modify them before deleting")
                        else:
                            category_service.delete_category(category_id)
                            st.success("You category has been deleted")
        with tab4:
            st.title("Analytics.")
            st.divider()


            habit_logs_today_yesterday = habit_log_dao.fetch_all_habits_logs_per_date([today_datetime_date, (today_datetime_date - timedelta(1))])

            report_slider = st.pills("Report",options=["Daily","Weekly","Habit", "Category",],label_visibility= "collapsed", default= "Daily")
            if report_slider == "Daily":
                col1,col2 = st.columns([0.4,0.6], border =True, gap = None)
                done, not_done, rate = analytics.daily_completion_rate(habit_logs, today_datetime_date)
                with col1:
                    st.subheader("Daily Completion Rate")
                    fig = px.pie(names= ["Completed", "Not completed"],values = (done, not_done), hole = 0.7 )
                    fig.update_layout(annotations=[dict(
                                                        text=f"{rate:.0f}%",
                                                        x=0.5,
                                                        y=0.5,
                                                            font_size=60,
                                                            showarrow=False)],
                                            showlegend=False)
                    st.plotly_chart(fig)
                    st.divider()


                    comparaison = analytics.productivity_comparaison(habit_logs_today_yesterday,today_datetime_date)
                    if comparaison > 0:
                        st.text(f"You are {comparaison}% more productive than yesterday")
                    elif comparaison < 0:
                        st.text(f"You are {comparaison}% less productive than yesterday")
                    else:
                        st.text(f"Your productivity is the same as yesterday.")
                with col2:
                    try:
                        df, df_raw = analytics.best_productivity_period(today_logs)
                        if df is not None and df_raw is not None and isinstance(df_raw, pd.DataFrame) and not df.empty:
                            plot_df = df.reset_index()
                            plot_df.columns = ["Hour Range", "Completions"]

                            plot_df = plot_df.sort_values("Hour Range")

                            fig = px.bar(
                                plot_df,
                                x="Hour Range",
                                y="Completions",
                                title="Best Productivity Period",
                            )
                            fig.update_xaxes(type="category")
                            fig.update_layout(
                                xaxis_title="Hour of the Day",
                                yaxis_title="Number of Completed Habits",
                            )
                            result = st.plotly_chart(fig,config = {'scrollZoom': False,}, selection_mode= ["points"] ,on_select= "rerun")
                            if result["selection"]["points"]:
                                selected_hours = result["selection"]["points"][0]["x"]
                                df_filtered = df_raw[df_raw["hour_range"].astype(str) == selected_hours]
                                st.subheader("Habit done on this periods:")
                                for _, row in df_filtered.iterrows():
                                    st.text(f"{row["habit_name"]} / {row["complete_at"]}")
                        else:
                            st.text("No data")
                    except Exception as e:
                        st.error(e)
            if report_slider =="Weekly":
                if "week_offset" not in st.session_state:
                    st.session_state.week_offset = 0

                week_start = (datetime.today() - timedelta(days = datetime.today().weekday()) + timedelta(weeks= st.session_state.week_offset)).date()
                week_end = week_start + timedelta(6)
                col1,col2 = st.columns([0.4,0.6], border =True, gap = None)
                done, not_done, rate = analytics.weekly_completion_rate(habit_logs, week_start, week_end)
                with col1:
                    st.subheader("Weekly Completion Rate")
                    fig = px.pie(names= ["Completed", "Not completed"],values = (done, not_done), hole = 0.7 )
                    fig.update_layout(annotations=[dict(
                                                        text=f"{rate:.0f}%",
                                                        x=0.5,
                                                        y=0.5,
                                                            font_size=60,
                                                            showarrow=False)],
                                            showlegend=False)
                    st.plotly_chart(fig)
                    st.divider()
                with col2:
                    col1,col2,col3 = st.columns([0.3,0.6,0.3], border= True)
                    with st.container(border = True):
                        with col1:
                            if st.button("◀", use_container_width= True, key = 1000):
                                st.session_state.week_offset -= 1
                                st.rerun()
                        with col2:
                            if st.button("Today",use_container_width= True, key = 1100):
                                st.session_state.week_offset = 0
                                st.rerun()
                            st.text(f"{week_start} - {week_end}", text_alignment= "center")
                        with col3:
                            if st.button("▶", use_container_width= True, key= 2409):
                                st.session_state.week_offset += 1
                                st.rerun()

                        df = analytics.weekly_completion_day_per_day(habit_logs, week_start, week_end)
                        fig = px.bar(df,x= "date_label", y = "completion_rate", labels={"date_label": "Day", "completion_rate": "Completion Rate"})
                        fig.update_xaxes(range = [0,None])
                        fig.update_yaxes(range = [0,1])
                        st.plotly_chart(fig)

            if report_slider == "Habit":
                st.subheader("Habits reports.", text_alignment= "center")
                col1,col2 = st.columns(2,gap = None , border= True)
                with col1:
        
                    done, not_done, rate = analytics.completion_rate(habit_logs)
                    st.subheader("Global Completion Rate")
                    fig = px.pie(names= ["Completed", "Not completed"],values = (done, not_done), hole = 0.7 )
                    fig.update_layout(annotations=[dict(
                                                        text=f"{rate:.0f}%",
                                                        x=0.5,
                                                        y=0.5,
                                                        font_size=60,
                                                        showarrow=False)],
                                        showlegend=False)
                    st.plotly_chart(fig)
                    st.divider()
                    #max streak by habits
                    st.subheader("Habits Streaks:")
                    habit_streaks_list = analytics.longuest_habit_streak(habit_logs)
                    fig = px.bar(x = list(habit_streaks_list.keys()), y = list(habit_streaks_list.values()), labels= {"x": "Habits", "y": "Longest streak"})
                    st.plotly_chart(fig)
                    best_habit = max(habit_streaks_list, key= lambda k:habit_streaks_list[k])
                    st.text(f"The habit with the longuest streak is :\n {best_habit}")
                with col2:
                    st.subheader("Completed Habits", text_alignment= "center")
                    done_by_habits = analytics.group_habit_for_plot(habit_logs)
                    fig = px.bar( x = done_by_habits["habit_name"], y = done_by_habits["done"], labels={"x": "Habits", "y": "Times completed"})
                    st.plotly_chart(fig)
                    with st.container(border = True, height= 350 ):
                        st.text(f"Top of the habits:")
                        top_habits = done_by_habits.sort_values(by= "done", ascending=False)
                        for i, (_, row) in enumerate(top_habits.iterrows()):
                            with st.container(border = True):
                              st.text(f"{i}) {row['habit_name']} / done : {row['done']}")
                                    
                
                #By habit analytics
                st.subheader("Habit to analyse:")
                habit_name = st.selectbox("Habit to report", done_by_habits["habit_name"] , placeholder ="Choose an option", label_visibility= "collapsed",index = None)
                if habit_name:
                    st.subheader(f"Habit report: {habit_name}", text_alignment="center")
                    col1,col2 = st.columns(2)
                    with col1:
                        done, not_done, rate = analytics.habit_completion_rate(habit_logs, habit_name)
                        st.subheader("Completion Rate")
                        fig = px.pie(names= ["Completed", "Not completed"],values = (done, not_done), hole = 0.7 )
                        fig.update_layout(annotations=[dict(
                                                            text=f"{rate:.0f}%",
                                                            x=0.5,
                                                            y=0.5,
                                                            font_size=60,
                                                            showarrow=False)],
                                            showlegend=False)
                        st.plotly_chart(fig)
                        df = analytics.habit_most_productive_day(habit_logs, habit_name)
                        st.text(f"The most productive days for this habit is : {df}")
                    with col2:
                        with st.container(border= True):
                            habit_streak_by_habit = analytics.longuest_habit_streak_by_habit(habit_logs, habit_name)
                            st.text(f"Best streak : {habit_streak_by_habit}")

            if report_slider == "Category":
                
                all_category_df = category_service.get_category_df()
                options_filtering = ["Daily", "Weekly","Global"]
                selected_pills =st.pills(label= "Filtering the plot", options=options_filtering, default= options_filtering[0])
                date = None
                if selected_pills == options_filtering[0]:
                    date = today_datetime_date
                if selected_pills == options_filtering[1]:
                    if "week_offset" not in st.session_state:
                        st.session_state.week_offset = 0

                    week_start = (datetime.today() - timedelta(days = datetime.today().weekday()) + timedelta(weeks= st.session_state.week_offset)).date()
                    week_end = week_start + timedelta(6)
                    date = [week_start, week_end]
                if selected_pills == options_filtering[2]:
                    date = None

                df = analytics.category_completion_rate(habit_logs,date)
                fig = px.bar(df.sort_values("completion_rate").rename(columns= {"category_name": "Category", "completion_rate": "Completion rate"}),
                            x="Category",
                            y="Completion rate",
                            text="Completion rate",
                            title=(f"Completion Rate by Category - {(f'{date[0]} / {date[1]}')if isinstance(date,list) else (date if date else 'Global')}") ,
                            labels= {"x": "Categories", "y": "Completion Rate"}
                        )

                fig.update_traces(texttemplate="%{text:.0%}")
                fig.update_yaxes(tickformat=".0%")

                st.plotly_chart(fig)
                # Charts for category and top
                

                #analysis per category 

                st.subheader("Category to analyse:")
                category_name = st.selectbox("Category to analyse", all_category_df["category_name"] , placeholder ="Choose an option", label_visibility= "collapsed",index = None)
                if category_name:
                    st.subheader(f"Category Analytics: {category_name}", text_alignment="center")
                    col1,col2 = st.columns(2)
                    with col1:
                        category_rate = analytics.category_completion_rate_per_category(habit_logs, category_name)
                        rate = category_rate["completion_rate"].iloc[0]
                        st.subheader("Completion Rate")
                        fig = px.pie(names= ["Completed", "Not Completed"], values = [rate, 1-rate], hole = 0.7 )
                        fig.update_layout(annotations=[dict(
                                                            text=f"{(rate*100):.0f}%",
                                                            x=0.5,
                                                            y=0.5,
                                                            font_size=60,
                                                            showarrow=False)],
                                            showlegend=False)
                        st.plotly_chart(fig)
                  
    
            
        with tab5:
            st.title("Reward")
            st.divider()
            col1, col2, col3, col4 = st.columns(4, vertical_alignment= "center")
            with col1:
                reward_data = longuest_streak
                if reward_data >= 5:
                    icon = st.markdown(f"<h1 style='text-align:center; opacity: 1; '>🚨</h1>", unsafe_allow_html=True)
                    legend =st.markdown(f"<h5 style='text-align:center; opacity: 1; '>5 days streak</h5>", unsafe_allow_html=True)
                else:
                    icon = st.markdown(f"<h1 style='text-align:center; opacity: 0.1; '>🚨</h1>", unsafe_allow_html=True)
                    legend = st.markdown(f"<h5 style='text-align:center; opacity: 0.1; '>5 days streak</h5>", unsafe_allow_html=True)
            with col2:
                if reward_data >= 15:
                    icon = st.markdown(f"<h1 style='text-align:center; opacity: 1; '>🚨</h1>", unsafe_allow_html=True)
                    legend =st.markdown(f"<h5 style='text-align:center; opacity: 1; '>15 days streak</h5>", unsafe_allow_html=True)
                else:
                    icon = st.markdown(f"<h1 style='text-align:center; opacity: 0.1; '>🚨</h1>", unsafe_allow_html=True)
                    legend = st.markdown(f"<h5 style='text-align:center; opacity: 0.1; '>15 days streak</h5>", unsafe_allow_html=True)

            with col3:
                if reward_data >= 25:
                    icon = st.markdown(f"<h1 style='text-align:center; opacity: 1; '>🚨</h1>", unsafe_allow_html=True)
                    legend =st.markdown(f"<h5 style='text-align:center; opacity: 1; '>25 days streak</h5>", unsafe_allow_html=True)
                else:
                    icon = st.markdown(f"<h1 style='text-align:center; opacity: 0.1; '>🚨</h1>", unsafe_allow_html=True)
                    legend = st.markdown(f"<h5 style='text-align:center; opacity: 0.1; '>25 days streak</h5>", unsafe_allow_html=True)
            with col4:
                if reward_data >= 50:
                    icon = st.markdown(f"<h1 style='text-align:center; opacity: 1; '>🚨</h1>", unsafe_allow_html=True)
                    legend =st.markdown(f"<h5 style='text-align:center; opacity: 1; '>50 days streak</h5>", unsafe_allow_html=True)
                else:
                    icon = st.markdown(f"<h1 style='text-align:center; opacity: 0.1; '>🚨</h1>", unsafe_allow_html=True)
                    legend = st.markdown(f"<h5 style='text-align:center; opacity: 0.1; '>50 days streak</h5>", unsafe_allow_html=True)

            st.divider()