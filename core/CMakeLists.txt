cmake_minimum_required(VERSION 3.15)
project(cream_core VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Options
option(BUILD_TESTS "Build unit tests" ON)
option(BUILD_PYTHON_BINDINGS "Build Python bindings" ON)

# Use modern Python finding for pybind11
set(PYBIND11_FINDPYTHON ON)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)

# Core library sources (exclude bindings.cpp)
file(GLOB_RECURSE CORE_SOURCES "src/*.cpp")
list(FILTER CORE_SOURCES EXCLUDE REGEX ".*bindings\\.cpp$")

# Create static library
add_library(cream_core STATIC ${CORE_SOURCES})
target_include_directories(cream_core PUBLIC ${CMAKE_SOURCE_DIR}/include)

# Python bindings
if(BUILD_PYTHON_BINDINGS)
    find_package(pybind11 CONFIG)
    if(pybind11_FOUND)
        pybind11_add_module(cream_py src/bindings.cpp)
        target_link_libraries(cream_py PRIVATE cream_core)
    else()
        message(WARNING "pybind11 not found, Python bindings will not be built")
    endif()
endif()

# Tests
if(BUILD_TESTS)
    enable_testing()
    find_package(GTest CONFIG)
    if(GTest_FOUND)
        file(GLOB_RECURSE TEST_SOURCES "tests/*.cpp")
        add_executable(cream_tests ${TEST_SOURCES})
        target_link_libraries(cream_tests PRIVATE cream_core GTest::gtest_main)
        include(GoogleTest)
        gtest_discover_tests(cream_tests)
    else()
        message(WARNING "GTest not found, tests will not be built")
    endif()
endif()
