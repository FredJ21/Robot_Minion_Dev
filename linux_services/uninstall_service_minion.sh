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

