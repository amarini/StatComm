#include <boost/python.hpp>
#include <boost/math/distributions/beta.hpp>

using namespace boost::python;

class betainvClass {
    public: double betainv(double p, double a, double b);
};

double betainvClass::betainv(double p, double a, double b) { 
    return boost::math::ibeta_inv(a, b, p);
}

// Expose classes and methods to Python
BOOST_PYTHON_MODULE(betainv) {
    class_<betainvClass> ("create_betainv_instance")
        .def("betainv", &betainvClass::betainv)
    ;
}
