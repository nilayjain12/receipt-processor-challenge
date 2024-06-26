from flask import Flask, request, jsonify
import uuid
import re
from flasgger import Swagger, swag_from

app = Flask(__name__)
#swagger = Swagger(app)

receipts = {}

swagger_template = {
    "components": {
        "schemas": {
            "Receipt": {
                "type": "object",
                "required": [
                    "retailer",
                    "purchaseDate",
                    "purchaseTime",
                    "items",
                    "total"
                ],
                "properties": {
                    "retailer": {
                        "description": "The name of the retailer or store the receipt is from.",
                        "type": "string",
                        "pattern": "^[\\w\\s\\-&]+$",
                        "example": "M&M Corner Market"
                    },
                    "purchaseDate": {
                        "description": "The date of the purchase printed on the receipt.",
                        "type": "string",
                        "format": "date",
                        "example": "2022-01-01"
                    },
                    "purchaseTime": {
                        "description": "The time of the purchase printed on the receipt. 24-hour time expected.",
                        "type": "string",
                        "format": "time",
                        "example": "13:01"
                    },
                    "items": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "$ref": "#/components/schemas/Item"
                        }
                    },
                    "total": {
                        "description": "The total amount paid on the receipt.",
                        "type": "string",
                        "pattern": "^\\d+\\.\\d{2}$",
                        "example": "6.49"
                    }
                }
            },
            "Item": {
                "type": "object",
                "required": [
                    "shortDescription",
                    "price"
                ],
                "properties": {
                    "shortDescription": {
                        "description": "The Short Product Description for the item.",
                        "type": "string",
                        "pattern": "^[\\w\\s\\-]+$",
                        "example": "Mountain Dew 12PK"
                    },
                    "price": {
                        "description": "The total price paid for this item.",
                        "type": "string",
                        "pattern": "^\\d+\\.\\d{2}$",
                        "example": "6.49"
                    }
                }
            }
        }
    }
}

swagger = Swagger(app, template=swagger_template)

@app.route('/receipts/process', methods=['POST'])
@swag_from({
    'summary': 'Submits a receipt for processing',
    'description': 'Submits a receipt for processing',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    '$ref': '#/components/schemas/Receipt'
                }
            }
        }
    },
    'responses': {
        '200': {
            'description': 'Returns the ID assigned to the receipt',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'id': {
                                'type': 'string',
                                'example': 'adb6b560-0eef-42bc-9d16-df48f30e89b2'
                            }
                        }
                    }
                }
            }
        },
        '400': {
            'description': 'The receipt is invalid',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {
                                'type': 'string',
                                'example': 'Invalid receipt format'
                            }
                        }
                    }
                }
            }
        },
        '422': {
            'description': 'Unprocessable entity due to validation error',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {
                                'type': 'string',
                                'example': 'Validation error: retailer format is incorrect'
                            }
                        }
                    }
                }
            }
        }
    }
})

def process_receipt():
    receipt = request.json
    is_valid, error_message = validate_receipt(receipt)

    if not is_valid:
        if error_message.startswith("Invalid"):
            return jsonify({"error": error_message}), 400
        else:
            return jsonify({"error": error_message}), 422

    receipt_id = str(uuid.uuid4())
    points = calculate_points(receipt)
    receipts[receipt_id] = points
    return jsonify({"id": receipt_id})

@app.route('/receipts/<id>/points', methods=['GET'])
@swag_from({
    'summary': 'Returns the points awarded for the receipt',
    'description': 'Returns the points awarded for the receipt',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'description': 'The ID of the receipt',
            'schema': {
                'type': 'string',
                'example': 'adb6b560-0eef-42bc-9d16-df48f30e89b2'
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'The number of points awarded',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'points': {
                                'type': 'integer',
                                'example': 100
                            }
                        }
                    }
                }
            }
        },
        '404': {
            'description': 'No receipt found for that id',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'error': {
                                'type': 'string',
                                'example': 'Receipt not found'
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_points(id):
    if id in receipts:
        return jsonify({"points": receipts[id]})
    else:
        return jsonify({"error": "Receipt not found"}), 404

def validate_receipt(receipt):
    required_fields = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
    for field in required_fields:
        if field not in receipt:
            return False, f"Invalid receipt format: missing {field}"

    if not re.match(r'^[\w\s\-&]+$', receipt['retailer']):
        return False, "Validation error: retailer format is incorrect"

    if not re.match(r'^\d{4}-\d{2}-\d{2}$', receipt['purchaseDate']):
        return False, "Validation error: purchaseDate format is incorrect"

    if not re.match(r'^\d{2}:\d{2}$', receipt['purchaseTime']):
        return False, "Validation error: purchaseTime format is incorrect"

    if not re.match(r'^\d+\.\d{2}$', receipt['total']):
        return False, "Validation error: total format is incorrect"

    if not isinstance(receipt['items'], list) or len(receipt['items']) < 1:
        return False, "Validation error: items must be a non-empty list"

    for item in receipt['items']:
        is_valid, error_message = validate_item(item)
        if not is_valid:
            return False, error_message

    return True, None

def validate_item(item):
    required_fields = ['shortDescription', 'price']
    for field in required_fields:
        if field not in item:
            return False, f"Validation error: missing {field} in item"

    if not re.match(r'^[\w\s\-]+$', item['shortDescription']):
        return False, "Validation error: shortDescription format is incorrect"

    if not re.match(r'^\d+\.\d{2}$', item['price']):
        return False, "Validation error: price format is incorrect"

    return True, None

def calculate_points(receipt):
    points = 0
    retailer = receipt['retailer']
    total = float(receipt['total'])
    items = receipt['items']
    purchase_date = receipt['purchaseDate']
    purchase_time = receipt['purchaseTime']

    # Rule 1: One point for every alphanumeric character in the retailer name
    points += sum(1 for char in retailer if char.isalnum())

    # Rule 2: 50 points if the total is a round dollar amount
    if total.is_integer():
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if total % 0.25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt
    points += (len(items) // 2) * 5

    # Rule 5: If the trimmed length of the item description is a multiple of 3, 
    # multiply the price by 0.2 and round up to the nearest integer
    for item in items:
        description = item['shortDescription'].strip()
        price = float(item['price'])
        if len(description) % 3 == 0:
            points += int(price * 0.2 + 0.99)

    # Rule 6: 6 points if the day in the purchase date is odd
    day = int(purchase_date.split('-')[2])
    if day % 2 != 0:
        points += 6

    # Rule 7: 10 points if the time of purchase is between 2:00pm and 4:00pm
    hour, minute = map(int, purchase_time.split(':'))
    if 14 <= hour < 16:
        points += 10

    return points

if __name__ == '__main__':
    app.run(debug=True)
