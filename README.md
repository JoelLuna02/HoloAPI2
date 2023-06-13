# HoloAPI
An API RESTFul fanmade based in hololive

Welcome! This is the HoloAPI GitHub page. In this section you can explore a bit the source code which is made of this REST API.

**If you want to test our available resources, you can access the [documentation](https://holoapi.onrender.com/docs). It Uses the [Swagger UI.](https://swagger.io/)**

**For more information about how this API works, you can access the [frequently asked questions](https://holoapi.onrender.com/faqs) section.**

If you want to contribute to this project and you have knowledge in web programming, you need to meet the following requirements:

- Knowledge of Python
- Basic knowledge of object-oriented programming.
- Knowledge of Flask for Web application development
- Knowledge in SQLAlchemy, Marshmallow, RESTful and Migrate for the creation of an API and its corresponding database.
- Knowledge of Flask's ApiSpec for API documentation (If you wish, you can import your own documentation, any contribution will be of great help).

You will need:
- Python >= 3.7
- Flask (Stable Version)
- SQLAlchemy (Stable Version)
- APISpec (0.7.0)
- RESTful (Stable Version)
- Migrate
- Gunicorn (To run server)

You can run this application by doing the following on your console:
```bash
git clone https://github.com/JoelLuna02/HoloAPI2
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Important**: You can declare local variables JWT_SECRET or a SECRET_KEY to protect your Application, as well as a Postgres-like database and store its corresponding url in the DB_URL variable. You can also declare APISPEC_SWAGGER to display the content of the swagger documentation and then modify the static/swagger-initializer.js file in the URL section and define localhost:5000/swagger/ or a path in question to initialize the local project.

To run this project; type: `flask run --reload` or `gunicorn main:apli`

If you have any questions or problems, you can access the [Issues](https://github.com/JoelLuna02/HoloAPI2/issues) section.
