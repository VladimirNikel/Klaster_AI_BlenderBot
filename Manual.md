# For local development

Activate the virtual environment using the commands:
```bash
python3 -m venv venv
source ./venv/bin/activate
```

Install the required libraries
```bash
pip3 install -r requirements.txt
pip3 install -r requirements_demon.txt
```

The next step is to fill in the `./docker-compose.yml` with the connection data. And export to the environment variables like:
```bash
export REDIS_CONNECT='{"hosts": [{"host": "<IP_1>", "port": "<PORT_1>"},{"host": "<IP_2>", "port": "<PORT_2>"},{"host": "<IP_3>", "port": "<PORT_3>"}], "password": "<REDIS_PASSWORD>"}'
export REDIS_CONNECT="redis://<__USER__>:<__PASSWORD__>@<__IP__>:<__PORT__>"
export API="http://<__IP__>:<__PORT__>"
```

> (!) Do not forget to specify the secret data in the fields, they are all highlighted in the same style.
 
And you can run the application:
```bash
python3 main.py
python3 demon.py
```



# For deploy

On the machine responsible for the neural part, transfer all the project files and run the command
```bash
docker-compose --compatibility up -d
```

