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
# from kivy.lang import Builder

# check kivy-version is correct
kivy.require('1.10.1')


# TODO: finish GET ops via filtering the data


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
            for i in range(len(indices), len(self.list_of_text_inputs) - 1):
                self.list_of_text_inputs[i].hint_text = "Not used"
                self.list_of_text_inputs[i].disabled = True
                self.list_of_text_inputs[i].text = ""

        return True

    # Checks if values have correct types. Doesn't fix incorrect values.
    # suspected_data: dictionary of pairs (index as field name, value of field)
    def validate_data(self, suspected_data: dict):
        if self.spinner_crud.text == "Add":
            for entry in suspected_data:
                # if key reflects list of ids, value should be a list of ints
                if str(entry).find("_ids") != -1:
                    # check if it's a list
                    if type(suspected_data[entry]) != list:
                        print(suspected_data[entry], "is not a list.")
                        return False
                    # check it contains integers only
                    for k in range(len(suspected_data[entry])):
                        try:
                            suspected_data[entry][k] = int(suspected_data[entry][k])
                        except ValueError:
                            print(str(suspected_data[entry][k]), "is not an integer. Check rest List members.")
                            return False

                # if key is an identifier, value should be integer only
                if str(entry).find("_id") != -1:
                    if type(suspected_data[entry]) != int:
                        print(str(suspected_data[entry], "is not an integer"))
                        return False

                # and now rest params that can fail the data system
                if str(entry).find("_amount") == -1:
                    if type(suspected_data[entry]) != int:
                        print(str(suspected_data[entry], "is not an integer"))
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
                    if len(suspected_data[entry] != 2):
                        print("coordinates should be 2 numbers")
                        return False
                    try:
                        latitude = float(suspected_data[entry][0])
                        longtitude = float(suspected_data[entry][1])
                        if abs(latitude) > 90:
                            print("abs(latitude) shouldn't exceed 90 degrees")
                            return False
                        if abs(longtitude) > 180:
                            print("abs(longtitude) shouldn't exceed 180 degrees")
                            return False
                    except ValueError:
                        print("coordinates should be Numbers")
                        return False

                if str(entry) == "sex":
                    if str(suspected_data[entry]) not in ['male', 'female']:
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
                    # we'll filter by one value OR between two values
                    buffer_entry = str(suspected_data[entry]).split(' ')
                    for c in range(len(buffer_entry)):
                        # if key reflects list of ids, value should be a list of ints
                        if str(buffer_entry[c]).find("_ids") != -1:
                            # check if it's a list
                            if type(suspected_data[buffer_entry[c]]) != list:
                                print(suspected_data[buffer_entry[c]], "is not a list.")
                                return False
                            # check it contains integers only
                            for k in range(len(suspected_data[buffer_entry[c]])):
                                try:
                                    suspected_data[buffer_entry[c]][k] = int(suspected_data[buffer_entry[c]][k])
                                except ValueError:
                                    print(str(suspected_data[buffer_entry[c]][k]),
                                          "is not an integer. Check rest List members.")
                                    return False

                        # if key is an identifier, value should be integer only
                        if str(buffer_entry[c]).find("_id") != -1:
                            if type(suspected_data[buffer_entry[c]]) != int:
                                print(str(suspected_data[buffer_entry[c]], "is not an integer"))
                                return False

                        # and now rest params that can fail the data system
                        if str(buffer_entry[c]).find("_amount") == -1:
                            if type(suspected_data[buffer_entry[c]]) != int:
                                print(str(suspected_data[buffer_entry[c]], "is not an integer"))
                                return False

                        if str(buffer_entry[c]) == "SSN_ID":
                            if not str(suspected_data[buffer_entry[c]]).isnumeric() and len(
                                    str(suspected_data[buffer_entry[c]])) != 16:
                                print("SSN_ID should be 16-digit number.")
                                return False

                        if str(buffer_entry[c]) == "telephone":
                            if not str(suspected_data[buffer_entry[c]]).isnumeric() and len(
                                    str(suspected_data[buffer_entry[c]])) != 11:
                                print("telephone should 11-digit number, starting from 8")
                                return False

                        if str(buffer_entry[c]) == "date_of_birth":
                            buf = str(suspected_data[buffer_entry[c]]).split("-")
                            if len(buf) != 3:
                                print("Date of birth should be in format <dd-mm-yyyy>")
                                return False
                            for num in buf:
                                if not str(num).isnumeric():
                                    print("Date of birth should be in format <dd-mm-yyyy>")
                                    return False

                        if str(buffer_entry[c]) == "coordinates":
                            if len(suspected_data[buffer_entry[c]] != 2):
                                print("coordinates should be 2 numbers")
                                return False
                            try:
                                latitude = float(suspected_data[buffer_entry[c]][0])
                                longtitude = float(suspected_data[buffer_entry[c]][1])
                                if abs(latitude) > 90:
                                    print("abs(latitude) shouldn't exceed 90 degrees")
                                    return False
                                if abs(longtitude) > 180:
                                    print("abs(longtitude) shouldn't exceed 180 degrees")
                                    return False
                            except ValueError:
                                print("coordinates should be Numbers")
                                return False

                        if str(buffer_entry[c]) == "sex":
                            if str(suspected_data[buffer_entry[c]]) not in ['male', 'female']:
                                print(str(suspected_data[buffer_entry[c]]), "is not a gender!")
                                return False

                        if str(buffer_entry[c]) == "salary":
                            try:
                                m_salary = float(str(suspected_data[buffer_entry[c]]))
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
        read_values = [self.list_of_text_inputs[i].text for i in range(0, 9)]

        # Part 1 - choose, what table to work with
        cur_table = self.tables[list(self.tables).index(str(self.spinner_table.text))]
        fields_of_cur_table = self.rdb.db('HMS').table(cur_table).get(0).keys().run(self.conn)
        cmd = cmd.table(cur_table)
        res = str(cmd)

        # Part 2 - choose, what operation to execute, with part 3 - run formed command
        cur_cmd = self.spinner_crud.text
        if cur_cmd == self.spinner_crud.values[0]:
            # Add ~ insert
            insert_data = dict(zip(fields_of_cur_table, read_values[0:len(fields_of_cur_table)]))
            if not self.validate_data(insert_data):
                self.list_of_text_inputs[len(self.list_of_text_inputs) - 1].text = "Incorrect input data!"
                return 0
            cmd = cmd.insert(insert_data)
            res = cmd.run(self.conn)
        elif cur_cmd == self.spinner_crud.values[1]:
            # Change ~ update. Not used
            res = "Not realized"
        elif cur_cmd == self.spinner_crud.values[3]:
            # Remove ~ delete
            remove_data = dict(zip(fields_of_cur_table, read_values[0:len(fields_of_cur_table)]))
            if not self.validate_data(remove_data):
                res = cmd.run(self.conn)
            print("DELETE:", cmd)
        else:
            # Print ~ get
            # get_data = dict(zip(fields_of_cur_table, read_values[0:len(fields_of_cur_table)]))
            # self.validate_data(get_data)
            # res = cmd.run(self.conn)
            print("GET:", cmd)

        # Part 4 - put the result in result text_input
        self.list_of_text_inputs[len(self.list_of_text_inputs) - 1].text = str(res)  # cmd

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

        # Also we'll need 9 text fields, whose value depends on Table_Selector.value, plus result shower
        self.list_of_text_inputs = [TextInput(hint_text=str(i + 1), multiline=False) for i in range(0, 9)]
        self.list_of_text_inputs.append(TextInput(hint_text='Result'))

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
