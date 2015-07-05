# Development server with docker-compose

## First set up
```sh
docker-compose build
docker-compose up
# create tables & such in the db
docker-compose run web ./manage.py migrate
# create dev user
docker-compose run web ./manage.py createsuperuser
```

------------

## If you modify the model fields
```sh
docker-compose run web ./manage.py makemigrations
docker-compose run web ./manage.py migrate
```

## If Someone else modified the model fields
```sh
docker-compose run web ./manage.py migrate
```

## If you want to clear your data
```sh
docker-compose run web ./manage.py flush
docker-compose run web ./manage.py createsuperuser
```

## If you want a json dump of the database
```sh
docker-compose run web ./manage.py dumpdata
```

## If you want to play with the database
```sh
docker-compose run db psql -h db -U postgres
```
