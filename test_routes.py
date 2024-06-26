import unittest
import app

class TestAppRoutes(unittest.TestCase):

    def setUp(self):
        self.app = app.main()
        self.app.testing = True

    def test_process_receipt(self):
        # Mock data for POST request
        mock_data = {
            "retailer": "Example Store",
            "purchaseDate": "2023-06-25",
            "purchaseTime": "13:30",
            "items": [
                {
                    "shortDescription": "Item 1",
                    "price": "10.99"
                },
                {
                    "shortDescription": "Item 2",
                    "price": "5.49"
                }
            ],
            "total": "16.48"
        }

        # Send POST request to /receipts/process
        response = self.app.post('/receipts/process', json=mock_data)
        data = response.get_json()

        # Assert status code and 'id' in response
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', data)

        # Verify receipt was added to 'receipts' dictionary
        receipt_id = data['id']
        self.assertIn(receipt_id, receipts)

    def test_get_points(self):
        # Add a mock receipt to 'receipts'
        receipt_id = str(uuid.uuid4())
        receipts[receipt_id] = 100

        # Send GET request to /receipts/{id}/points
        response = self.app.get(f'/receipts/{receipt_id}/points')
        data = response.get_json()

        # Assert status code and 'points' in response
        self.assertEqual(response.status_code, 200)
        self.assertIn('points', data)
        self.assertEqual(data['points'], 100)

    def test_get_points_not_found(self):
        # Send GET request to a non-existing receipt ID
        response = self.app.get('/receipts/invalid-id/points')
        data = response.get_json()

        # Assert status code and 'error' message in response
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Receipt not found')

if __name__ == '__main__':
    unittest.main()

