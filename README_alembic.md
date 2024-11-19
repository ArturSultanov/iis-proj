# Create migration

```bash
pip install alembic
```

```bash
alembic init alembic
```

```bash
alembic revision --autogenerate -m "<message>"
```

# Apply migration

```bash
alembic upgrade head
```