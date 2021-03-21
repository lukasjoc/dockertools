#PYX_MODULE=cooldocker.pyx
PYTHON=python3

all: clean build-python-so

.PHONY: all

# build the shared object file
build-python-so:
	$(PYTHON) setup.py build_ext build_ext --inplace

clean:
	rm -rf *.so
	rm -rf build/
	rm -rf *.c
