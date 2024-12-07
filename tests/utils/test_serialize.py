import unittest

import numpy as np

from aip_trainer.utils.serialize import serialize


test_dict_list_dict = {
    "type": "FeatureCollection",
    "name": "volcanoes",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
    "features": [
        {"type": "Feature", "properties": {"Volcano_Number": 283010, "Volcano_Name": "Izu-Tobu", "prop_none": None},
         "geometry": {"type": "Point", "coordinates": [139.098, 34.9]}},
        {"type": "Feature",
         "properties": {"Volcano_Number": 283020, "Volcano_Name": "Hakoneyama", "ndarray": np.array([1])},
         "geometry": {"type": "Point", "coordinates": [139.021, 35.233]}}
    ]
}


class TestSerialize(unittest.TestCase):
    def test_serialize(self):
        from bson import ObjectId

        # remove keys with values as bson.ObjectId
        d1 = {"_id": ObjectId()}
        self.assertDictEqual(serialize(d1), dict())

        # test: serialize nd.float*, number as key => str
        np_int_4 = np.asarray([87], dtype=np.integer)[0]
        d2 = {"b": np.float32(45.0), 3: 33, 1.56: np_int_4, 3.5: 44.0, "d": "b", "tuple": (1, 2)}
        expected_d2 = {
            'b': 45.0,
            3: 33,
            1.56: 87,
            3.5: 44.0,
            'd': 'b',
            "tuple": [1, 2]
        }
        serialized_d2 = serialize(d2)
        self.assertDictEqual(serialized_d2, expected_d2)

        # # nested dict of list of dict, serialize nd.array
        d3 = {"e": [{"q": 123}, {"q": 456}], "a": np.arange(1.1, 16.88).reshape(4, 4)}
        expected_d3 = {
            "e": [{"q": 123}, {"q": 456}],
            'a': [[1.1, 2.1, 3.1, 4.1], [5.1, 6.1, 7.1, 8.1], [9.1, 10.1, 11.1, 12.1], [13.1, 14.1, 15.1, 16.1]]
        }
        self.assertDictEqual(serialize(d3), expected_d3)

    def test_serialize_dict_exception(self):
        from json import JSONDecodeError

        e = JSONDecodeError(msg="x", doc="what we are?", pos=111)
        exception = serialize({"k": e})
        self.assertDictEqual(
            exception,
            {'k': {'msg': 'x', 'type': "<class 'json.decoder.JSONDecodeError'>", 'doc': 'what we are?', 'pos': 111,
                   'lineno': 1, 'colno': 112}}
        )

    def test_serialize_bytes(self):
        self.assertDictEqual(
            serialize({"k": b"x"}),
            {'k': {'value': 'eA==', 'type': 'bytes'}}
        )

    def test_serialize_dict_list_dict(self):
        serialized_dict_no_none = serialize(test_dict_list_dict, include_none=False)
        self.assertDictEqual(serialized_dict_no_none, {
            'type': 'FeatureCollection',
            'name': 'volcanoes',
            'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}},
            'features': [
                {'type': 'Feature', 'properties': {'Volcano_Number': 283010, 'Volcano_Name': 'Izu-Tobu'},
                 'geometry': {'type': 'Point', 'coordinates': [139.098, 34.9]}},
                {'type': 'Feature',
                 'properties': {'Volcano_Number': 283020, 'Volcano_Name': 'Hakoneyama', 'ndarray': [1]},
                 'geometry': {'type': 'Point', 'coordinates': [139.021, 35.233]}}
            ]
        })

        serialized_dict_wiht_none = serialize(test_dict_list_dict, include_none=True)
        self.assertDictEqual(serialized_dict_wiht_none, {
            'type': 'FeatureCollection',
            'name': 'volcanoes',
            'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}},
            'features': [
                {'type': 'Feature',
                 'properties': {'Volcano_Number': 283010, 'Volcano_Name': 'Izu-Tobu', 'prop_none': None},
                 'geometry': {'type': 'Point', 'coordinates': [139.098, 34.9]}},
                {'type': 'Feature',
                 'properties': {'Volcano_Number': 283020, 'Volcano_Name': 'Hakoneyama', 'ndarray': [1]},
                 'geometry': {'type': 'Point', 'coordinates': [139.021, 35.233]}}
            ]
        })


if __name__ == '__main__':
    unittest.main()
