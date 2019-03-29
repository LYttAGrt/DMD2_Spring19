from rethinkdb import RethinkDB
# import os
from random import randint
import mimesis
from mimesis.enums import Gender

r = RethinkDB()

# TODO for tables who stores coordinate:
#  since geospatial search is required - maybe use index_create(geo=True). Check RethinkDB docs for details
# TODO for stories & forms - check uniqueness of pairs [owner, forms]

# ----------------------------------------------------------------------------------------------------------------------
# part 1: create all tables used. Since all fields of each table should be described - use direct table creation
def create_all_tables(connection):
    # id as PK, name, date_of_birth, sex, qualification, SSN_ID, telephone, home_address, salary
    r.table_create('Doctors', primary_key='doctor_id').run(connection)
    # id as PK, name, date_of_birth, sex, qualification, SSN_ID, telephone, home_address, salary
    r.table_create('Nurses', primary_key='nurse_id').run(connection)
    # id as PK, name, date_of_birth, sex, qualification, SSN_ID, telephone, home_address, salary
    r.table_create('Paramedics', primary_key='nurse_id').run(connection)
    # id as PK, name, date_of_birth, sex, qualification, SSN_ID, telephone, home_address, salary
    r.table_create('Administrators', primary_key='administrator_id').run(connection)
    # id as PK, name, date_of_birth, sex, vacated position, SSN_ID, telephone, home_address, salary
    r.table_create('Stuff', primary_key='stuff_id').run(connection)
    # id as PK, name, date_of_birth, sex, SSN_ID, telephone, home_address, coordinates
    r.table_create('Patients', primary_key='patient_id').run(connection)

    # id as PK, owner, data, next_id
    r.table_create('IllnessHistories', primary_key='history_id').run(connection)
    # id as PK, form_type, doctor_id, patient_id, type_of_procedure (checking, operation),
    # list of additional data as key-value
    r.table_create('IllnessForms', primary_key='form_id').run(connection)

    # id as PK==0, address, coords, director, list of departments
    r.table_create('Hospital').run(connection)
    # id as PK, name, id_of_leader, ids_of_doctors, ids_of_nurses, ids_of_admins, ids_of_stuff, maybe # beds
    r.table_create('Departments').run(connection)
    # id as PK, driver_id, doctor_id, list of paramedic_id, coords
    r.table_create('Ambulances').run(connection)


# ----------------------------------------------------------------------------------------------------------------------
# Part 2: generate all the data.
# So, for realism we want 100*Ne employees and 1000*Np patients
def generate_sample_data(total_employees_amount: int, total_patients_amount: int, conn):
    # first - check arguments
    if total_employees_amount < 0 or total_employees_amount % 10.0 != 0.0:
        return 1
    if total_patients_amount < 0 or total_patients_amount % 100.0 != 0.0:
        return 1

    # mimesis generators will be used because they're really easy. very easy
    # pls read docs on them, it'll take 5 min or even less
    gen_person = mimesis.Person('en')
    date = mimesis.Datetime()
    ssn_id = mimesis.Numbers()
    home_addr = mimesis.Address()
    stuff_jobs = ['janitor', 'cook', 'guard']
    doctors_amount = int(0.25 * total_employees_amount)
    nurses_amount = int(0.35 * total_employees_amount)
    paramedic_amount = int(0.15 * total_employees_amount)
    admins_amount = int(0.15 * total_employees_amount)
    stuff_amount = int(0.10 * total_employees_amount)
    ambulance_amount = int(0.01 * total_employees_amount)

    # add multipliers such as no more than 1 Hospital - partially done
    # add loops - partially done

    # Doctors generator. Doctor types have been taken from Wikipedia - all questions for them
    doctor_types = ['Cardiac surgery', 'Cardiothoracic surgery', 'Colorectal surgery', 'Dental surgery',
                    'Organ transplant|Transplant surgery', 'Upper gastrointestinal surgery', 'Vascular surgery',
                    'Craniofacial surgery', 'Neurological surgery', 'Oral and maxillofacial surgery',
                    'Obstetrics and gynaecology', 'Orthopedic surgery', 'Ophthalmology', 'Otorhinolaryngology',
                    'Pediatric surgery', 'Podiatric_surgery', 'Plastic surgery', 'Surgical oncology',
                    'Trauma surgery', 'Thoracic surgery', 'Urology', 'General Surgery']
    for i in range(doctors_amount):
        r.table('Doctors').insert({
            'doctor_id': i,
            'name': gen_person.full_name(gender=Gender.MALE),
            'date_of_birth': str(date.date(start=1950, end=1995)),
            'sex': 'male',
            'qualification ': doctor_types[randint(0, len(doctor_types) - 1)],
            'SSN_ID': ssn_id.between(minimum=1000000000000000, maximum=10000000000000000 - 1),
            'telephone': ssn_id.between(minimum=89000000000, maximum=89999999999),
            'home_address': home_addr.address(),
            'salary': 12000.00
        }).run(conn)

    # Nurses generator
    for i in range(nurses_amount):
        r.table('Nurses').insert({
            'nurse_id': i,
            'name': gen_person.full_name(gender=Gender.FEMALE),
            'date_of_birth': str(date.date(start=1950, end=1997)),
            'sex': 'female',
            'qualification': 'nurse',
            'SSN_ID': ssn_id.between(minimum=1000000000000000, maximum=10000000000000000 - 1),
            'telephone': ssn_id.between(minimum=89000000000, maximum=89999999999),
            'home_address': home_addr.address(),
            'salary': 27000.00
        }).run(conn)

    # Paramedics generator
    for i in range(paramedic_amount):
        r.table('Paramedics').insert({
            'paramedic_id': i,
            'name': gen_person.full_name(gender=Gender.MALE),
            'date_of_birth': str(date.date(start=1980, end=2000)),
            'sex': 'male',
            'qualification': 'ambulance paramedic',
            'SSN_ID': ssn_id.between(minimum=1000000000000000, maximum=10000000000000000 - 1),
            'telephone': ssn_id.between(minimum=89000000000, maximum=89999999999),
            'home_address': home_addr.address(),
            'salary': 16600.00
        }).run(conn)

    # Administrators generator
    admins_types=['Dean of the Hospital', 'Hospital Administrator', 'Head of Surgeons and Doctors Department',
                  'Head of Nursing Department', 'Head of Emergency Department', 'Head of Recruitment Department',
                  'Head of Medicine Department', 'Head of Equipment Department', 'Head of Security Department',
                  'Medical Student Administration', 'Inventory Head']
    for i in range(admins_amount):
        r.table('Administrators').insert({
            'administrator_id': i,
            'name': gen_person.full_name(gender=Gender.FEMALE),
            'date_of_birth': str(date.date(start=1970, end=1990)),
            'sex': 'male',
            'qualification': admins_types[randint(0, len(admins_types) - 1)],
            'SSN_ID': ssn_id.between(minimum=1000000000000000, maximum=10000000000000000 - 1),
            'telephone': ssn_id.between(minimum=89000000000, maximum=89999999999),
            'home_address': home_addr.address(),
            'salary': 0.00
        }).run(conn)

    # Stuff generator
    for i in range(stuff_amount):
        r.table('Stuff').insert({
            'stuff_id': i,
            'name': gen_person.full_name(gender=Gender.FEMALE),
            'date_of_birth': str(date.date(start=1950, end=2000)),
            'sex': 'female',
            'vacated_position': stuff_jobs[randint(0, len(stuff_jobs) - 1)],
            'SSN_ID': ssn_id.between(minimum=1000000000000000, maximum=10000000000000000 - 1),
            'telephone': ssn_id.between(minimum=89000000000, maximum=89999999999),
            'home_address': home_addr.address(),
            'salary': 8800.00
        }).run(conn)

    for i in range(total_patients_amount):
        coin = randint(0, 1)
        if coin == 1:
            gender = Gender.MALE
        else:
            gender = Gender.FEMALE
        r.table('Patients').insert({
            'patient_id': i,
            'name': gen_person.full_name(gender=gender),
            'date_of_birth': str(date.date(start=1935, end=2015)),
            'sex': str(gender.value),
            'SSN_ID': ssn_id.between(minimum=1000000000000000, maximum=10000000000000000 - 1),
            'telephone': ssn_id.between(minimum=89000000000, maximum=89999999999),
            'home_address': home_addr.address(),
            'coordinates': {float(randint(10000, 300000) / 100), float(randint(10000, 300000) / 100)},
            'illness_history_head_id': i
        }).run(conn)


    # Let's link a little illness histories with their owners.
    # Also, by analogue of extended books, next_ids can be used
    for i in range(total_patients_amount):
        r.table('IllnessHistories').insert({
            'history_id': i,
            'owner_id': i,
            'forms_ids': [],
            'next_id': ''
        }).run(conn)

    # for this table - maybe generate different types of forms
    form_types=['069-uf', '322-es', '183-op', '013-dt']
    for i in range(3 * total_patients_amount):
        patient_id = randint(0, total_patients_amount - 1)
        procedure_types = ['bone removing', 'bone updating', 'bone inserting', 'bone growing']
        r.table('IllnessForms').insert({
            'form_id': i,
            'form_type': form_types[randint(0, len(form_types) - 1)],
            'doctor_id': randint(0, doctors_amount - 1),
            'patient_id': patient_id,
            'procedure_type': procedure_types[randint(0, len(procedure_types) -1)],
            'additional_information': {
                # so, form data by itself should be stored here
                'operation_type': '',
                'result': 'success'
            }
        }).run(conn)
        a = r.table('IllnessHistories').get(patient_id)['forms_ids'].append(i).run(conn)
        r.table('IllnessHistories').filter(r.row['owner_id'] == patient_id).update({'forms_ids': a}).run(conn)

    # Hospital generator
    r.table('Hospital').insert({
        'hospital_id': 0,
        'address': home_addr.address(),
        'coordinates': {0.00, 0.00},
        'director': 'wanted',
        'departments': doctor_types
    }).run(conn)

    # Departments generator
    for i in range(len(doctor_types)):
        r.table('Departments').insert({
            'department_id': i,
            'name': doctor_types[i],
            'leader_id': total_employees_amount,
            'doctors_ids': [total_employees_amount],
            'nurses_ids': [total_employees_amount],
            'administrators_ids': [total_employees_amount],
            'stuff_ids': [total_employees_amount],
            'beds': randint(15, 50)
        }).run(conn)

    # Ambulance generator
    for i in range(ambulance_amount):
        r.table('Ambulances').insert({
            'ambulance_id': i,
            'driver_id': 'wanted',
            'doctor_id': 'wanted',
            'paramedic_ids': ['wanted'],
            'coords': {0.00, 0.00}
        }).run(conn)

    return 0


# if something goes wrong or clear DB needed - let's brutally drop all tables
def clear_db(connection):
    db_list = r.db_list().run(connection)
    if db_list:
        r.db_drop('HMS').run(connection)
        print('Database HMS dropped.')
        r.db_create('HMS').run(connection)
    else:
        r.db_create('HMS').run(connection)
    return 0


# before the start - set up RebirthDB via shell
# TODO: automatize it
# so, let's make it more efficient by making a function from script
def generate_new_data():
    # Set up the DBMS via system call
    # syscall_res = os.system('rebirthdb')
    # if syscall_res:
    #     print("Please check RebirthDB or install it from \n https://github.com/floydkots/rebirthdb")
    #     return 0
    # print('DBMS launched.')

    # connect our DB
    conn = r.connect(db="HMS")
    print('Connection installed.')

    # point 0: clear the DB
    clear_db(connection=conn)
    print('DB cleared.')

    # point 1: create all usable tables *if they do not exist*
    create_all_tables(connection=conn)
    print('All tables set up.')

    # point 2: fill up these tables *according to some half-randomized aggregation*
    generate_sample_data(total_employees_amount=20, total_patients_amount=100, conn=conn)
    print('Sample data generated.')

    return 0


generate_new_data()


