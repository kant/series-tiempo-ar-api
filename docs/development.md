# Development

# Requerimientos

- Python 2.7.6
- Virtualenv
- Docker
- Docker compose

## Setup

### Virtualen (con Pyenv)
```bash
pyenv virtualenv 2.7.6 stiempo-api
pyenv activate stiempo-api
pip install -r requirements/local.txt
```

### Configuración

```bash
cp conf/settings/local_example.py conf/settings/local.py
cp conf/settings/.env.default_local conf/settings/.env
```

### Servicios

```bash
docker-compose pull
docker-compose up -d
```

### Base de datos

```bash
python manage.py migrate
```

## Pruebas

```bash
python manage.py read_datajson http://infra.datos.gob.ar/catalog/sspm/data.json
```

## Tests

```bash
./manage.py generate_data --years=300
./manage.py test
```