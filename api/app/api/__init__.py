from fastapi import APIRouter

from app.api import auth, wallets, categories, transactions, statistics

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
