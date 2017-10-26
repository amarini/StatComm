TARGET = betainv
PYTHON_INC = /cvmfs/cms.cern.ch/slc6_amd64_gcc530/external/python/2.7.11-mlhled/include/python2.7
PYTHON_LIB = /cvmfs/cms.cern.ch/slc6_amd64_gcc530/external/python/2.7.11-mlhled/lib/python2.7/config
BOOST_INC = /cvmfs/cms.cern.ch/slc6_amd64_gcc530/external/boost/1.63.0-mlhled/include
BOOST_LIB = /cvmfs/cms.cern.ch/slc6_amd64_gcc530/external/boost/1.63.0-mlhled/lib

$(TARGET).so: $(TARGET).o
	g++ -shared -fPIC \
	$(TARGET).o -L$(BOOST_LIB) -lboost_python \
	-L$(PYTHON_LIB) -lpython2.7 \
	-o $(TARGET).so

$(TARGET).o: $(TARGET).cpp
	g++ -fPIC -I$(PYTHON_INC) -I$(BOOST_INC) -c $(TARGET).cpp

clean:
	rm -f *.o *.a *.so *~ core
