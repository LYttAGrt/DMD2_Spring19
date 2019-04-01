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

# TODO: run DBMS in thread; launch sample data generator (maybe)
# TODO: add fool protection s.a. empty fields & usage of _id field
# TODO: add UPDATE, DELETE ops. For UPDATE - insert actual values as hint_texts
# TODO: use Builder & choose optimal layout


class MainActivity(App):
    # Set up connection in the very beginning, cache some useful data
    rdb = RethinkDB()
    conn = rdb.connect(db='HMS')
    tables = rdb.db('HMS').table_list().run(conn)

    # Puts the values that should be used: F(str, int) -> str
    def set_hint_value(self, instance, x):
        # get all necessary indices
        indices = self.rdb.db('HMS').table(self.spinner_table.text).get(0).keys().run(self.conn)
        # set all hint_texts
        for i in range(len(indices)):
            self.list_of_text_inputs[i].hint_text = indices[i]
            if self.list_of_text_inputs[i].disabled:
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
        return 0

    # Responded for executing after Button is pressed
    def button_callback(self, instance):
        # Part 0 - form basis for ReQL command. Get all values from TextInputs
        cmd = self.rdb.db('HMS')
        read_values = list()
        for i in range(0, 9):
            read_values.append(self.list_of_text_inputs[i].text)
        print(cmd, read_values)

        # Part 1 - choose, what table to work with
        cur_table = self.tables[list(self.tables).index(str(self.spinner_table.text))]
        cmd = cmd.table(cur_table)
        print(cur_table, cmd)

        # Part 2 - choose, what operation to execute
        cur_cmd = self.spinner_crud.text
        if cur_cmd == self.spinner_crud.values[0]:
            # Add ~ insert
            fields_of_cur_table = self.rdb.db('HMS').table(cur_table).get(0).keys().run(self.conn)
            insert_data = dict(zip(fields_of_cur_table, read_values[0:len(fields_of_cur_table)]))
            cmd = cmd.insert(insert_data)
        elif cur_cmd == self.spinner_crud.values[1]:
            # Change ~ update
            print("UPDATE:", cmd)
        elif cur_cmd == self.spinner_crud.values[3]:
            # Remove ~ delete
            print("DELETE:", cmd)
        else:
            # Print ~ get
            read_id = self.list_of_text_inputs[0].text
            cmd = cmd.get(read_id)
        # Part 3 - run formed command
        # res = cmd.run(conn)

        # Part 4 - put the result
        print(cmd)
        self.list_of_text_inputs[9].text = str(cmd) # res
        return 0

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
        self.spinner_table.bind(text=self.set_hint_value)

        # Also we'll need 9 text fields, whose value depends on Table_Selector.value, plus result shower
        self.list_of_text_inputs = [TextInput(hint_text=str(i + 1), multiline=False) for i in range(0, 9)]
        self.list_of_text_inputs.append(TextInput(hint_text='Result'))

        # and, finally, confirming Button
        self.btn_action = Button(text='Confirm')
        self.btn_action.bind(on_press=self.button_callback)

        # Now, add all these widgets to layout & return it
        layout.add_widget(self.spinner_crud)
        layout.add_widget(self.spinner_table)
        for i in range(0, len(self.list_of_text_inputs)):
            layout.add_widget(self.list_of_text_inputs[i])
        layout.add_widget(self.btn_action)
        return layout


MainActivity().run()
