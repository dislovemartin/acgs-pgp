from fastapi import APIRouter
from .endpoints import policies, constitution, policy_lifecycle, bulk_operations, policy_validation

api_router = APIRouter()
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(constitution.router, prefix="/constitution", tags=["constitution"])
api_router.include_router(policy_lifecycle.router, prefix="/policies/lifecycle", tags=["policy-lifecycle"])
api_router.include_router(bulk_operations.router, prefix="/policies", tags=["bulk-operations"])
api_router.include_router(policy_validation.router, prefix="/policies", tags=["policy-validation"])
