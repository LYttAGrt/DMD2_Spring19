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

# Builder shall be used to markup all widgets
# from kivy.lang import Builder

# check version is correct
kivy.require('1.10.1')


# TODO: add INSERT, GET ops. For GET - insert actual values as hint_texts     set_hint_values() & confirm_ops()
# TODO: add fool protection s.a. empty fields & usage of _id field            validate_data()
# TODO: use Builder & choose optimal layout                                   build()


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
                self.list_of_text_inputs[i].hint_text = "Type addable value of candidate's " + str(indices[i])
                self.list_of_text_inputs[i].disabled = False
                try:
                    if str(self.list_of_text_inputs[i].text).index("_id") > 0:
                        self.list_of_text_inputs[i].text = "Service field"
                        self.list_of_text_inputs[i].disabled = True
                except ValueError:
                    continue
            for i in range(len(indices), len(self.list_of_text_inputs) - 1):
                self.list_of_text_inputs[i].hint_text = "Not used"
                self.list_of_text_inputs[i].disabled = True

        if ops_type == 'Change':
            # we don't realize this feature
            for i in range(len(self.list_of_text_inputs)):
                self.list_of_text_inputs[i].hint_text = "Feature is unavailable"
                self.list_of_text_inputs[i].disabled = True

        if ops_type == 'Remove':
            # then we use our text_inputs as filters
            pass

        if ops_type == 'Print':
            # then we use our text_inputs as filters
            pass

        return 0

    # Checks if values have correct types. Fixes them if necessary
    # suspected_data is wanted as a dictionary of pairs field-value
    def validate_data(self, suspected_data: dict):
        validated_data = dict.fromkeys(suspected_data.keys())
        return validated_data

    # Responded for executing after Button is pressed ~ Controller
    def confirm_operation(self, instance):
        # Part 0 - form basis for ReQL command. Get all values from TextInputs. Validate these values.
        cmd = self.rdb.db('HMS')
        read_values = [self.list_of_text_inputs[i].text for i in range(0, 9)]

        # Part 1 - choose, what table to work with
        cur_table = self.tables[list(self.tables).index(str(self.spinner_table.text))]
        cmd = cmd.table(cur_table)

        # Part 2 - choose, what operation to execute, with part 3 - run formed command
        cur_cmd = self.spinner_crud.text
        if cur_cmd == self.spinner_crud.values[0]:
            # Add ~ insert
            fields_of_cur_table = self.rdb.db('HMS').table(cur_table).get(0).keys().run(self.conn)
            insert_data = dict(zip(fields_of_cur_table, read_values[0:len(fields_of_cur_table)]))
            cmd = cmd.insert(self.validate_data(insert_data))
            res = cmd.run(self.conn)
        elif cur_cmd == self.spinner_crud.values[1]:
            # Change ~ update. Not used
            res = "Not realized"
        elif cur_cmd == self.spinner_crud.values[3]:
            # Remove ~ delete
            remove_data = dict()
            self.validate_data(remove_data)
            res = cmd.run(self.conn)
            print("DELETE:", cmd)
        else:
            # Print ~ get
            get_data = dict()
            self.validate_data(get_data)
            res = cmd.run(self.conn)
            print("GET:", cmd)

        # Part 4 - put the result in result text_input
        self.list_of_text_inputs[9].text = str(res)  # cmd

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
