# LACRI

lacri is an attempt to bring commonly used features of the openssl tool to a webapp. This makes it easier to generate certificates by clicking buttons instead of reading man pages everytime you need a new cert for personal use (e.g. openvpn, internal https/tls). It also keeps your PKI in a database instead of a file system somewhere.

# Create a new account

You can create a new account by simply entering a new username and password into the input fields on the front page. From there you will see a list of your roots, of which you have none to begin with.

[![Creating an account example](http://share.mrdanielsnider.com/lacri/smith_login.webm.play.png)](http://share.mrdanielsnider.com/lacri/smith_login.webm)

# Create a self-signed CA

On the roots page, you can navigate to an existing root, or create a new one by pressing the create button and entering a name. On the root's page you'll find the certificate and key available for download as well as instructions on how to trust the CA (and therefore all domain certificates created under it) on various operating systems (at the moment, only instructions for arch linux exist)

[![Creating a CA example](http://share.mrdanielsnider.com/lacri/smith_new_ca.webm.play.png)](http://share.mrdanielsnider.com/lacri/smith_new_ca.webm)


# Create a domain certificate & key

On a given roots page, you can inspect your domain certificates created for this root, or create a new one by clicking the create button and entering a domain name. 

On the certificate page you can find instructions for installing the certificate with nginx, apache2, and more. You can also find the files for download in a table at the bottom.

[![Creating a domain cert example](http://share.mrdanielsnider.com/lacri/smith_new_domain.webm.play.png)](http://share.mrdanielsnider.com/lacri/smith_new_domain.webm)

# Install with nginx
[![Installing a domain cert with nginx example](http://share.mrdanielsnider.com/lacri/smith_nginx.webm.play.png)](http://share.mrdanielsnider.com/lacri/smith_nginx.webm)


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
