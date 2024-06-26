import unittest
import json
from app import app, validate_receipt, validate_item, calculate_points

class ReceiptProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_process_receipt_valid(self):
        receipt = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {
                    "shortDescription": "Mountain Dew 12PK",
                    "price": "6.49"
                }
            ],
            "total": "6.49"
        }
        response = self.app.post('/receipts/process', data=json.dumps(receipt), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('id', data)

    def test_process_receipt_invalid(self):
        receipt = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [],
            "total": "6.49"
        }
        response = self.app.post('/receipts/process', data=json.dumps(receipt), content_type='application/json')
        self.assertEqual(response.status_code, 422)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Validation error: items must be a non-empty list')

    def test_get_points_valid(self):
        receipt = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {
                    "shortDescription": "Mountain Dew 12PK",
                    "price": "6.49"
                }
            ],
            "total": "6.49"
        }
        response = self.app.post('/receipts/process', data=json.dumps(receipt), content_type='application/json')
        data = json.loads(response.data)
        receipt_id = data['id']
        
        response = self.app.get(f'/receipts/{receipt_id}/points')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('points', data)

    def test_get_points_invalid(self):
        response = self.app.get('/receipts/nonexistent-id/points')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Receipt not found')

    def test_validate_receipt(self):
        valid_receipt = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {
                    "shortDescription": "Mountain Dew 12PK",
                    "price": "6.49"
                }
            ],
            "total": "6.49"
        }
        is_valid, error_message = validate_receipt(valid_receipt)
        self.assertTrue(is_valid)
        self.assertIsNone(error_message)

        invalid_receipt = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [],
            "total": "6.49"
        }
        is_valid, error_message = validate_receipt(invalid_receipt)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, 'Validation error: items must be a non-empty list')

    def test_validate_item(self):
        valid_item = {
            "shortDescription": "Mountain Dew 12PK",
            "price": "6.49"
        }
        is_valid, error_message = validate_item(valid_item)
        self.assertTrue(is_valid)
        self.assertIsNone(error_message)

        invalid_item = {
            "shortDescription": "Mountain Dew 12PK",
            "price": "6.4"
        }
        is_valid, error_message = validate_item(invalid_item)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, 'Validation error: price format is incorrect')

    def test_calculate_points(self):
        receipt = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {
                    "shortDescription": "Mountain Dew 12PK",
                    "price": "6.49"
                }
            ],
            "total": "6.49"
        }
        points = calculate_points(receipt)
        self.assertEqual(points, 20)  # Assuming points calculation is correct

if __name__ == '__main__':
    unittest.main()
