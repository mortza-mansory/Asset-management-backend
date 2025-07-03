import logging
from sqlalchemy import create_engine
from app.core.models.base import Base
from psycopg2.errors import DuplicateTable

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

engine = create_engine("postgresql://postgres:postgres@localhost:5432/assetsrfid_db")

logger.debug("Starting model imports")

try:
    from app.core.models.company import Company
    logger.debug("Imported Company model")
    from app.features.auth.data.models import User, UserCompanyRole, OtpToken, ResetCode, LoginAttempt
    logger.debug("Imported auth models")
    from app.features.logs.data.models import Log
    logger.debug("Imported Log model")
    from app.features.subscription.data.models import Subscription
    logger.debug("Imported Subscription model")
    from app.features.assets_management.data.models import Asset, AssetStatusHistory
    logger.debug("Imported assets models")
    from app.features.assets_loan_management.data.models import AssetLoan
    logger.debug("Imported AssetLoan model")
    from app.features.work_flow.data.models import WorkFlow
    logger.debug("Imported WorkFlow model")
except Exception as e:
    logger.error(f"Failed to import models: {str(e)}")
    raise

# لاگ‌گذاری مدل‌ها و جدول‌ها
logger.debug(f"Base subclasses: {[cls.__name__ for cls in Base.__subclasses__()]}")
try:
    registered_models = [model.__name__ for model in Base._decl_class_registry.values() if hasattr(model, '__tablename__')]
    logger.info(f"Registered models: {registered_models}")
except AttributeError:
    logger.warning("SQLAlchemy 2.0 detected; using metadata for model listing")
    registered_models = [cls.__name__ for cls in Base.__subclasses__() if hasattr(cls, '__tablename__')]
logger.info(f"Registered tables: {list(Base.metadata.tables.keys())}")

try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
    logger.info("Tables created")
except Exception as e:
    if isinstance(e.__cause__, DuplicateTable):
        logger.warning(f"Ignoring duplicate table/index error: {str(e)}")
    else:
        logger.error(f"Failed to create tables: {str(e)}")
        raise