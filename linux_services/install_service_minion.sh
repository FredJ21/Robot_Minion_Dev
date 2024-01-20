#------------------------------------------------------------------------------
#							MINION services
#													Fred J.		Janvier 2024
#------------------------------------------------------------------------------


sudo cp *.service /etc/systemd/system

sudo systemctl enable minion_core
sudo systemctl enable minion_web
sudo systemctl enable minion_cam

sudo systemctl start minion_core
sudo systemctl start minion_web
sudo systemctl start minion_cam

sudo systemctl status minion_core
sudo systemctl status minion_web
sudo systemctl status minion_cam
