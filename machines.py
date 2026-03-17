import streamlit as st
import mysql.connector
import time

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="macmod_db"
        )
except mysql.connector.Error as err:
        st.write(err)    


cursor = conn.cursor()


# You may start your code here
# st.title("Machines")
# st.write("Here's the place you manage your terminal")

# Replace st.title and st.write with this:
st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div class="macmod-title">Machines Control Panel</div>
        <div class="macmod-subtitle">"Here's the place you manage your machines.</div>
    </div>
""", unsafe_allow_html=True)
st.write("---")

@st.dialog("Add New Machines")
def add():
    #st.write("Machines Name")
    machinesName = st.text_input("Machines Name")
    serial_number = st.text_input("Serial Number")
    if st.button("Submit"):
        if machinesName and serial_number:
            try:
                query_sql = "SELECT serial_number FROM machines WHERE serial_number = (%s)"
                query_value = (serial_number,)
                cursor.execute(query_sql, query_value)
                row_validate = cursor.fetchall()
                row_count_len = len(row_validate)
                
                if row_count_len < 1:
                    insert_sql = "INSERT INTO machines (machinesName, serial_number, status_use) VALUES (%s,%s,%s)"
                    insert_val = (machinesName, serial_number, "ACTIVE")
                    cursor.execute(insert_sql, insert_val)
                    conn.commit()
                    st.success("Data add successfully.✅")
                    time.sleep(1)  
                    st.rerun()
                    
                else:
                    st.warning("This machines has been registered.")
                
            except mysql.connector.Error as err:
                st.error("Data add failed.❌")
            #st.rerun()
        else:
            st.error("Please fill the blank.")

# Added current_status to the parameters
@st.dialog("Updates Machines Detail")
def update(id, current_name, current_serial, current_status): 
    machinesID = id
    
    machinesName = st.text_input("Machines Name", value=current_name)
    serial_number = st.text_input("Serial Number", value=current_serial)
    
    # 1. Define the allowed statuses
    status_options = ["ACTIVE", "INACTIVE"]
    
    # 2. Find the index of the current status so the select box defaults to it
    try:
        # We use .upper() just in case it was saved in lowercase in the DB
        default_index = status_options.index(current_status.upper()) 
    except ValueError:
        default_index = 0 # Defaults to "ACTIVE" if the status isn't in the list
        
    # 3. Create the select box
    status_use = st.selectbox("Status", options=status_options, index=default_index)
    
    if st.button("Update"):
        if machinesName and serial_number:
            try:
                # FIX: Added status_use to the UPDATE query
                update_sql = "UPDATE machines SET machinesName = %s, serial_number = %s, status_use = %s WHERE machinesID = %s"
                update_val = (machinesName, serial_number, status_use, machinesID)
                
                cursor.execute(update_sql, update_val)
                conn.commit()
                st.success("Data updated successfully.✅")
                time.sleep(1)
                st.rerun()
                
            except mysql.connector.Error as err:
                st.error(f"Data update failed.❌ Error: {err}")
        else:
            st.error("Please fill in all blanks.")
            
if st.button("Add New"): 
    add()

try:
    cursor.execute("SELECT * FROM machines")
    rows = cursor.fetchall()
    
    if rows:
        # Loop through each machine in the database
        for row in rows:
            # Unpack the tuple into variables
            mac_id = row[0]
            mac_name = row[1]
            mac_serial = row[2]
            mac_status = row[3]
            
            # Create a bordered container "card" for each machine
            with st.container(border=True):
                # Using columns inside the container to space out the info
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(label="Machine Name", value=mac_name)
                with col2:
                    st.metric(label="Serial Number", value=mac_serial)
                with col3:
                    st.write("Status") # Keeps the label aligned with "Action" in col4
                    
                    # Use native Streamlit elements based on the status
                    if mac_status.upper() == "ACTIVE":
                        # You can even customize the icon, or set icon=None to hide it
                        st.success(mac_status) 
                    elif mac_status.upper() == "INACTIVE":
                        st.error(mac_status)
                    else:
                        st.warning(mac_status)
                with col4:
                    #st.metric(label="Action", value=st.button("Update"))
                    st.write("Action")
                    if st.button("Update", key=f"update_btn_{mac_id}"):
                        update(mac_id, mac_name, mac_serial, mac_status)
                           
    else:
        st.info("No machines found in the database. Add one above!")

except mysql.connector.Error as err:
    st.error(f"Failed to fetch data: {err}")