# Overview

A dockerised stack containing the following components:

* FastAPI backend
* Postgres database
* SQLAlchemy ORM (Async)
* Alembic Migrations
* Pydantic Validations

# Getting Started

TODO

1. Clone repo:

    ```git clone git@github.com:pavdwest/fastapi_pg_sqlalchemy.git```

2. Enter directory:

    ```cd fastapi_pg_sqlalchemy```

3. Create & activate virtual environment:

    ```python -m venv services/backend/app/.ignore/venv && source services/backend/app/.ignore/venv/bin/activate```

4. Install dependencies for local development/intellisense:

    ```pip install -r services/backend/app/requirements/base.txt```

5. Add .env file:

    ```cp ./.env.example ./.env```

6. Run stack (we attach only to the backend as we don't want to listen to PGAdmin4 spam):

    ```docker compose up --build --attach backend```

7. Everything's running:

    ```http://127.0.0.1:8000/docs```

8. Run migrations with Alembic:

     ```docker compose exec fastapi_pg_sqlalchemy-backend-1 alembic upgrade head```

# Notes

## Set up Alembic from scratch:

```docker compose exec fastapi_pg_sqlalchemy-backend-1 alembic init -t async src/migrations```

## PGAdmin4

You can access PGAdmin4 at ```http://localhost:5050```.

See the `pgadmin` service in the ```docker-componse.yml``` file for credentials.

Once you've logged into PGAdmin add the db server using the details as per `db` service in the ```docker-componse.yml```. **_Tip: Host name/address is `db` (name of the service) by default._**

## Adding a New Model

1. Add folder to ```services/backend/app/src/modules```

    `.../models/my_model/routes.py`         for the endpoints

    `.../models/my_model/models.py`         for the SQLAlchemy model

    `.../models/my_model/validators.py`     for the Pydantic validators

2. Import models to ```services/backend/app/src/migrations/env.py```

3. Create migration:

    ```docker exec -it fastapi_pg_sqlalchemy-backend-1 alembic revision --autogenerate -m "Add MyModel"```

4. Run migration:

    ```docker exec -it fastapi_pg_sqlalchemy-backend-1 alembic upgrade head"```
