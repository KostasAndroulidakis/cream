#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include "cream/core.hpp"
#include "cream/money.hpp"

namespace py = pybind11;

PYBIND11_MODULE(cream_py, m) {
    m.doc() = "CREAM C++ Core - Finance engine for ledger, validation, and calculations";

    // Version info
    m.attr("VERSION_MAJOR") = cream::VERSION_MAJOR;
    m.attr("VERSION_MINOR") = cream::VERSION_MINOR;
    m.attr("VERSION_PATCH") = cream::VERSION_PATCH;
    m.attr("__version__") = std::to_string(cream::VERSION_MAJOR) + "." +
                            std::to_string(cream::VERSION_MINOR) + "." +
                            std::to_string(cream::VERSION_PATCH);

    // Money class
    py::class_<cream::Money>(m, "Money")
        .def(py::init<>())
        .def(py::init<int64_t>(), py::arg("cents"))
        .def_static("from_raw", &cream::Money::from_raw)
        .def_static("from_double", &cream::Money::from_double)
        .def_static("from_string", &cream::Money::from_string)
        .def("raw", &cream::Money::raw)
        .def("to_double", &cream::Money::to_double)
        .def("to_string", &cream::Money::to_string)
        .def("is_zero", &cream::Money::is_zero)
        .def("is_positive", &cream::Money::is_positive)
        .def("is_negative", &cream::Money::is_negative)
        .def("abs", &cream::Money::abs)
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self * int64_t())
        .def(py::self / int64_t())
        .def(-py::self)
        .def(py::self += py::self)
        .def(py::self -= py::self)
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def(py::self < py::self)
        .def(py::self <= py::self)
        .def(py::self > py::self)
        .def(py::self >= py::self)
        .def("__repr__", [](const cream::Money& m) {
            return "Money(" + m.to_string() + ")";
        });
}
