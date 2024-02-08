#------------------------------------------------------------------------------
#                              MINION services
#                                                       Fred J.  Janvier 2024
#------------------------------------------------------------------------------

sudo systemctl stop minion_checkWiFi

sudo systemctl disable minion_checkWiFi

sudo cp minion_checkWiFi.service /etc/systemd/system

sudo systemctl enable minion_checkWiFi

sudo systemctl start minion_checkWiFi

sudo systemctl status minion_checkWiFi
