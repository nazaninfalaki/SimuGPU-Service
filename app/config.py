import os

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = "HS256"
JWT_EXPIRE_MINUTES = 120

SIM_SPEED = float(os.getenv("SIM_SPEED", "2"))
