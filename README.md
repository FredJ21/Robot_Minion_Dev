# Le Projet "ROBOT MINION" ... la programmation !!!

***Introduction***

Instructions d'installation du programme

    --> Cet article est en mode DRAFT pour le moment <--

*TODO :*
- Installation de l'OS sur la carte Raspberry PI
- Configuration
- Installation des dépendances
- le programme principale



<img src="img/minion.gif" width=100px /><img src="img/minion.gif" width=150px /><img src="img/minion.gif" width=100px /><img src="img/minion.gif" width=100px /><img src="img/minion.gif" width=150px /><img src="img/minion.gif" width=100px />

---
## Carte SD & Système


#### Formatage de carte SD

On part de zéro, Formattage de la carte SD --> https://www.sdcard.org/downloads/formatter/


#### Installation de l'OS

Préparation de la carte SD, sous wimndows, à l'aide de **Raspberry Pi Imager** --> https://www.raspberrypi.com/software/

dans Raspberry Pi Imager, on sélectionne :
- le type de carte : PI 4
- l'OS  --> Raspberry PI OS (other) -->  Raspberry PI OS Lite (64-bit) **
- la carte SD cible
- dans les options de configuration : Nom machine, user/pass, conf WiFi, SSH ...


| <a href="img/pi_imager.JPG"><img src="img/pi_imager.JPG" width="100%"></a> | <a href="img/pi_imager_os_custom_1.JPG"><img src="img/pi_imager_os_custom_1.JPG" width="100%"></a> | <a href="img/pi_imager_os_custom_2.JPG"><img src="img/pi_imager_os_custom_2.JPG" width="100%"></a> |
|-----|-----|-----|



** la **version Lite** permet de bénéficier d'une verion sans l'environnement graphique de seulement 400Mo, tout est fait en CLI via SSH.

#### Connection et configuration

/!\ il faut trouver l'adresse IP de la Raspberry PI /!\

    $ ssh pi@pi19-minion-2
    pi@pi19-minion-2's password:

mise à jour système

    pi@pi19-minion-2:~ $ sudo apt update    
    pi@pi19-minion-2:~ $ sudo apt upgrade -y

installation des packages système indispensables

    pi@pi19-minion-2:~ $ sudo apt install vim git python3-pip virtualenv mpg321


Activation du service de gestion des GPIOs

    pi@pi19-minion-2:~ $ sudo systemctl enable pigpiod
    pi@pi19-minion-2:~ $ sudo systemctl start pigpiod
    pi@pi19-minion-2:~ $ sudo systemctl status pigpiod



### Dépot GIT

Récupération du dépot Git , depuis le répertoire /home/pi : 

    git clone https://github.com/FredJ21/Robot_Minion_Dev.git  MINION

    Cloning into 'MINION'...
    remote: Enumerating objects: 38, done.
    remote: Counting objects: 100% (38/38), done.
    remote: Compressing objects: 100% (31/31), done.
    remote: Total 38 (delta 7), reused 32 (delta 5), pack-reused 0
    Receiving objects: 100% (38/38), 1.30 MiB | 5.25 MiB/s, done.
    Resolving deltas: 100% (7/7), done.

Création de l'environnement virtuel Python et installation des packages

    cd MINION
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    $ chmod +x bin/minion.py
    $ chmod +x bin/play_sequence.py




TODO :
source venv/bin/activate
echo 'source ~/.autoenv/activate.sh' >> ~/.bashrc

pip freeze > requirements.txt
pip install -r requirements.txt












  ---