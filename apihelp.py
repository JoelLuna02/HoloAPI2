apih = {
    "/v1": "Shows the api rest version and all information of routes",
    "/v1/vtuber": [
        {
            "/": "Shows all vtubers stored in the database",
            "Is_it_a_protected_route": False,
            "route_method": "GET",
            "status_code": 200
        },
        {
            "/random": "Select a random vtuber and shows her information",
            "Is_it_a_protected_route": False,
            "route_method": "GET",
            "status_code": 200
        },
        {
            "/{id}": "Shows vtuber's information by id",
            "Is_it_a_protected_route": False,
            "route_method": "GET",
            "status_code": 200
        },
        {
            "/create": "Creates a vtuber",
            "Is_it_a_protected_route": True,
            "route_method": "POST",
            "status_code": 201
        },
        {
            "/delete/{id}": "Delete a vtuber by id",
            "Is_it_a_protected_route": True,
            "route_method": "DELETE",
            "status_code": 204
        },
        {
            "/update/{id}": "Update the vtuber's information by id",
            "Is_it_a_protected_route": True,
            "route_method": "PUT",
            "status_code": 200
        }
    ],
    "/v1/auth": [
        {
            "/signup": "Registers a user for the use of routes. By default [normal user]",
            "Is_it_a_protected_route": True,
            "route_method": "POST",
            "status_code": 201
        },
        {
            "/login": "Sign in to a registered user.",
            "Is_it_a_protected_route": False,
            "routed_method": "POST",
            "status_code": 200
        }
    ]
}