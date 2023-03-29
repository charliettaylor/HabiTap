# HabiTap
A habit tracker with a good API

## Development Notes

### Docker

Commands to spin up containers and bring them down

```sh
docker-compose up -d --build --remove-orphans

docker-compose down
```

### Python

Running on local will require making your own postgres database, so try using docker for convenience.

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 api.py <host> <port>
```

