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


### List all the users

**Definition**

`GET /api/users/all` (Login required)

**Response**

- `200 OK` on success
- `401 UNAUTHORIZED` on unauthorized access

```json
[
    {
        "aadhar_card": "123214983204",
        "address": "Shivanand Bungalows B/H Annapurna Restaurant Jashodanagar",
        "avatar": "https://www.gravatar.com/avatar/4edab099fecc10e6f090d5567ab7c2aa?d=identicon&s=128",
        "email": "ninad.sachania@gmail.com",
        "firstname": "Ninad",
        "id": 1,
        "lastname": "Sachania",
        "middlename": "Jaimin",
        "phone_number": "9099869696",
        "rfid": null
    }
]
```

It will return an empty array (`[]`) if there are not users.

* `GET /api/users/<id>` Return a user
* `GET /api/users/` Return the collection of users
* `POST /api/users` Register a new account
* `PUT /api/users/<id>` Modify a user
* `GET /api/users/static_information/<id>` Return the static information of a user
* `PUT /api/users/static_information/<id>` Modify the static information of a user
