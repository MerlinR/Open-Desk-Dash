INSTALL_PATH=/opt/opendeskdash/
SERVICE_FILE=opendeskdash.service
SYSTEMD_DIR=/etc/systemd/system
SYSTEMD_LIB_DIR=/lib/systemd/system/

.PHONY: install

install: install_deps  install_app install_service
	@echo "Installed Desktop Service"

install_deps:
	@echo "Installing App dependencies"
	python3 -m pip install -r requirements.txt

install_service:
	@echo "Install Service file"
	cp $(SERVICE_FILE) $(SYSTEMD_LIB_DIR)
	ln -s $(SYSTEMD_LIB_DIR)/$(SERVICE_FILE) $(SYSTEMD_DIR)/$(SERVICE_FILE) || true
	systemctl daemon-reload
	systemctl enable $(SYSTEMD_DIR)/$(SERVICE_FILE)
	systemctl start $(SERVICE_FILE)

install_app:
	@echo "Install Service App"
	mkdir -p $(INSTALL_PATH)
	cp -R service/* $(INSTALL_PATH)
	@systemctl restart $(SERVICE_FILE) || true

uninstall: uninstall_deps uninstall_app uninstall_service
	@echo "Uninstalled Desktop Service"

uninstall_deps:
	@echo "Uninstall App dependencies"
	@echo "FUck knows how"

uninstall_service:
	@echo "Uninstall Service file"
	systemctl stop $(SERVICE_FILE)
	systemctl disable $(SERVICE_FILE)
	rm -f $(SYSTEMD_DIR)/$(SERVICE_FILE)
	rm -f $(SYSTEMD_LIB_DIR)/$(SERVICE_FILE)
	systemctl daemon-reload

uninstall_app:
	@echo "Uninstall Service App"
	rm -rf $(INSTALL_PATH)

run:
	gunicorn --workers 1 --bind 0.0.0.0:5001 --chdir ./app/ service:app --log-level debug