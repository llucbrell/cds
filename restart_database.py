from models import Base, engine

# Elimina todas las tablas
Base.metadata.drop_all(engine)

# Crea todas las tablas de nuevo
Base.metadata.create_all(engine)
