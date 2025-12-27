# TODO: Simplify Architecture (Option 1)

Remove C++ core and implement validation in pure Python.

## Phase 1: Add Python Validation

- [ ] Create `backend/app/services/validation.py`
  - [ ] Implement `TransactionValidator` class
  - [ ] Add amount validation rules:
    - [ ] Amount must not be zero
    - [ ] Amount must be >= 0.0001 (minimum precision)
    - [ ] Amount must be <= 999,999,999.9999 (maximum)
  - [ ] Add date validation rules:
    - [ ] `occurred_at` must not be in the future (configurable)
  - [ ] Add ID validation rules:
    - [ ] `wallet_id` must be positive
    - [ ] `category_id` must be positive
  - [ ] Return structured validation errors

- [ ] Create `backend/app/services/category_helpers.py` (optional)
  - [ ] Implement `get_children(category_id, db)` using SQL
  - [ ] Implement `get_ancestors(category_id, db)` using recursive CTE
  - [ ] Add cycle detection for category hierarchy

- [ ] Write tests for validation
  - [ ] `backend/tests/test_validation.py`
  - [ ] Test all validation rules
  - [ ] Test edge cases (zero, negative, future dates)
  - [ ] Test error message formatting

## Phase 2: Integrate Validation into API

- [ ] Update `backend/app/api/transactions.py`
  - [ ] Import and use `TransactionValidator`
  - [ ] Validate before database write in `create_transaction`
  - [ ] Validate before database write in `update_transaction`
  - [ ] Return 422 with validation errors on failure

- [ ] Update transaction tests
  - [ ] Add tests for validation errors in create
  - [ ] Add tests for validation errors in update

## Phase 3: Remove C++ Core

- [ ] Delete `core/` directory
  - [ ] `core/include/` - all header files
  - [ ] `core/src/` - bindings.cpp
  - [ ] `core/tests/` - all test files
  - [ ] `core/CMakeLists.txt`

- [ ] Update documentation
  - [ ] Update `README.md` - remove C++ references
  - [ ] Update `CLAUDE.md` - remove C++ references
  - [ ] Update `claude/backend-progress.md` - mark C++ integration as N/A
  - [ ] Update `claude/cpp-core-progress.md` - archive or delete

## Phase 4: Cleanup

- [ ] Remove C++ related files
  - [ ] Delete `.clang-format` if exists
  - [ ] Delete any CMake cache files
  - [ ] Delete any build directories

- [ ] Update project structure in README
  - [ ] Remove `core/` from project structure diagram
  - [ ] Update architecture diagram

- [ ] Final verification
  - [ ] Run all backend tests: `pytest`
  - [ ] Verify all 92+ tests pass
  - [ ] Manual API testing

## Estimated Effort

| Phase | Lines of Code | Time |
| ------- | --------------- | ------ |
| Phase 1 | ~100 lines | - |
| Phase 2 | ~20 lines | - |
| Phase 3 | Delete ~2000 lines | - |
| Phase 4 | Documentation | - |

## Success Criteria

- [ ] All existing tests pass
- [ ] New validation tests pass
- [ ] No C++ code remains in project
- [ ] Documentation is updated
- [ ] API behavior unchanged (validation is additive)
