from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from pydantic import AnyHttpUrl
from config import settings

TENANT_ID = settings.ID_DIRECTORIO
CLIENT_ID = settings.ID_APLICACION_CLIENTE
AZURE_APP_URI = settings.AZURE_APP_URI
SCOPE_NAME = settings.SCOPE_NAME
FULL_SCOPE_URI = settings.FULL_SCOPE_URI

azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=CLIENT_ID,
    tenant_id=TENANT_ID,
    scopes={
        FULL_SCOPE_URI: SCOPE_NAME
    },
)