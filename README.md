# PJVMS Backend

### This is main repository for backend part of PJVMS

## How to Start

### Clone & Setup Environment

1. Clone from our beloved repository

```
git clone git@github.com:egelipta/template-backend.git
```

2. Copy dan sesuaikan isi .env

```
cp env-example .env
vim .env
```

2. Create python virtualenv

```
python3.9 -m virtualenv .venv
```

3. Activate your newly created python virtualenv

```
source .venv/bin/activate
```

4. Upgrade pip

```
pip install -U pip
```

5. Install required python library

```
pip install -r requirements.txt
```

### Setup Database Server

1. Make sure docker daemon is running, then spawn mysql+pma with docker-compose

```
docker-compose up -d
```

2. Login to your PMA then import db.sql

### Run Backend

```
uvicorn app:app --reload --host 0.0.0.0 --port 8888
```
