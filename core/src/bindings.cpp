#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/chrono.h>
#include "core.hpp"
#include "money.hpp"
#include "transaction.hpp"

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

    // Transaction struct
    py::class_<cream::Transaction>(m, "Transaction")
        .def(py::init<>())
        .def(py::init<int64_t, int64_t, int64_t, cream::Money, std::string, cream::Timestamp>(),
             py::arg("id"), py::arg("wallet_id"), py::arg("category_id"),
             py::arg("amount"), py::arg("description"), py::arg("occurred_at"))
        .def_readwrite("id", &cream::Transaction::id)
        .def_readwrite("wallet_id", &cream::Transaction::wallet_id)
        .def_readwrite("category_id", &cream::Transaction::category_id)
        .def_readwrite("amount", &cream::Transaction::amount)
        .def_readwrite("description", &cream::Transaction::description)
        .def_readwrite("occurred_at", &cream::Transaction::occurred_at)
        .def("is_income", &cream::Transaction::is_income)
        .def("is_expense", &cream::Transaction::is_expense)
        .def("__repr__", [](const cream::Transaction& t) {
            return "Transaction(id=" + std::to_string(t.id) +
                   ", amount=" + t.amount.to_string() + ")";
        });
}
