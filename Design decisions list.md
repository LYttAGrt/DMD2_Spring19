* This is how we understood this problem.
  * Users are distibuted on several tables, and all of them have the same basis field, such as name, SSN_ID and etc.
  * We have called everybody, who is related with management process in the hospital, "Administrators": DB administrator, receptionist, etc.
  * Hospital is organized in the list of Departments, and each Department contains differernt Employees: Doctors, Nurses, Paramedics, Stuff, and - indirectly - Patients.
  * There's an Ambulance service (probably one more Department), and it contains teams of Ambulances. We say each team contains Doctor and Paramedics, one of whom is a driver. 

* There's a weak point in our data model, and it is called "additional_data". 
  * Why is it weak? Well, for different tables this field contains specified (and usually distinguished) data.
  * Still, it provides us a space for the model' flexibility.

* We have realized simple and sample user interface, that mostly looks like an DB administrator UI (see kivy_UI.py for details)
  * For this UI, we tried to prevent our database from logical (and partially physical) failures by validating parameters, provided by the user - for example, user cannot directly insert primary key value - instead, system does the calculations. 
  * Actually, we do not have any registration form to sign up or log in. Nonetheless, all necessary fields for this part exist in our data model.

* We are open for suggestions.  
