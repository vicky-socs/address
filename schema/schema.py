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

    ]
}
