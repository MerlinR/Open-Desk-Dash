INSTALL_PATH=/opt/opendeskdash/
SERVICE_FILE=opendeskdash.service
SYSTEMD_DIR=/etc/systemd/system
SYSTEMD_LIB_DIR=/lib/systemd/system/

.PHONY: install

install: install_deps  install_open_desk_dash install_service
	@echo "Installed Desktop Service"

install_deps:
	@echo "Installing open_desk_dash dependencies"
	python3 -m pip install -r requirements.txt

install_service:
	@echo "Install Service file"
	cp $(SERVICE_FILE) $(SYSTEMD_LIB_DIR)
	ln -s $(SYSTEMD_LIB_DIR)/$(SERVICE_FILE) $(SYSTEMD_DIR)/$(SERVICE_FILE) || true
	systemctl daemon-reload
	systemctl enable $(SYSTEMD_DIR)/$(SERVICE_FILE)
	systemctl start $(SERVICE_FILE)

install_open_desk_dash:
	@echo "Install Service open_desk_dash"
	mkdir -p $(INSTALL_PATH)
	cp -R . $(INSTALL_PATH)
	@systemctl restart $(SERVICE_FILE) || true

uninstall: uninstall_deps uninstall_open_desk_dash uninstall_service
	@echo "Uninstalled Desktop Service"

uninstall_deps:
	@echo "Uninstall open_desk_dash dependencies"
	@echo "Fuck knows how"

uninstall_service:
	@echo "Uninstall Service file"
	systemctl stop $(SERVICE_FILE)
	systemctl disable $(SERVICE_FILE)
	rm -f $(SYSTEMD_DIR)/$(SERVICE_FILE)
	rm -f $(SYSTEMD_LIB_DIR)/$(SERVICE_FILE)
	systemctl daemon-reload

uninstall_open_desk_dash:
	@echo "Uninstall Service open_desk_dash"
	rm -rf $(INSTALL_PATH)

run:
	gunicorn --workers 1 --bind 0.0.0.0:5001 --chdir ./open_desk_dash/ service:ODDash --log-level info

# chromium-browser --start-fullscreen --start-maximized http:://localhost:56970

#For me solution was to install unclutter on the client:
# sudo apt-get install unclutter

#And turn cursor off, by adding to autostart
# nano ~/.config/lxsession/LXDE/autostart

#line:
# @unclutter -idle 0.1
#It will make your coursor disappear after not moving for 0.1s, so if you want to use mouse - you still can.

# Turn display on and off
# sudo bash -c "echo 1 > /sys/class/backlight/rpi_backlight/bl_power"
# sudo bash -c "echo 0 > /sys/class/backlight/rpi_backlight/bl_power"

# Set sscreen saver timeout
# xset s 0
# xset -dpms