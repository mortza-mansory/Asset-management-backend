from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.core.models.base import Base

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/assetsrfid_db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.core.models.company import Company
from app.features.auth.data.models import User, UserCompanyRole, OtpToken, ResetCode, LoginAttempt
from app.features.logs.data.models import Log
from app.features.subscription.data.models import Subscription
from app.features.assets_management.data.models import Asset, AssetStatusHistory
from app.features.assets_loan_management.data.models import AssetLoan
from app.features.work_flow.data.models import WorkFlow

Base.metadata.create_all(bind=engine, checkfirst=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
