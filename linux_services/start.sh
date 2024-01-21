#------------------------------------------------------------------------------
#                                 MINION services
#                                                       Fred J.   Janvier 2024
#------------------------------------------------------------------------------

set -x

sudo systemctl start minion_core
sudo systemctl start minion_web
sudo systemctl start minion_cam
