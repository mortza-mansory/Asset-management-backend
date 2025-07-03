from fastapi import FastAPI
from app.features.auth.api.routes import router as auth_router
from app.features.users.api.routes import router as user_router
from app.features.company.api.routes import router as company_router
from app.features.subscription.api.routes import router as subscription_router
from app.features.assets_management.api.routes import router as asset_router
from app.features.assets_gps_management.api.routes import router as gps_router
from app.features.assets_loan_management.api.routes import router as loan_router
from app.features.assets_report_management.api.routes import router as report_router
from app.features.work_flow.api.routes import router as workflow_router
from app.features.logs.api.routes import router as log_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(company_router)
    app.include_router(subscription_router)
    app.include_router(asset_router)
    app.include_router(gps_router)
    app.include_router(loan_router)
    app.include_router(report_router)
    app.include_router(workflow_router)
    app.include_router(log_router)
