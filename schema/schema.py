custom_paths = {
    "servers": [
        {
            "url": "{protocol}://{environment}.zyla.in/api/v1",
            "variables": {
                "protocol": {
                    "enum": ["http", "https"],
                    "default": "https"
                },
                "environment": {
                    "enum": ["services", "feature.services"],
                    "default": "feature.services"
                }
            }
        }

    ],
    'paths': {
        '/medicine/schema': {
            'get': {
                "summary": "Get schema for medicine service",
                "responses": {
                    "200": {
                        "description": "Schema fetched successfully"
                    }
                },
                "tags": ["Schema"]
            },
        }
    },
    "tags": [
        {
            "name": "Schema"
        }
    ]
}
