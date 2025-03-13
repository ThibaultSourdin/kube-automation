build:
	$(info ${BLUE}[*] Building ...${RESET})
	make build-lambda

build-lambda:
	$(info ${BLUE}[*] Building lambda ...${RESET})
	if [ -d ".stimio/src" ]; then rm -Rf .stimio/src; fi
	if [ -d ".stimio/build" ]; then rm -Rf .stimio/build; fi

	mkdir -p .stimio/src/lambda
	uv pip install -r requirements.txt --target .stimio/src/lambda/
	cp -R src .stimio/src/lambda
	cd .stimio/src/lambda && find . -type d -name  "__pycache__" -exec rm -r {} +
