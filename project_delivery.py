from random import randint

from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect(db="HMS")


# Our geospatial search is defined as a distance between Patients and Ambulances
def get_nearest(point: dict, table: list, n: int):
    from math import sqrt
    distances = list()
    for element in table:
        # get coords
        point_coords = point["coordinates"]["coordinates"]
        elem_coords = element["coordinates"]["coordinates"]
        # calculate the distance
        distance = (point_coords[0] - elem_coords[0]) * (point_coords[0] - elem_coords[0])
        distance += (point_coords[1] - elem_coords[1]) * (point_coords[1] - elem_coords[1])
        distance = sqrt(distance)
        # insert pair <id, distance>
        distances.append([element["primary_id"], distance])
    distances.sort(key=lambda unit: unit[0])
    return distances[:n]


# 1st geospatial search example: some randomly picked patient needs to be mobilized
patients_amount = r.db("HMS").table("Patients").count().run(conn)
patient = r.db("HMS").table("Patients").get(randint(0, patients_amount)).run(conn)

ambulances_amount = r.db("HMS").table("Ambulances").count().run(conn)
ambulances = r.db("HMS").table("Ambulances").run(conn)

res_list = get_nearest(patient, list(ambulances), 1)
print(res_list)

# following doesn't work. no idea why
#
# patients_amount = r.db("HMS").table("Patients").count().run(conn)
# patient = r.db("HMS").table("Patients").get(randint(0, patients_amount)).run(conn)
# coords = patient["coordinates"]["coordinates"]
# patient_point = r.point(coords[0], coords[1])
# r.db("HMS").table("Ambulances").get_nearest(patient_point, index='coordinates', max_results=2).run(conn)
