# Tech interview -- User registration API

DISCLAIMER : I've struggled understanding the level of abstractions I was allowed
 to use in this exercice (especially concerning the TCP socket managment),
 I've made the choice to use the aiohttp library, favoring performance and security
(and thus, the "production-ready" part of the exercise) over the simplistic
 approach I would have been able to achieve working  with the standard Python
 socket managment library in such a short time. If I was expected to work at
lower-level, please let me know, I'd be glad to update this repository as such.

  This app uses : 
   - A docker container with Python3, the aiohttp library, the pymongo database driver,
   the passlib library to encrypt the passwords in database.
   - A Mongodb docker container.
   - A reverse-proxy (Nginx) docker container to be able to use 
   multiple web server instances.
   - A Mailhog mock smtp server in a docker container.

## Run app
```sh
#You might want to modify the .env file to set-up the mongo credentials
#Otherwise, root:root will be used
docker-compose up -d
```
## API documentation
This service is an HTTP API. It features two endpoints, usually used conjointly.

The first one "/register" is used to ask for the creation of a user.
 If everything is is order, the app then sends an email to the mail address, 
 providing a verification code (it also appears in the HTTP response). 
 You have one minute to go through the next step, after this delay, 
 the code will be considered stale, you'll get an 410 HTTP code + 
 an error response, and the process will need to be retried from scratch.

The second one "/verify" is used as another layer of security 
in the registering process. You need to provide it the verification 
code gathered with the call to the first endpoint. It is using 
BASIC AUTH and therefore will raise an HTTP 401 if the authentication 
fails (either the header is missing or the credentials are wrong).

Both take an application/x-www-form-urlencoded encoded 
request and return an application/json encoded response.

The stream is encrypted using a self-signed SSL certificate, 
thus the "--insecure" parameters on the examples below.

Using curl to illustrate practical examples :

```sh
'''
Submit a user creation request
  --insecure : Don`t raise error when encountering self-signed SSL certificates

In case of success, the response will be of this format :
{
  "status": "success",
  "message": "The registration process has been recorded, \
    "here is your code (also sent via email)",
  "code": "7646"
}

Where "code" is the verification code needed at the next step.
In production, the code would not be returned in the HTTP response but sent
 to the email address only.
As the SMTP server is a mock here, I have had to return it here.
'''
curl --insecure -d "password=testpassword&email=foo@bar.com" -X POST https://localhost/register

'''
Get that code and use it to validate the creation.
   -u : sets-up BASIC AUTH HTTP Header
'''
curl --insecure -d "verification_code=XXXX" -u "foo@bar.com:testpassword" -X POST https://localhost/verify
```
## Run tests
```sh
docker exec -it tech-interview_web_1 /bin/bash
#TODO : find a unittest discovery solution to automate it   
python3 registration/verification_test.py
python3 registration/creation_test.py 
```

## Connecting to the database
```sh
docker exec -it tech-interview_mongo_1 /bin/bash
mongo --username <mongo_username> --password <mongo_password> --authenticationDatabase admin
use auth_api
db.users.find()
```

## Architecture 
![plot](./assets/Architecture.png)

