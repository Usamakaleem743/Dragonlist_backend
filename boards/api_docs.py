"""
API Documentation for Dragonlist Backend

Base URL: http://localhost:8000/api/

Authentication:
- All endpoints except auth/register and auth/login require JWT token
- Add token to request headers: Authorization: Bearer <access_token>
"""

# Authentication Examples
AUTH_ENDPOINTS = {
    "register": {
        "endpoint": "/api/auth/register/",
        "method": "POST",
        "request": {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
            "first_name": "Test",
            "last_name": "User"
        },
        "response": {
            "user": {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User"
            },
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    },
    "login": {
        "endpoint": "/api/auth/login/",
        "method": "POST",
        "request": {
            "username": "testuser",
            "password": "securepassword123"
        },
        "response": {
            "user": {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com"
            },
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    }
}

# Board Endpoints
BOARD_ENDPOINTS = {
    "list_create": {
        "endpoint": "/api/boards/",
        "method": "GET/POST",
        "request": {
            "title": "My Project Board",
            "background": "#0079bf"
        },
        "response": {
            "id": 1,
            "title": "My Project Board",
            "background": "#0079bf",
            "owner": {"id": 1, "username": "testuser"},
            "members": [],
            "lists": [],
            "labels": [],
            "created_at": "2024-02-20T12:00:00Z",
            "updated_at": "2024-02-20T12:00:00Z"
        }
    },
    "add_member": {
        "endpoint": "/api/boards/{board_id}/add_member/",
        "method": "POST",
        "request": {
            "user_id": 2
        },
        "response": "HTTP 200 OK"
    }
}

# List Endpoints
LIST_ENDPOINTS = {
    "create": {
        "endpoint": "/api/lists/",
        "method": "POST",
        "request": {
            "title": "To Do",
            "board": 1
        },
        "response": {
            "id": 1,
            "title": "To Do",
            "board": 1,
            "order": 1,
            "cards": [],
            "created_at": "2024-02-20T12:00:00Z"
        }
    }
}

# Card Endpoints
CARD_ENDPOINTS = {
    "create": {
        "endpoint": "/api/cards/",
        "method": "POST",
        "request": {
            "title": "Implement API",
            "description": "Create REST API endpoints",
            "list": 1
        },
        "response": {
            "id": 1,
            "title": "Implement API",
            "description": "Create REST API endpoints",
            "list": 1,
            "order": 1,
            "members": [],
            "labels": [],
            "checklists": [],
            "attachments": [],
            "location": None,
            "due_date": None,
            "due_date_complete": False,
            "created_at": "2024-02-20T12:00:00Z",
            "updated_at": "2024-02-20T12:00:00Z"
        }
    },
    "move": {
        "endpoint": "/api/cards/{card_id}/move/",
        "method": "POST",
        "request": {
            "list_id": 2,
            "order": 1
        },
        "response": "Updated card object"
    },
    "members": 'CARD_MEMBER_ENDPOINTS'
}

# Checklist Endpoints
CHECKLIST_ENDPOINTS = {
    "create": {
        "endpoint": "/api/checklists/",
        "method": "POST",
        "request": {
            "title": "Development Tasks",
            "card": 1
        },
        "response": {
            "id": 1,
            "title": "Development Tasks",
            "items": [],
            "created_at": "2024-02-20T12:00:00Z"
        }
    }
}

# Checklist Item Endpoints
CHECKLIST_ITEM_ENDPOINTS = {
    "create": {
        "endpoint": "/api/checklist-items/",
        "method": "POST",
        "request": {
            "title": "Create models",
            "checklist": 1
        },
        "response": {
            "id": 1,
            "title": "Create models",
            "checked": False,
            "order": 1
        }
    },
    "toggle": {
        "endpoint": "/api/checklist-items/{item_id}/toggle/",
        "method": "POST",
        "response": "Updated checklist item object"
    }
}

# Label Endpoints
LABEL_ENDPOINTS = {
    "create": {
        "endpoint": "/api/labels/",
        "method": "POST",
        "request": {
            "title": "Bug",
            "color": "#ff0000",
        },
        "response": {
            "id": 1,
            "title": "Bug",
            "color": "#ff0000"
        }
    }
}

# Attachment Endpoints
ATTACHMENT_ENDPOINTS = {
    "create": {
        "endpoint": "/api/attachments/",
        "method": "POST",
        "request": {
            "title": "Design Document",
            "file": "<file_upload>",
            "card": 1
        },
        "response": {
            "id": 1,
            "title": "Design Document",
            "file": "/media/attachments/design.pdf",
            "url": "",
            "created_at": "2024-02-20T12:00:00Z"
        }
    }
}

# Card Location Endpoints
CARD_LOCATION_ENDPOINTS = {
    "create": {
        "endpoint": "/api/card-locations/",
        "method": "POST",
        "request": {
            "card": 1,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "place_name": "New York City"
        },
        "response": {
            "id": 1,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "place_name": "New York City"
        }
    }
}

# Card Member Endpoints
CARD_MEMBER_ENDPOINTS = {
    "list_members": {
        "endpoint": "/api/cards/{card_id}/members/",
        "method": "GET",
        "response": [
            {
                "id": 1,
                "username": "user1",
                "email": "user1@example.com",
                "first_name": "John",
                "last_name": "Doe"
            }
        ]
    },
    "add_member": {
        "endpoint": "/api/cards/{card_id}/members/",
        "method": "POST",
        "request": {
            "user_id": 1
        },
        "response": {
            "id": 1,
            "title": "Card Title",
            "members": [
                {
                    "id": 1,
                    "username": "user1",
                    "email": "user1@example.com",
                    "first_name": "John",
                    "last_name": "Doe"
                }
            ],
            # ... other card fields ...
        }
    },
    "remove_member": {
        "endpoint": "/api/cards/{card_id}/members/",
        "method": "DELETE",
        "request": {
            "user_id": 1
        },
        "response": {
            "id": 1,
            "title": "Card Title",
            "members": [],
            # ... other card fields ...
        }
    },
    "assign_multiple": {
        "endpoint": "/api/cards/{card_id}/assign-multiple-members/",
        "method": "POST",
        "request": {
            "user_ids": [1, 2, 3]
        },
        "response": {
            "card": {
                "id": 1,
                "title": "Card Title",
                "members": [
                    # ... member objects ...
                ]
            },
            "added_users": [1, 2],
            "errors": ["User 3 is already assigned to this card"]
        }
    }
} 