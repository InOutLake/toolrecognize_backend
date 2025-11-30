# Backend service for inventory automation 
Note: I'm working on clean architecture for this app, you can check it out in the other branch
## Quickstart  
Before start make sure you have cuda and nvidia container toolkit installed on your machine.

To run the service locally, execute the following command from the project root:  
`docker compose --env-file local.env up --build`  

Access URLs:  
- API: `http://localhost:7999`, documentation at `http://localhost:8000/docs`  
- Recognition service: `http://localhost:8000`, documentation at `http://localhost:8001/docs`  
- Message broker console: `http://localhost:15672`  

## Configuration  
Service configuration is performed by setting environment variables. A complete list of variables and their descriptions can be found in `example.env`.

## About service
### Architecture
!(High level architecture diagram)[attachments/high-level-architecture.png)
The system consists of few components:
- Proxy server
- API with main business logic
- Redis for caching
- PostreSQL relational database
- Minio as file storage and file server
- Rabbitmq for managing CPU (or GPU) bound tasks queues
- FastStream workers with GPU bound task (detection)
It is also possible to use HTTP instead of AMQP protocol between FastStream workers and API by switching modes in .env file.
### API arhitecture
!(API low level architecture diagram)[attachments/api-low-level-architecture.png)
API separated on a few layers:
- View (or route)
- Service (main business logic)
- Repository (services interfaces)


## TODOs
- [ ] Implement clean architecture
- [ ] Separate shared modules into individual repository
- [ ] Cover with tests
- [ ] Connect graphana
- [ ] Perform stress tests
