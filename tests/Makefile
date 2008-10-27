RUNIT_DIR=$(shell pwd)

all: install test

full: build install test

install:
	cd ..; \
	python setup.py install && \
	cd ${RUNIT_DIR}

build:
	cd ${TOP}; \
	${R_CMD} CMD build ${PKG_PATH} && \
	cd ${RUNIT_DIR}

test:
	./runalltests.py

%.py: FORCE
	./$@ ${METHOD} 

FORCE:

clean:
	rm *.pdf prof

