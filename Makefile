
.PHONY: build

build: 
	@echo "Fuck off"
	$(MAKE) -C desktop_service/make build

install_pi:
	$(MAKE) -C ./pi_app/ install

run_pi:
	$(MAKE) -C ./pi_app/ run

install_desktop:
	$(MAKE) -C ./desktop_service/ install

run_desktop:
	$(MAKE) -C ./desktop_service/ run
