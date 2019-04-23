from pprint import pprint
from random import randint

from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(db="HMS")

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

# res_list = get_nearest(patient, list(ambulances), 1)
# print(res_list)


# Our geospatial search is defined as a distance between Patients and Ambulances
# Then, 1st example shows N nearest ambulances to the randomly picked patient
patients_amount = r.db("HMS").table("Patients").count().run(conn)
patient = r.db("HMS").table("Patients").get(randint(0, patients_amount - 1)).run(conn)
coords = patient["coordinates"]["coordinates"]
patient_point = r.point(coords[0], coords[1])

print(patient)
pprint(r.db("HMS").table("Ambulances").
       get_nearest(patient_point, index='coordinates', max_results=2, unit='km').run(conn))

# Let's use the same function in the opposite way
# 2nd query is to get N potentially close-located patients for certain ambulance
ambulances = r.db("HMS").table("Ambulances").count().run(conn)
ambulance = r.db("HMS").table("Ambulances").get(randint(0, ambulances - 1)).run(conn)
point = r.point(ambulance["coordinates"]["coordinates"][0], ambulance["coordinates"]["coordinates"][1])

print(ambulance)
pprint(r.db("HMS").table("Patients").
       get_nearest(point, index='coordinates', max_results=100, unit='km').run(conn)
       )
