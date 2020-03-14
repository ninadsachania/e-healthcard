# E-HealthCard 👨‍⚕️

## Build Instructions

```
$ pip3 install -r requirements.txt
```

Then execute `run.sh` file:

```
$ ./run.sh
...
```

## API

* `GET /api/users/<id>` Return a user
* `GET /api/users/` Return the collection of users
* `POST /api/users` Register a new account
* `PUT /api/users/<id>` Modify a user 
* `GET /api/users/static_information/<id>` Return the static information of a user
* `PUT /api/users/static_information/<id>` Modify the static information of a user
