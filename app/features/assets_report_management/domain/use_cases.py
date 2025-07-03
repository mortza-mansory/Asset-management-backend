from app.features.assets_report_management.data.repository import ReportRepository

class GetCompanyReportUseCase:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    def execute(self, company_id: int) -> dict:
        return self.repository.get_company_report(company_id)