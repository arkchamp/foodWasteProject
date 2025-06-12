import streamlit as st
import psycopg
import pandas as pd
import datetime

# ---------------------- App Title ----------------------
st.set_page_config(page_title="Local Food Wastage Management",layout="wide",page_icon='♻️')
st.title("Local Food Wastage Management System")


# ---------------------- Sidebar Navigation ----------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Project Introduction",
    "View Tables",
    "CRUD Operations",
    "SQL Queries & Visualization",
    "Learner SQL Queries",
    "User Introduction"
])

# ---------------------- Database Connection Setup ----------------------
@st.cache_resource
def connect_db():
    return psycopg.connect(
        dbname = "foodwaste",
        user="postgres",
        password="admin",
        host="localhost",
        port=5432
    )

conn = connect_db()
cursor = conn.cursor()

# ---------------------- Page Routing ----------------------
#PageINTRO
if page == "Project Introduction":
    st.subheader("📌 Project Introduction")
    st.markdown("""
        This project helps manage surplus food and reduce wastage by connecting providers with those in need.

        - **Providers**: Restaurants, households, and businesses list surplus food.
        - **Receivers**: NGOs and individuals claim available food.
        - **Geolocation**: Helps locate nearby food.
        - **SQL Analysis**: Powerful insights using SQL queries.
    """)

#ViewTable
elif page == "View Tables":
    st.subheader("📊 Database Tables")
    #selectbox
    selected_table = st.selectbox("Select Table",["providers","receivers","food_listings","claims"])

    pk_columns = {
        "providers":"provider_id",
        "receivers":"receiver_id",
        "food_listings":"food_id",
        "claims":"claim_id"
    }   #table:id_column

    if selected_table:
        try:
            #getting pk from the selected table from the dict(pk_columns)
            pk_column=pk_columns[selected_table]

            cursor.execute(f'select * from {selected_table} order by {pk_column}')
            rows=cursor.fetchall()
            colnames = [des[0] for des in cursor.description]
            df = pd.DataFrame(rows, columns=colnames)
            st.dataframe(df, use_container_width=True)
            st.success(f"Showing data from '{selected_table}' table")
        except Exception as e:
            st.error(f"Failed to fetch table: {e}")


#CRUD
elif page == "CRUD Operations":
    st.subheader("Manage the food data (CRUD)")

    #Choosing table
    table = st.selectbox("Choose the table",["providers","receivers","food_listings","claims"])
    action = st.radio("Choose an action", ["Add","Update","Delete"])


    #extractcing table columns
    cursor.execute(f"select * from {table} limit 0")
    columns = [des[0] for des in cursor.description]
    # first column is the pk
    pk_column = columns[0]

    inputs={}

    def render_input_fields(columns) :
        for col in columns:
            if col == "quantity":
                inputs[col]=st.number_input("quantity", max_value=50)

            elif col== "status":
                inputs[col]=st.selectbox("status",["Pending","Completed","Cancelled"])

            elif col in ["type","provider_type"]:
                if table in ["providers","food_listings"]:
                    inputs[col]=st.selectbox(col,["Catering Service","Grocery Store","Restaurant","Supermarket"])
                
                elif table == "receivers":
                    inputs[col]=st.selectbox(col,["Charity","Individual","NGO","Shelter"])
                

            elif col== "food_type":
                inputs[col]=st.selectbox(col,["Vegan","Vegetarian","Non-Vegetarian"])

            
            elif col== "meal_type":
                inputs[col]=st.selectbox(col,["Breakfast","Lunch","Snacks","Dinner"])


            elif col == "expiry_date":
                #setting defaultValue as one day from today's date
                default = datetime.date.today() + datetime.timedelta(days=1)
                inputs[col] = st.date_input("expiry_date",value=default)

            elif col == "timestamp":
                #merging date and time
                date_part = st.date_input("(for timestamp) Date: ")
                time_part = st.time_input("(for timestamp) Time: ")
                inputs[col] = datetime.datetime.combine(date_part,time_part)
                
            
            else:
                inputs[col] = st.text_input(f'{col}')

      
        
    #add ->asking all the columns
    if action == "Add":
        with st.form("add_form"):
            st.write(f"Fill the fields for `{action} Operation` on _{table}_")
            render_input_fields(columns)
            submitted = st.form_submit_button("Execute")
            if submitted:
                try:
                    column_names = ",".join(columns)
                    placeholders = ",".join(["%s"]*len(columns))
                    query = f"insert into {table} ({column_names}) values ({placeholders})"

                    values = tuple(inputs[column] for column in columns)        #passing each col as key to retreive the correspond value
                    cursor.execute(query,values)
                    conn.commit()
                    st.success(f"✅ Add operation successful on `{table}`.")

                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error during Add: {e}")



    #update -> asking the pk and allowing to choose fields to update
    elif action == "Update":
        st.markdown(f"""
                    ---
                    Fill the fields for `{action} Operation` on _{table}_""")
        inputs[pk_column] = st.text_input(f"{pk_column} (Primary Key)") #columns[0] is here
        update_cols = st.multiselect("Choose columns to update", columns[1:]) #columns[1] to end is here
        
        if update_cols:
            with st.form("update_form"):
                
                render_input_fields(update_cols)
                submitted = st.form_submit_button("Execute")

                if submitted:
                    try:
                        colWithValues = ", ".join([f"{column} = %s" for column in update_cols])
                        values = [inputs[column] for column in update_cols]
                        values.append(inputs[pk_column]) # Add PK to the end for WHERE clause

                        cursor.execute(
                            f"update {table} set {colWithValues} where {pk_column} = %s",tuple(values)
                        )
                        conn.commit()
                        st.success(f"✅ Update operation successful on *{table}*.")
                    except Exception as e:
                        st.error(f"❌ Update failed: {e}")




    #delete ->asking the pk only
    elif action == "Delete":
        with st.form("delete_form"): 
            st.write(f"Fill the fields for `{action} Operation` on _{table}_")
            inputs[pk_column] = st.text_input(f"{pk_column} (Primary Key)")
            submitted = st.form_submit_button("Execute")
            if submitted:
                try:

                    cursor.execute(f"delete from {table} where {pk_column} = %s", (inputs[pk_column],))
                    conn.commit()
                    st.success(f"✅ Delete operation successful on `{table}`.")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error during Delete: {e}")


elif page == "SQL Queries & Visualization":
    import plotly.express as px
    st.subheader("SQL Queries & Visualization")
    query_map = {
        "1) How many food providers and receivers are there in each city?":"""
            select city, count(provider_id) as  total_providers, count(receiver_id) as total_receivers
            from(
                select city, provider_id, NULL::integer as receiver_id
                from providers
                union all
                select city, NULL::integer as provider_id, receiver_id
                from receivers
            ) as combined
            group by city
            order by city;
        """,
        "2)Which type of food provider (restaurant, grocery store, etc.) contributes the most food?":"""
            select provider_type,sum(quantity) as total_quantity from food_listings
            group by provider_type
            having sum(quantity) = (
                select max(total_quantity) from (
                    select sum(quantity) as total_quantity from food_listings
                    group by provider_type
                    )as sub
                );
            """,
        "3) What is the contact information of food providers in a specific city?":None,
        "4) Which receivers have claimed the most food?":"""
            select name,count(claim_id) as total_claims 
            from receivers r
            join claims c 
            on r.receiver_id = c.receiver_id
            group by name,c.receiver_id
            having count(claim_id) = (
                select max(total_claims) from(
                    select count(claim_id) as total_claims from claims 
                    group by receiver_id 
                    )as sub
                )
            order by c.receiver_id;
            """,
        "5) What is the total quantity of food available from all providers?":"""
            select sum(quantity) as total_quantity_available from food_listings;
        """,
        "6) Which city has the highest number of food listings?":"""
            select location, count(food_id) as total_listings from food_listings
            group by location
            having count(food_id) = (
            select max(total_listings) from (
            select count(food_id) as total_listings from food_listings
            group by location)as sub
            );""",
        "7) What are the most commonly available food types?":"""
            select food_type, count(*) as most_common_foodType from food_listings
            group by food_type
            order by most_common_foodType desc""",
        "8)How many food claims have been made for each food item?":"""
            select food_name,count(claim_id) as no_of_food_Claims from claims c 
            join food_listings f
            on c.food_id = f.food_id
            group by food_name
            order by no_of_food_Claims;""",
        "9) Which provider has had the highest number of successful food claims?":"""
            select name, count(claim_id) as successful_claims from providers p
            join food_listings f on p.provider_id = f.provider_id
            join claims c on f.food_id = c.food_id
            where status = 'Completed'
            group by name
            having count(claim_id) = (
                select max(max_claims) from (
                    select count(claim_id) as max_claims from food_listings f
                    join claims c on f.food_id = c.food_id
                    where status = 'Completed'
                    group by provider_id) as sub
                );
                """,
        "10) What percentage of food claims are completed vs. pending vs. canceled?":"""
            select status, round(100 * count(*)/(select count(*) from claims), 2) as percentage from claims
            group by status;""",
        "11) What is the average quantity of food claimed per receiver?":"""
            select name,round(avg(quantity),2) as average_quantity from food_listings f
            join claims c on f.food_id = c.food_id
            join receivers r on c.receiver_id = r.receiver_id
            group by name;""",
        "12) Which meal type (breakfast, lunch, dinner, snacks) is claimed the most?":"""
            select meal_type,count(claim_id) as total_claims from food_listings f
            join claims c on f.food_id = c.food_id
            group by meal_type
            having count(claim_id) = (
            select max(total_claims) from (
            select count(claim_id) as total_claims from food_listings f
            join claims c on f.food_id = c.food_id
            group by meal_type)as sub);""",
        "13) What is the total quantity of food donated by each provider?":"""
            select name as provider_name ,sum(quantity) as total_quantity from providers p
            join food_listings f on p.provider_id = f.provider_id
            group by name
            order by total_quantity desc"""
        
    }
   

    query_name = st.selectbox("Choose a query to run", list(query_map.keys()))

    if query_name == "3) What is the contact information of food providers in a specific city?":
        st.subheader("Providers by City")

        #ask user to type a city name
        city = st.text_input("Enter city name to filter (it will match similar if partial name is typed):")

        #run query only if city is selected
        if city:
            query = f"""
                SELECT *
                FROM providers 
                WHERE LOWER(city) LIKE LOWER('%{city}%')
            """
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                
                # Step 3: Display results
                if rows:
                    colnames = [desc[0] for desc in cursor.description]
                    df = pd.DataFrame(rows, columns=colnames)
                    st.dataframe(df)
                else:
                    st.info("No records found for the given city.")
            except Exception as e:
                conn.rollback()
                st.error(f"Error: {e}")

    elif query_name:
        query = query_map[query_name]
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=colnames)
            

            st.dataframe(df, use_container_width=(df.shape[1] > 3))     #df.shape-> (rows,col)->index->(0,1)respectively -> could be 5 rows 3 cols

            # 💡 Insert Visualizations Here
            # Normalize column names for safe matching
            # cols=[col.lower() for col in df.columns]
            # kya ye isme exist karta hai
            if query_name.startswith("7"):
                fig = px.pie(df, names="food_type", values="most_common_foodtype", title="Most Common Food Types")
                st.plotly_chart(fig)

            elif query_name.startswith("8"):
                # fig = px.bar(df, x="food_name", y ="no_of_food_claims", title="Most Frequently Claimed Food Items",
                #              labels={"food_name":"Items", "no_of_food_claims":"Total Claims"})
                # st.plotly_chart(fig)

                #gpt
                st.markdown("""
                    <div style='display: flex; justify-content: space-between;'>
                    <div><h3>Most Frequently Claimed Food Items</h3></div>
                    <div><b>x</b>: Items | <b>y</b>: Total Claims</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.bar_chart(df.set_index("food_name")["no_of_food_claims"])

            elif query_name.startswith("10"):
                import plotly.express as px
                fig = px.pie(df, names="status", values="percentage", title="Claim Status Distribution")
                st.plotly_chart(fig, use_container_width=True)

            elif query_name.startswith("11"):
                import plotly.express as px
                df_sorted = df.sort_values(by="average_quantity", ascending=False)
                fig = px.bar(df_sorted, x="average_quantity", y="name", orientation='h',
                            title="Average Quantity of Food Claimed per Receiver")
                st.plotly_chart(fig, use_container_width=True)

            elif query_name.startswith("13"):
                    df_sorted = df.sort_values(by="total_quantity", ascending=False)
                    fig = px.bar(df_sorted, x="total_quantity", y="provider_name", orientation='h',
                                title="Average Quantity of Food Claimed per Receiver")
                    st.plotly_chart(fig, use_container_width=True)
                    st.bar_chart(df.set_index("provider_name")["total_quantity"])
        except Exception as e:
            conn.rollback()
            st.error(f"❌ Query execution failed: {e}")


elif page == "Learner SQL Queries":
    import plotly.express as px
    st.subheader("Learner SQL Queries")
    query_map = {
        "1) Which type of provider is most common?":"""
            select type, count(provider_id) as total_providers from providers
            group by type
            having count(provider_id) = (
                select max(total_providers) from(
                    select count(provider_id) as total_providers from providers
                    group by type)as sub
                    );
        """,
        "2) Which receiver names appear most frequently in the database?":"""
            select name, count(receiver_id) as total_received from receivers
            group by name
            having count(receiver_id) = (
            select max(total_received) from (select count(receiver_id) as total_received from receivers
            group by name)as sub
            );
        """,
        "3) Which meal types are most commonly listed by food providers?":"""
            select meal_type ,count(provider_id) as meal_type_count from food_listings
            group by meal_type
            having count(provider_id) = (
            select max(meal_type_count) from (
            select count(provider_id) as meal_type_count from food_listings
            group by meal_type) as sub)
        """,
        "4) Rank the Top food items claimed":"""
            select 
                food_name, 
                count(claim_id) as no_of_claimed_food,
                dense_rank() over (
                    ORDER BY count(claim_id) DESC
                ) as food_rank
            from food_listings f
            join claims c on f.food_id= c.food_id
            group by food_name
        """,
        "5) List the total quantiy of food per item which were never claimed?":"""
            select food_name, sum(quantity) as total_item from food_listings f
            left join claims c on f.food_id=c.food_id
            where status is null
            group by food_name
        """,
        "6) Top 5 cities with the most completed claims":"""
            select location, count(claim_id) as completed_claims from food_listings f
            join claims c on f.food_id = c.food_id
            where status = 'Completed'
            group by location
            order by completed_claims desc limit 5;
        """,
        "7) Provider-wise breakdown of claim statuses":"""
            select name, status,count(*) as total from providers p
            join food_listings f on p.provider_id=f.provider_id
            join claims c on c.food_id= f.food_id
            group by name, status
            order by name
        """,
        "8) Count of unique food items by provider":"""
            select name as provider_name,
                count(distinct(food_name)) as unique_food 
            from providers p
            join food_listings f on p.provider_id = f.provider_id
            group by name
            order by name
        """,
        "9) Average quantity per food type":"""
            select food_type, round(avg(quantity),2) as avg_quantity from food_listings
            group by food_type
            order by avg_quantity
        """,
        "10) Claims made per day ":"""
            select date(timestamp) as claim_date, count(claim_id) from claims
            group by claim_date
            order by claim_date
        """,
        }
    
    query_name = st.selectbox("Choose a query to run",list(query_map.keys()))

    if query_name:
        
        query = query_map[query_name]
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows,columns=colnames)
            st.dataframe(df, use_container_width=(df.shape[1]>3))

            #Visualisations

            
            if query_name.startswith("4"):
                df_sorted = df.sort_values(by="no_of_claimed_food", ascending=True)
                fig = px.bar(df_sorted, x="no_of_claimed_food", y="food_name", orientation="h",
                            title="Top Claimed Food Items")
                st.plotly_chart(fig)

            elif query_name.startswith("5"):
                
                fig = px.bar(df, x="food_name", y="total_item",
                            title="Unclaimed Food Quantity by Item")
                st.plotly_chart(fig)

            
            elif query_name.startswith("7"):
                fig = px.bar(df, x="name", y="total", color="status",color_discrete_map={
                        "Completed": "#89379E",   # green
                        "Pending": "#2AABC2",     # yellow
                        "Cancelled": "#B4E73C"    # red
                    }, barmode="group", title="Provider-wise Claim Status Breakdown")
                st.plotly_chart(fig)

            elif query_name.startswith("8"):
                df_sorted = df.sort_values(by="unique_food", ascending=True)
                fig = px.bar(df_sorted, x="unique_food", y="provider_name",
                            title="Unique Food Items by Provider")
                st.plotly_chart(fig)

            elif query_name.startswith("9"):
                fig = px.pie(df, names="food_type", values="avg_quantity", title="Average Quantity per Food Type")
                st.plotly_chart(fig, use_container_width=True)

                fig = px.bar(df, x="food_type", y="avg_quantity", title="Average Quantity per Food Type",color="food_type",color_discrete_map={
                    "Vegetarian":"#ff2b2b",
                    "Non-Vegetarian":"#83c9ff",
                    "Vegan":"#0068c9",
                },)
                st.plotly_chart(fig)

            elif query_name.startswith("10"):
                fig = px.line(df, x="claim_date", y="count", markers=True, title="📈 Claims Per Day")
                st.plotly_chart(fig)
            


        except Exception as e:
            conn.rollback()
            st.error(f" Error: {e}")


elif page == "User Introduction":
    st.subheader("👤 User Introduction")

    st.markdown("""
    ### 🙋 About the Developer
    - **Name:** Abdullah Khatri  
    - **Role:** Data Science Learner @ GUVI  
    - **Project:** Local Food Wastage Management System  
    - **Tech Stack:** PostgreSQL, Streamlit, Python, Pandas, SQL(psycopg)  

    ### 💬 Description
    This application was developed as part of a mini project in the Data Science course.  
    It demonstrates data analysis, SQL logic, CRUD operations, and interactive dashboards using Streamlit.

    ### 📧 Contact
    - Email: `abdullahkahtri1204@gmail.com`  
    - GitHub: [your-github-link-if-any]

    ### 👨🏽‍💻 What I Learned?
    Throughout the development of this project, I gained hands-on experience and deeper understanding in the following areas:

    📊 **SQL & PostgreSQL**  
    - Writing complex SQL queries using `JOIN`,`UNION`, `GROUP BY`, `HAVING`, `WINDOW FUNCTIONS`, `AGGREGATIONS`, `FILTERS`,`NULL::INTEGER as column-name` and `SUBQUERIES`.
    Designing normalized relational schemas and understanding foreign key relationships.

    🐍 **Python + psycopg**  
    - Loading csv to dataframe, previewing it & checked for nulls by using `table.isnull().sum()`
    - Checked data_type for all columns -> found and fixed -> learned converting dateColumns
    - Connecting PostgreSQL databases with Python using the `psycopg` library.
    - Learned `with` block and used it with `psyocpyg.connect` to close the connection automatically.
    - Learned about `@st.cache_resources`
    - Created function to insert values in the created table with `df.itertuples`.

    🌐 **Streamlit (Web App Development)**  
    - Designing multi-page apps using sidebar navigation.
    - Implementing CRUD operations (Create, Read, Update, Delete) with dynamic form generation.
    - Displayed All SQL queries (13+10) and visual charts (bar, pie, line) only for those query which make sense for chart.
    - Improving user interaction with dynamic widgets like `selectbox`, `date_input`, `multiselect`, etc.

    📈 **Data Visualization & Insights**  
    - Creating meaningful visualizations from SQL output using `Plotly Express`, `st.plotly_chart(fig)` and `st.bar_chart()`.
    - Intepreted trend from claims data.

    🧠 **Problem Solving & Logical Thinking**  
    - Structuring SQL queries to match real-world business analysis.
    - Debugging multi-step logic for conditional updates and data visualization flows.

    ---
    
    """)

