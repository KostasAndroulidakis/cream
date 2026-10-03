from fastapi import APIRouter

from app.api import auth, bank, health, merchants, rules, wallets, categories, transactions, statistics

router = APIRouter()
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
router.include_router(bank.router, prefix="/bank", tags=["bank"])
router.include_router(rules.router, prefix="/rules", tags=["rules"])
router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
