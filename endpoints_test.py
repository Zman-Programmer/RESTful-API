import unittest
import httplib2

address = 'http://localhost:5000'


class TestStringMethods(unittest.TestCase):

    def test_valid_id(self):
        url = address + '/api/users/1'
        h = httplib2.Http()
        resp, result = h.request(url, 'GET')
        self.assertEqual(resp['status'], '200')

    def test_invalid_id(self):
        url = address + '/api/users/100000000'
        h = httplib2.Http()
        resp, result = h.request(url, 'GET')
        self.assertEqual(resp['status'], '500')


if __name__ == '__main__':
    unittest.main()
