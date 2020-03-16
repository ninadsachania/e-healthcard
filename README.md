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

It will return an empty array (`[]`) if there are no users.

### Get a token

**Definition**

`POST /api/users/token`

**Response**

- `200 OK` on success

```json
{
    "token": "4Id5JpPZ3NtYUgqlcNy5m12mjrbytZxt"
}
```

If you make a call and a token is already present then that token is returned instead of a new token.

- `401 UNAUTHORIZED` when the username or password fields are missing or empty

```json
{
    "error": "Unauthorized"
}
```

### Revoking a token

**Definition**

`DELETE /api/users/token`

**Response**

- `204 NO CONTENT` on success

No content in the body.

- `401 UNAUTHORIZED` when the token is wrong on not present

```json
{
    "error": "Unauthorized"
}
```

### Get a user's information

**Definition**

`GET /api/users` (Authorization required)

**Response**

- `200 OK` on success

```json
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
```

- `401 UNAUTHORIZED` when the token is wrong on not present

```json
{
    "error": "Unauthorized"
}
```

### Creating a user

**Definition**

`POST /api/users` (Authorization required)

**Arguments**

- `firstname: string`
- `middlename: string`
- `lastname: string`
- `email: string`
- `aadhar_card: string` The aadhar_card of the user (it should be 12 in length).
- `phone_number: string` It should be 10 in length.
- `address: string` The address of the user
- `password: string`

**Response**

- `201 CREATED` on success

```json
{
    "aadhar_card": "123456789012",
    "address": "India",
    "avatar": "https://www.gravatar.com/avatar/c89cf6721f229f50dfddb66873f6779e?d=identicon&s=128",
    "email": "sagar.gohil@gmail.com",
    "firstname": "Sagar",
    "id": 3,
    "lastname": "Gohil",
    "middlename": "B",
    "phone_number": "9099869695",
    "rfid": null
}
```

- `409 CONFLICT` if the `email`, `phone_number` or `aadhar_card` already exists.

```json
{
    "error": "Conflict",
    "message": "Sorry! This email is already in use"
}
```

```json
{
    "error": "Conflict",
    "message": "Sorry! This phone number is already in use."
}
```

```json
{
    "error": "Conflict",
    "message": "Sorry! This aadhar number is already in use."
}
```

### Get a user's static information

**Definition**

`GET /api/users/static_information`

**Response**

- `200 OK` on success

```json
{
    "allergies": "From stupid people.",
    "bloodgroup": "A+",
    "current_medication": "Vitamin B12",
    "dob": "Tue, 07 Jul 1998 00:00:00 GMT",
    "emergency_contact": "9099869696",
    "gender": "Male",
    "height": 180,
    "id": 1,
    "weight": 71.0
}
```

- `204 NO CONTENT` if there is no static information