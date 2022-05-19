
.PHONY: build

build: 
	@echo "Fuck off"
	$(MAKE) -C desktop_service/make build

install_pi:
	@echo "Hello World"

install_desktop:
	$(MAKE) -C ./desktop_service/ install

run_desktop:
	$(MAKE) -C ./desktop_service/ run
