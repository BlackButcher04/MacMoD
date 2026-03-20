***Welcome to MacMoD Launch Version***

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is a AI driven machines predictive monitoring dashboard.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requirement to run MacMoD
1. Install Database Management System and Manager (such as Xampp or HeidiSQL).
2. Package/Library use for MacMod :-
   a. Streamlit
   b. Numpy
   c. Joblib
   d. Pandas
   e. FPDF
   f. MySQL-Connector
   Thus, it's require to install library above to make sure MacMoD able to run as well.
3. Suggest to run MacMoD with Spyder and Ananconda.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Step to run MacMoD
1. Create Database with name macmod_db.
2. Paste the SQL File script as well by following the table and it's data. Machines > Conditions_Log > Maintenance_Log.
3. Make sure the database password in each .py file is password="" .
4. Make sure the .pkl file path is correct in diagnose.py file. The .pkl file is the "brain" of AI to predict the RUL.
5. In Ananconda Terminal, run MacMoD with "streamlit run "MaMoD_path_in_your_pc\index.py" "
5. Control + C to terminate the MacMoD. Running in Ananconda Terminal

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For inquiry: Please contact 
Email (Jun Hwa): ljhwa2004@gmail.com (For setup inquiry)
Email (Hoe Yien): (For usage inquiry)
Email (Huey Lym): (For MacMoD friendly feedback)
