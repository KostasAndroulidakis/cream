"""Creating, changing and deleting categories and groups (Settings › Categories).

System categories are shared by every user, so a user's changes to one (a new name, the budget
choice, deleting it) are stored as that user's CategoryOverride instead of changing the row.
"""

from fastapi import HTTPException, status
from sqlalchemy import delete, exists, select
from sqlalchemy.orm import Session

from app.models import BudgetBy, Category, CategoryOverride, MerchantRule, Transaction
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.authorization import SystemResourceError, check_category_cycle, verify_parent_category
from app.services.categorization.system_categories import UNCATEGORIZED_KEY, hidden_category_ids

# What a user can change on a system category
SYSTEM_EDITABLE = {"name", "budget_by"}


class CategoryRuleError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail)


class CategoryDeleteError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


def user_overrides(user_id: int, db: Session) -> dict[int, CategoryOverride]:
    """This user's changes to system categories, by category ID."""
    rows = db.scalars(select(CategoryOverride).where(CategoryOverride.user_id == user_id))
    return {row.category_id: row for row in rows}


def to_read(category: Category, override: CategoryOverride | None = None) -> CategoryRead:
    """The category as this user sees it: the system one with their changes on top."""
    read = CategoryRead.model_validate(category)
    if override is None:
        return read
    if override.name is not None:
        read.name = override.name
    if override.budget_by is not None:
        read.budget_by = BudgetBy(override.budget_by)
    return read


def read_for_user(category: Category, user_id: int, db: Session) -> CategoryRead:
    override = db.get(CategoryOverride, (user_id, category.id)) if category.user_id is None else None
    return to_read(category, override)


def _check_budget_fields(is_group: bool, budget_by: BudgetBy | None, exclude_from_budget: bool | None) -> None:
    if not is_group and budget_by is not None:
        raise CategoryRuleError("Only groups have a budget choice")
    if is_group and exclude_from_budget:
        raise CategoryRuleError("Exclude the group's categories from the budget instead")


def create_category(data: CategoryCreate, user_id: int, db: Session) -> Category:
    _check_budget_fields(data.is_group, data.budget_by, data.exclude_from_budget)
    if data.is_group:
        if data.parent_id is not None:
            raise CategoryRuleError("A group can't be inside another group")
    elif data.parent_id is not None:
        verify_parent_category(data.parent_id, data.type, user_id, db)

    values = data.model_dump()
    if data.is_group and data.budget_by is None:
        values["budget_by"] = BudgetBy.CATEGORY
    category = Category(user_id=user_id, **values)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(category: Category, changes: CategoryUpdate, user_id: int, db: Session) -> None:
    values = changes.model_dump(exclude_unset=True)
    _check_budget_fields(category.is_group, values.get("budget_by"), values.get("exclude_from_budget"))

    if category.user_id is None:
        _override_system_category(category, values, user_id, db)
        return

    if "parent_id" in values:
        if category.is_group and values["parent_id"] is not None:
            raise CategoryRuleError("A group can't be inside another group")
        if values["parent_id"] is not None:
            verify_parent_category(values["parent_id"], category.type, user_id, db)
            check_category_cycle(category.id, values["parent_id"], db)
    for field, value in values.items():
        # A name or flag can't be cleared; null there means "leave it"
        if value is None and field in {"name", "exclude_from_budget"}:
            continue
        setattr(category, field, value)
    db.commit()


def _override_system_category(category: Category, values: dict, user_id: int, db: Session) -> None:
    if set(values) - SYSTEM_EDITABLE:
        raise SystemResourceError("category")
    override = db.get(CategoryOverride, (user_id, category.id)) or CategoryOverride(
        user_id=user_id, category_id=category.id
    )
    if "name" in values and values["name"] is not None:
        # Back to the system name means no override
        override.name = None if values["name"] == category.name else values["name"]
    if "budget_by" in values:
        override.budget_by = values["budget_by"]
    db.add(override)
    db.commit()


def delete_category(category: Category, user_id: int, db: Session) -> None:
    """Delete a category, or a group with every category in it.

    Refused while any of them holds the user's transactions: deleting must never lose or move
    money records silently. System categories are hidden for this user instead of deleted.
    """
    hidden = hidden_category_ids(user_id, db)
    if category.is_group:
        children = [
            child
            for child in db.scalars(select(Category).where(Category.parent_id == category.id))
            if child.id not in hidden and child.user_id in (None, user_id)
        ]
    else:
        children = []
    targets = [category, *children]
    target_ids = [target.id for target in targets]

    if any(target.key == UNCATEGORIZED_KEY for target in targets):
        raise CategoryDeleteError("Uncategorized can't be deleted: new transactions wait there for a category")
    in_use = db.scalar(
        select(
            exists().where(
                Transaction.category_id.in_(target_ids),
                Transaction.wallet.has(user_id=user_id),
            )
        )
    )
    if in_use:
        what = "Its categories have" if category.is_group else "It has"
        raise CategoryDeleteError(f"{what} transactions. Move them to another category first.")

    for target in targets:
        if target.user_id is None:
            override = db.get(CategoryOverride, (user_id, target.id)) or CategoryOverride(
                user_id=user_id, category_id=target.id
            )
            override.is_hidden = True
            db.add(override)
    # The user's own categories (and the group itself, if theirs) go for good; children first
    for target in sorted(targets, key=lambda t: t.is_group):
        if target.user_id == user_id:
            db.delete(target)
    # Rules pointing at a hidden system category would keep filing transactions there
    db.execute(delete(MerchantRule).where(MerchantRule.user_id == user_id, MerchantRule.category_id.in_(target_ids)))
    db.commit()
