# Dailymotion test -- User registration API

## Run app
```sh
docker-compose up -d
```
## API documentation
This service is an HTTP API. It features two endpoints, usually used conjointly.

The first one "/register" is used to ask for the creation of a user. If everything is is order, the app then sends an email to the mail address, providing a verification code. You have one minute to go through the next step, after this delay, the code will be considered stale, you'll get an 410 HTTP code + an error response, and the process will need to be retried from scratch.

The second one "/verify" is used as another layer of security in the registering process. You need to provide it the verification code gathered with the call to the first endpoint.

Both take an application/x-www-form-urlencoded encoded request and return an application/json encoded response.

The stream is encrypted using a self-signed SSL certificate, thus the "--insecure" parameters on the examples below.

Using curl to illustrate practical examples :

```sh
#Submit a user creation request
curl --insecure -d "username=testusername&password=testpassword&email=foo@bar.com" -X POST https://localhost/register
#An email is sent, containing a verification code, (for the sake of the exercise, the code is also returned by the previous request as an HTTP data) get that code and use it to validate the creation  
curl --insecure -d "verification_code=1234" -X POST https://localhost/verify
```
## Run tests
```sh
docker exec -it <container_web_name> /bin/bash      
python3 -m unittest discover ./
```

## Architecture
![plot](./assets/Architecture.png)

