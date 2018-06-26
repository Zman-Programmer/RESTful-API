import unittest
from httplib2 import Http
import json

address = 'http://localhost:5000'


class TestStringMethods(unittest.TestCase):

    # tests the basic connection with the API and redis server, if not set up incorrectly
    def test_connection(self):
        h = Http()
        resp, result = h.request(address, 'GET')
        self.assertEqual(resp['status'], '200')

    # test adding a new user, could fail if the user already exists
    def test_add_new_user(self):
        h = Http()
        url = address + '/api/users'
        data = dict(username="unit_test", password="unit_test")
        data = json.dumps(data)
        resp, result = h.request(url, 'POST', body=data, headers={"Content-Type": "application/json"})
        self.assertEqual(resp['status'], '201')

    # tests authentication resource and token
    def test_authentication(self):
        url = address + '/token'
        h = Http()
        h.add_credentials('unit_test', 'unit_test')
        resp, result = h.request(url, 'POST', headers={"Content-Type": "application/json"})
        self.assertEqual(resp['status'], '200')

    # test adding a new resource
    # curl -u user1:pass1 -i -H "Content-Type: application/json" -X POST -d '{"versionNumber":"2.0.0", "nameUpdate":"Version 2", "newFeatures":"None", "bugFixes":"None"}' http://127.0.0.1:5000/version
    def test_add_new_update(self):
        url = address + '/version'
        h = Http()
        h.add_credentials('unit_test', 'unit_test')
        data = dict(versionNumber="3.0.0", nameUpdate="Version 3", newFeatures="None", bugFixes="None")
        data = json.dumps(data)
        resp, result = h.request(url, 'POST', body=data, headers={"Content-Type": "application/json"})
        self.assertEqual(resp['status'], '200')

    # tests to see if we can access users
    def test_valid_id(self):
        url = address + '/api/users/1'
        h = Http()
        resp, result = h.request(url, 'GET')
        self.assertEqual(resp['status'], '200')

    # tests to see if the API throws a error in the case of invalid user id
    def test_invalid_id(self):
        url = address + '/api/users/100000000'
        h = Http()
        resp, result = h.request(url, 'GET')
        self.assertEqual(resp['status'], '500')

    # test to see if we can access the resource without credentials
    def test_access_without_credentials(self):
        url = address + '/version'
        h = Http()
        resp, result = h.request(url, 'GET')
        self.assertEqual(resp['status'], '401')

    # test to see if we can access the resource with the credentials
    def test_access_with_credentials(self):
        url = address + '/version'
        h = Http()
        h.add_credentials('unit_test', 'unit_test')
        resp, result = h.request(url, 'GET')
        self.assertEqual(resp['status'], '200')

if __name__ == '__main__':
    unittest.main()
