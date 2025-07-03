from setuptools import setup, find_packages

setup(
    name="assetsrfid_backend",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.115.0",
        "uvicorn==0.32.0",
        "pydantic==2.9.2",
        "sqlalchemy==2.0.36",
        "passlib[bcrypt]==1.7.4",
        "python-jose[cryptography]==3.3.0",
        "python-dotenv==1.0.1",
        "slowapi==0.1.9",
        "emails==0.6",
        "pyjwt==2.10.1"
    ],
)
