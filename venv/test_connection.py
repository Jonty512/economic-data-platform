from sqlalchemy import create_engine

engine = create_engine("postgresql://localhost/economic_platform")

with engine.connect():
    print("Connected!")