from pprint import pprint
from random import randint
from bokeh import colors
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(db="HMS")


# Our geospatial search is defined as a distance between Patients and Ambulances
# def get_nearest(point: dict, table: list, n: int):
#     from math import sqrt
#     distances = list()
#     for element in table:
#         # get coords
#         point_coords = point["coordinates"]["coordinates"]
#         elem_coords = element["coordinates"]["coordinates"]
#         # calculate the distance
#         distance = (point_coords[0] - elem_coords[0]) * (point_coords[0] - elem_coords[0])
#         distance += (point_coords[1] - elem_coords[1]) * (point_coords[1] - elem_coords[1])
#         distance = sqrt(distance)
#         # insert pair <id, distance>
#         distances.append([element["primary_id"], distance])
#     distances.sort(key=lambda unit: unit[0])
#     return distances[:n]

#res_list = get_nearest(patient, list(ambulances), 1)
#print(res_list)

# 1st geospatial search example: some randomly picked patient needs to be mobilized

patients_amount = r.db("HMS").table("Patients").count().run(conn)
patient = r.db("HMS").table("Patients").get(randint(0, patients_amount)).run(conn)
pprint(patient)
coords = patient["coordinates"]["coordinates"]
patient_point = r.point(coords[0], coords[1])
pprint(r.db("HMS").table("Ambulances").get_nearest(patient_point, index='coordinates', max_results=2, unit='km').run(conn))

# colors.Color.from_rgb()

#INSERT ONE ENTRY
r.db("HMS").table("Ambulances").insert({
    'primary_id': 77,
    'driver_id': 50,
    'doctor_id': 36,
    'paramedic_ids': [55, 73, 125],
    'coordinates': r.point(55.752258, 48.744576),
    'additional_data': {"the fastest ambulance in hospital"}
        }).run(conn)
pprint(r.db("HMS").table("Ambulances").run(conn))


#INSERT MULTIPLE ENTRIES
patient_id = 10000
illness_history_id = 10001
form_id_1 = 10002
form_id_2 = 10003
doctor_id = 10004


r.db("HMS").table("Patients").insert({
    'primary_id': patient_id,
    'login': 'john.terry',
    'password': 'password12',
    'name': 'John Terry',
    'date_of_birth': '1980',
    'sex': 'male',
    'SSN_ID': 4735501961098410,
    'telephone': 88005553535,
    'home_address': "Innopolis, Universitetskaya, 1, 306",
    'coordinates': r.point(55.43423, 47.76545),
    'illness_history_head_id': illness_history_id,
    'additional_data': {"problem patient"}
}, return_changes=True).run(conn)
pprint(r.db("HMS").table("Patients").filter({'name': 'John Terry'}).run(conn))


r.db("HMS").table("IllnessHistories").insert({
            'primary_id': illness_history_id,
            'owner_id': patient_id,
            'forms_ids': [form_id_1, form_id_2],
            'next_id': '',
            'additional_data': {"history of problem patient"}
        }).run(conn)
pprint(r.db("HMS").table("IllnessHistories").filter({'owner_id': patient_id}).run(conn))


r.db("HMS").table('IllnessForms').insert([{
                'primary_id': form_id_1,
                'form_type': "069-uf",
                'doctor_id': doctor_id,
                'patient_id': patient_id,
                'procedure_type': "bandaging",
                'additional_data': {
                    'operation_type': 'operation on right arm',
                    'result': 'success'
                }
            },
            {
                'primary_id': form_id_2,
                'form_type': "183-op",
                'doctor_id': doctor_id + 1,
                'patient_id': patient_id,
                'procedure_type': "electrodiagnostics",
                'additional_data': {
                    'operation_type': 'operation on left arm',
                    'result': 'success'
                }
            }]
).run(conn)
pprint(r.db("HMS").table("IllnessForms").filter({'patient_id' : patient_id}).run(conn))
