from abc import ABC, abstractmethod
from mfds_admin.app.dtos.admin_auth_dto import AdminLoginCommand, AdminTokenDTO

class AdminAuthUseCase(ABC):
    @abstractmethod
    async def login(self, command: AdminLoginCommand) -> AdminTokenDTO:
        pass
