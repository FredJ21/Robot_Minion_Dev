#------------------------------------------------------------------------------
#                              MINION services
#                                                       Fred J.  Janvier 2024
#------------------------------------------------------------------------------

sudo systemctl stop minion_core
sudo systemctl stop minion_web
sudo systemctl stop minion_cam

sudo systemctl disable minion_core
sudo systemctl disable minion_web
sudo systemctl disable minion_cam

sudo cp minion_core.service /etc/systemd/system
sudo cp minion_web.service /etc/systemd/system
sudo cp minion_cam.service /etc/systemd/system

sudo systemctl enable minion_core
sudo systemctl enable minion_web
sudo systemctl enable minion_cam

sudo systemctl start minion_core
sudo systemctl start minion_web
sudo systemctl start minion_cam

sudo systemctl status minion_core
sudo systemctl status minion_web
sudo systemctl status minion_cam
