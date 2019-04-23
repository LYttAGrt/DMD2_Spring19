# Still, we need connection
from rethinkdb import RethinkDB

# Let's use kivy library to make UI
import kivy
# use it to run app
from kivy.app import App
# Layout is responded for drawing the widgets
from kivy.uix.boxlayout import BoxLayout
# these widgets should be just enough
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

# Builder can be used to markup all widgets
from kivy.lang import Builder

# check kivy-version is correct
kivy.require('1.10.1')


class MainActivity(App):
    # Set up connection in the very beginning, cache some useful data
    rdb = RethinkDB()
    conn = rdb.connect(db='HMS')
    tables = rdb.db('HMS').table_list().run(conn)

    # Puts the values that should be used: F(str, int) -> str
    def set_hint_values(self, instance, param):
        # get type of ops. Should be one of CRUD types
        ops_type = self.spinner_crud.text
        # get all necessary indices of current table
        indices = self.rdb.db('HMS').table(self.spinner_table.text).get(0).keys().run(self.conn)

        if ops_type == 'Add':
            # set all hint_texts for inserting new data
            for i in range(len(indices)):
                try:
                    substr = str(indices[i]).index("primary_id")
                    if str(indices[i]).index("_id") != -1 and substr != -1:
                        self.list_of_text_inputs[i].hint_text = str("Service field: " + str(indices[i]))
                        self.list_of_text_inputs[i].disabled = True
                except ValueError:
                    self.list_of_text_inputs[i].hint_text = "Type addable value of candidate's " + str(indices[i])
                    self.list_of_text_inputs[i].disabled = False
                    self.list_of_text_inputs[i].text = ""
            for i in range(len(indices), len(self.list_of_text_inputs) - 1):
                self.list_of_text_inputs[i].hint_text = "Not used"
                self.list_of_text_inputs[i].disabled = True
                self.list_of_text_inputs[i].text = ""

        if ops_type == 'Change':
            # we don't realize this feature, but fool protection should exist
            for i in range(len(self.list_of_text_inputs) - 1):
                self.list_of_text_inputs[i].hint_text = "Feature is unavailable"
                self.list_of_text_inputs[i].disabled = True

        if ops_type == 'Remove':
            # then we use our text_inputs as filters
            for i in range(len(indices)):
                self.list_of_text_inputs[i].hint_text = "Type filterable value of candidate's " + str(indices[i])
                self.list_of_text_inputs[i].disabled = False
                self.list_of_text_inputs[i].text = ""
                if indices[i] == 'password':
                    self.list_of_text_inputs[i].hint_text = "Not shown"
                    self.list_of_text_inputs[i].disabled = True
                    self.list_of_text_inputs[i].text = ""
            for i in range(len(indices), len(self.list_of_text_inputs) - 1):
                self.list_of_text_inputs[i].hint_text = "Not used"
                self.list_of_text_inputs[i].disabled = True
                self.list_of_text_inputs[i].text = ""

        if ops_type == 'Print':
            # then we use our text_inputs as filters
            for i in range(len(indices)):
                self.list_of_text_inputs[i].hint_text = "Type filterable value of candidate's " + str(indices[i])
                self.list_of_text_inputs[i].disabled = False
                self.list_of_text_inputs[i].text = ""
                if indices[i] == 'password':
                    self.list_of_text_inputs[i].hint_text = "Not shown"
                    self.list_of_text_inputs[i].disabled = True
                    self.list_of_text_inputs[i].text = ""
            for i in range(len(indices), len(self.list_of_text_inputs) - 1):
                self.list_of_text_inputs[i].hint_text = "Not used"
                self.list_of_text_inputs[i].disabled = True
                self.list_of_text_inputs[i].text = ""

        return True

    # Checks if values have correct types. Doesn't fix incorrect values.
    # suspected_data: dictionary of pairs (index as field name, value of field)
    def validate_data(self, suspected_data: dict):
        print(suspected_data)
        if self.spinner_crud.text == "Add":
            for entry in suspected_data:
                if str(entry) == "additional_data":
                    continue

                # if key reflects list of ids, value should be a list of ints
                if str(entry).find("_ids") != -1:
                    # cast it to list
                    suspected_data[entry] = str(suspected_data[entry]).split(" ")
                    # check it contains integers only
                    for k in range(len(suspected_data[entry])):
                        try:
                            suspected_data[entry][k] = int(suspected_data[entry][k])
                        except ValueError:
                            print(str(suspected_data[entry][k]), "is not an integer. Check rest List members.")
                            return False
                # if key is an identifier, value should be integer only
                elif str(entry).find("_id") != -1:
                    try:
                        suspected_data[entry] = int(suspected_data[entry])
                    except ValueError:
                        print(str(suspected_data[entry]), entry, "is not an integer")
                        return False

                # and now rest params that can fail the data system
                if str(entry).find("_amount") != -1:
                    try:
                        suspected_data[entry] = int(suspected_data[entry])
                    except ValueError:
                        print(str(suspected_data[entry]), entry, "is not an integer")
                        return False

                if str(entry) == "SSN_ID":
                    if not str(suspected_data[entry]).isnumeric() and len(str(suspected_data[entry])) != 16:
                        print("SSN_ID should be 16-digit number.")
                        return False

                if str(entry) == "telephone":
                    if not str(suspected_data[entry]).isnumeric() and len(str(suspected_data[entry])) != 11:
                        print("telephone should 11-digit number, starting from 8")
                        return False

                if str(entry) == "date_of_birth":
                    buf = str(suspected_data[entry]).split("-")
                    if len(buf) != 3:
                        print("Date of birth should be in format <dd-mm-yyyy>")
                        return False
                    for num in buf:
                        if not str(num).isnumeric():
                            print("Date of birth should be in format <dd-mm-yyyy>")
                            return False

                if str(entry) == "coordinates":
                    buf = str(suspected_data[entry]).split(" ")
                    if len(buf) != 2:
                        print("coordinates should be 2 numbers")
                        return False
                    try:
                        latitude = float(buf[0])
                        longitude = float(buf[1])
                        if abs(latitude) > 90:
                            print("abs(latitude) shouldn't exceed 90 degrees")
                            return False
                        if abs(longitude) > 180:
                            print("abs(longitude) shouldn't exceed 180 degrees")
                            return False
                    except ValueError:
                        print("coordinates should be Numbers")
                        return False

                if str(entry) == "sex":
                    if str(suspected_data[entry]) not in ['male', 'female', "Male", "Female", "M", "F"]:
                        print(str(suspected_data[entry]), "is not a gender!")
                        return False

                if str(entry) == "salary":
                    try:
                        m_salary = float(str(suspected_data[entry]))
                        if m_salary < 0.0:
                            print("Who pays negative salary?")
                            return False
                    except ValueError:
                        print("salary should be a Number")
                        return False

        if self.spinner_crud.text == "Print" or self.spinner_crud.text == "Remove":
            for entry in suspected_data:
                # cut all empty values
                if suspected_data[entry] != "":
                    # if key reflects list of ids, value should be a list of ints
                    if str(entry).find("_ids") != -1:
                        # cast it to list
                        suspected_data[entry] = str(suspected_data[entry]).split(" ")
                        # check it contains integers only
                        for k in range(len(suspected_data[entry])):
                            try:
                                suspected_data[entry][k] = int(suspected_data[entry][k])
                            except ValueError:
                                print(str(suspected_data[entry][k]), "is not an integer. Check rest List members.")
                                return False
                    # if key is an identifier, value should be integer only
                    elif str(entry).find("_id") != -1:
                        try:
                            suspected_data[entry] = int(suspected_data[entry])
                        except ValueError:
                            print(str(suspected_data[entry]), entry, "is not an integer")
                            return False

                    # and now rest params that can fail the data system
                    if str(entry).find("_amount") != -1:
                        try:
                            suspected_data[entry] = int(suspected_data[entry])
                        except ValueError:
                            print(str(suspected_data[entry]), entry, "is not an integer")
                            return False

                    if str(entry) == "SSN_ID":
                        if not str(suspected_data[entry]).isnumeric() and len(str(suspected_data[entry])) != 16:
                            print("SSN_ID should be 16-digit number.")
                            return False

                    if str(entry) == "telephone":
                        if not str(suspected_data[entry]).isnumeric() and len(str(suspected_data[entry])) != 11:
                            print("telephone should 11-digit number, starting from 8")
                            return False

                    if str(entry) == "date_of_birth":
                        buf = str(suspected_data[entry]).split("-")
                        if len(buf) != 3:
                            print("Date of birth should be in format <dd-mm-yyyy>")
                            return False
                        for num in buf:
                            if not str(num).isnumeric():
                                print("Date of birth should be in format <dd-mm-yyyy>")
                                return False

                    if str(entry) == "coordinates":
                        buf = str(suspected_data[entry]).split(" ")
                        if len(buf) != 2:
                            print("coordinates should be 2 numbers")
                            return False
                        try:
                            latitude = float(buf[0])
                            longitude = float(buf[1])
                            if abs(latitude) > 90:
                                print("abs(latitude) shouldn't exceed 90 degrees")
                                return False
                            if abs(longitude) > 180:
                                print("abs(longitude) shouldn't exceed 180 degrees")
                                return False
                        except ValueError:
                            print("coordinates should be Numbers")
                            return False

                    if str(entry) == "sex":
                        if str(suspected_data[entry]) not in ['male', 'female', "Male", "Female", "M", "F"]:
                            print(str(suspected_data[entry]), "is not a gender!")
                            return False

                    if str(entry) == "salary":
                        try:
                            m_salary = float(str(suspected_data[entry]))
                            if m_salary < 0.0:
                                print("Who pays negative salary?")
                                return False
                        except ValueError:
                            print("salary should be a Number")
                            return False

        return True

    # Responded for executing after Button is pressed ~ Controller
    def confirm_operation(self, instance):
        # Part 0 - form basis for ReQL command. Get all values from TextInputs. Validate these values.
        cmd = self.rdb.db('HMS')
        read_values = [self.list_of_text_inputs[i].text for i in range(0, len(self.list_of_text_inputs) - 1)]

        # Part 1 - choose, what table to work with
        cur_table = self.tables[list(self.tables).index(str(self.spinner_table.text))]
        fields_of_cur_table = self.rdb.db('HMS').table(cur_table).get(0).keys().run(self.conn)
        cmd = cmd.table(cur_table)
        res = str(cmd)

        # Part 2 - choose, what operation to execute,
        # with part 3 - run formed command
        # and part 4 - show result
        cur_cmd = self.spinner_crud.text
        if cur_cmd == self.spinner_crud.values[0]:
            # Add ~ insert. Then, first of all, get new primary key value
            counter = self.rdb.db("HMS").table(self.spinner_table.text).count().run(self.conn)
            insert_data = dict(zip(fields_of_cur_table, read_values[0:len(fields_of_cur_table)]))
            insert_data["primary_id"] = counter + 1
            # Validate everything
            if not self.validate_data(insert_data):
                self.list_of_text_inputs[len(self.list_of_text_inputs) - 1].text = "Incorrect input data!"
                return 0
            # and execute command
            cmd = cmd.insert(insert_data)
            res = cmd.run(self.conn)
            # show result
            print("INSERT:", cmd)
            print("RES:", res)
            self.list_of_text_inputs[len(self.list_of_text_inputs) - 1].text = str(res)

        elif cur_cmd == self.spinner_crud.values[1]:
            # Change ~ update. Not used
            res = "Not realized"
        elif cur_cmd == self.spinner_crud.values[2]:
            # Remove ~ delete. Collect all data
            init_data = dict(zip(fields_of_cur_table, read_values[0:len(fields_of_cur_table)]))
            remove_data = dict()
            # drop empty fields
            for entry in init_data:
                if init_data[entry] != "":
                    remove_data[entry] = init_data[entry]
            init_data.clear()
            # validate data
            if not self.validate_data(remove_data):
                self.list_of_text_inputs[len(self.list_of_text_inputs) - 1].text = "Incorrect input data!"
                return 0
            # execute
            cmd = cmd.filter(remove_data)
            cmd = cmd.delete()
            res = cmd.run(self.conn)
            # show result
            print("DELETE:", cmd)
            print("RES:", res)
            self.list_of_text_inputs[len(self.list_of_text_inputs) - 1].text = str(res)  # cmd

        else:
            # Print ~ get
            # collect all data
            init_data = dict(zip(fields_of_cur_table, read_values[0:len(fields_of_cur_table)]))
            # drop empty fields
            get_data = dict()
            for entry in init_data:
                if init_data[entry] != "":
                    get_data[entry] = init_data[entry]
            init_data.clear()
            # validate rest params
            if not self.validate_data(get_data):
                self.list_of_text_inputs[len(self.list_of_text_inputs) - 1].text = "Incorrect input data!"
                return 0
            # execute command
            cmd = cmd.filter(get_data)
            res = cmd.run(self.conn)
            # show result
            print("GET:", cmd)
            print("RES:", res)
            self.list_of_text_inputs[len(self.list_of_text_inputs) - 1].text = str(list(res))

        return 0

    # Responds for View part
    def build(self):
        # Layout ~ container for widgets
        layout = BoxLayout(orientation='vertical')

        # So, we'll have two Spinners aka selectors
        self.spinner_crud = Spinner(text='Choose operation type',
                                    values=('Add', 'Change', 'Remove', 'Print'),
                                    size=(50, 20))
        self.spinner_table = Spinner(text='Choose table',
                                     values=tuple(self.rdb.db('HMS').table_list().run(self.conn)),
                                     size=(50, 20))
        self.spinner_table.bind(text=self.set_hint_values)

        # Also we'll need 12 text fields, whose value depends on Table_Selector.value, plus result shower
        self.list_of_text_inputs = [TextInput(hint_text=str(i + 1), multiline=False) for i in range(0, 12)]
        self.list_of_text_inputs.append(
            Builder.load_string("""TextInput:
                hint_text: "Result"
                width: 100
                width: self.width""")
        )

        # and, finally, confirming Button
        self.btn_action = Button(text='Confirm')
        self.btn_action.bind(on_press=self.confirm_operation)

        # Now, add all these widgets to layout & return it
        layout.add_widget(self.spinner_crud)
        layout.add_widget(self.spinner_table)
        for i in range(0, len(self.list_of_text_inputs)):
            layout.add_widget(self.list_of_text_inputs[i])
        layout.add_widget(self.btn_action)
        return layout


MainActivity().run()
