# HoloAPI2
An API RESTFul fanmade based in hololive

Welcome! This is the HoloAPI GitHub page. In this section you can explore a bit the source code which is made of this REST API.

**If you want to test our available resources, you can access the [documentation](https://holoapi.onrender.com/docs). It Uses the [Swagger UI.](https://swagger.io/)**

**For more information about how this API works, you can access the [frequently asked questions](https://holoapi.onrender.com/faqs) section.**

You can run this application by doing the following on your console:
```bash
git clone https://github.com/JoelLuna02/HoloAPI2
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Important**: You can declare local variables JWT_SECRET or a SECRET_KEY to run your Application, as well as a Postgres type database and store its corresponding url in the DB_URL variable. You can also declare APISPEC_SWAGGER to display the content of the swagger documentation and then modify the static/swagger-initializer.js file in the url section and define localhost:5000 to initialize the local project.
