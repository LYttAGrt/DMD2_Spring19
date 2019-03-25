import rethinkdb as r

connection = r.connect(db="HMS")


# ----------------------------------------------------------------------------------------------------------------------
# part 1: create all tables used
def create_all_tables(conn):
    # id, name, birthdate, sex, qualification, SSN_ID, telephone, home address, salary
    r.table_create('Doctors').run(conn)
    # id, name, birthdate, sex, qualification, SSN_ID, telephone, home address, salary
    r.table_create('Nurses').run(conn)
    # id, name, birthdate, sex, qualification, SSN_ID, telephone, home address, salary
    r.table_create('Paramedics').run(conn)
    # id, name, birthdate, sex, qualification, SSN_ID, telephone, home address, salary
    r.table_create('Administrators').run(conn)
    # id, name, birthdate, sex, vacated position, SSN_ID, telephone, home address, salary
    r.table_create('Stuff').run(conn)
    # id, name, birthdate, sex, SSN_ID, telephone, home address, coordinates
    r.table_create('Patients').run(conn)

    # id, owner, data, next_id
    r.table_create('IllnessHistories').run(conn)
    # id, form_type, doctor_id, patient_id, type_of_procedure (checking, operation),
    # list of additional data as key-value
    r.table_create('IllnessForms').run(conn)

    # id==0, address, coords, director, list of departments
    r.table_create('Hospital').run(conn)
    # id, name, id_of_leader, ids_of_doctors, ids_of_nurses, ids_of_admins, ids_of_stuff, maybe # beds
    r.table_create('Departments').run(conn)
    # id, driver_id, doctor_id, list of paramedic_id, coords
    r.table_create('Ambulances').run(conn)


# ----------------------------------------------------------------------------------------------------------------------
# part 2. generate all the data
def generate_sample_data(base_coefficient: int, conn):
    if base_coefficient < 0:
        return
    else:
        # add multipliers such as no more than 1 Hospital
        # add loops
        r.table('Doctors').insert({
            'doctor_id': base_coefficient,
            'name': 'D.A. Kochan',
            'birthdate': '01-07-1999',
            'sex': 'male',
            'qualification ': 'Heart surgeon',
            'SSN_ID': '7452 0014 7485 9654',
            'telephone': 'blue',
            'home_address': 'Pushkina, 69',
            'salary': 12000.00
        }).run(conn)
        r.table('Nurses').insert({
            'nurse_id': base_coefficient,
            'name': 'A. O. Gilfanova',
            'birthdate': '13-09-1991',
            'sex': 'female',
            'qualification': 'senior nurse',
            'SSN_ID': '1799 4567 4532 8975',
            'telephone': '88005553535',
            'home_address': 'Nazarbaeva, 1',
            'salary': 27000.00
        }).run(conn)
        r.table('Paramedics').insert({
            'paramedic_id': base_coefficient,
            'name': 'M. I. Izmaylov',
            'birthdate': '13-09-1987',
            'sex': 'male',
            'qualification': 'ambulance paramedic',
            'SSN_ID': '7974 5245 2867 8605',
            'telephone': '89535767669',
            'home_address': 'Nursultana, 29',
            'salary': 16600.00
        }).run(conn)
        r.table('Administrators').insert({
            'administrators_id': base_coefficient,
            'name': 'M. V. Baliner',
            'birthdate': '08-03-1999',
            'sex': 'male',
            'qualification': 'intern',
            'SSN_ID': '4796 4512 4652 4754',
            'telephone': '85246324005',
            'home_address': 'Smazchikov, 3',
            'salary': 0.00
        }).run(conn)
        r.table('Stuff').insert({
            'stuff_id': base_coefficient,
            'name': 'O. G. Zaharova',
            'birthdate': '17-11-1971',
            'sex': 'female',
            'vacated_position': 'janitor',
            'SSN_ID': '4796 4512 8456 7887',
            'telephone': '85986557489',
            'home_address': 'Frontovykh Brigad, 71',
            'salary': 8800.00
        }).run(conn)
        r.table('Patients').insert({
            'patient_id': base_coefficient,
            'name': 'D. I. Ed',
            'birthdate': '15-10-1995',
            'sex': 'male',
            'SSN_ID': '6274 6579 8487 5642',
            'telephone': '89222255737',
            'home_address': 'Sovietskaya, 22',
            'coordinates': {1670.04, 542.50}
        }).run(conn)
        r.table('IllnessHistories').insert({
            'history_id': base_coefficient,
            'owner_id': base_coefficient,
            'data': {},
            'next_id': ''
        }).run(conn)
        # for this table - maybe generate different types of forms
        r.table('IllnessForms').insert({
            'form_id': base_coefficient,
            'form_type': '069-uf',
            'doctor_id': base_coefficient,
            'patient_id': base_coefficient,
            'procedure_type': 'operation',
            'additional_information': {
                'operation_type': 'bone marrow transplant',
                'result': 'success'
            }
        }).run(conn)
        r.table('Hospital').insert({
            'hospital_id': base_coefficient,
            'address': 'Volgogradskaya, 174',
            'coordintes': {0.00, 0.00},
            'director': 'wanted',
            'departments': ['Cardiosurgery', 'Surgery']
        }).run(conn)
        r.table('Departments').insert({
            'department_id': base_coefficient,
            'name': 'Cardiosurgery',
            'leader_id': base_coefficient,
            'doctors_ids': [base_coefficient],
            'nurses_ids': [base_coefficient],
            'administrators_ids': [base_coefficient],
            'stuff_ids': [base_coefficient],
            'beds': 3
        }).run(conn)
        r.table('Ambulances').insert({
            'ambulance': base_coefficient,
            'drived_id': 'wanted',
            'doctor_id': 'wanted',
            'paramedic_ids': ['wanted'],
            'coords': {0.00, 0.00}
        }).run(conn)
        return 0


create_all_tables(connection)
generate_sample_data(1, connection)
