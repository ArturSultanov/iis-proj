# Create migration


# Install alembic for migration ability
```bash
pip install alembic
```

# Initialize alembic for migration
```bash
alembic init alembic
```

# Edit alembic.ini file
place the database connection string in the sqlalchemy.url field, then create migration script
```bash
alembic revision --autogenerate -m "<message>"
```

# Apply migration

```bash
alembic upgrade head
```