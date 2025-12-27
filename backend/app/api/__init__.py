from fastapi import APIRouter

from app.api import auth, wallets, categories, transactions

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
