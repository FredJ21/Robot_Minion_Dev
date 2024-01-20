#------------------------------------------------------------------------------
#							MINION services
#													Fred J.		Janvier 2024
#------------------------------------------------------------------------------
set -x

sudo systemctl stop minion_core
sudo systemctl stop minion_web
sudo systemctl stop minion_cam
