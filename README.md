All the packages needed for the project is mentioned in 'requirements.txt' file. Install the packages using:
>       pip install -r requirements.txt


## LIST OF APIS

included a file named AccuKnox.postman_collection.json for the Postman Collections

1. **User Registration API**: /api/register/
- Method: POST
- Request Body: {
                    "email": "email@mail.com",
                    "password": "12345"
                }

2. **User Login API**: /api/login/
- Method: GET
- Request Body: {
                    "email": "vijesh@mail.com",
                    "password": "12345"
                }

3. **User Name Update API**: /api/user-name-update/
- Method: POST
- Request Body (logined user): {
                    "name": "HUMAN"
                }
- Request Body (Other user): {
                    "user_id": 3,
                    "name": "HUMAN"
                }

4. **User Search API**: /api/search/
- Method: GET
- Request Query Parameters: ?search=HUMAN

5. **Send Friends Request API**: /api/send-friends-requests/
- Method: POST
- Request Body:{
                    "request_recived_user_id": 5
                }

6. **Accept Friend Request API**: /api/accept-friend-request/
- Method: POST
- Request Body:{
                    "request_id": 3
                }

7. **Reject Friend Request API**: /api/reject-friend-request/
- Method: POST
- Request Body: {
                    "request_id": 4
                }

8. **List Friends API**: /api/list-friends/
- Method: GET
- Request Query Parameters: logined User id

9. **List Pending Requests API**: /api/list-pending-rquests/
- Method: GET
- Request Query Parameters: logined User id


## DATABASE SETUP
- Create a new database named `social_network` in your PostgresSQL.
>      all the database settings are in Accuknox > settings.py file under DATABASES check DB parameters 

- Run the following command to create the tables in the database in docker.
>      docker-compose exec db psql -U your_database_user -d postgres
>      CREATE DATABASE social_network;

- perform DB migrations using commands:
>       docker-compose exec python manage.py makemigrations
>       docker-compose exec python manage.py migrate



