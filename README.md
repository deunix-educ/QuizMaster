# QuizMaster (SeriousGame)
QuizMaster est un SeriousGame de  questions / réponses

Ici n'est présenté que la partie maître et joueurs sur nano pc (raspberry pi) et mobiles<br>
A l'origine il était conçu pour fonctionner avec un matériel IOT qu'il sera aisé de rajouter:

 - un processeur ESP8266 d1-mini
 - un écran OLED monochrome 0.96"
 - 6 à 8 boutons de commande
 - 1 batterie de 9000 mAh et chargeur
    
### Description
QuizMaster est un SeriousGame ou un questionnaire permettant de tester les connaissances d'un groupe d'utilisateur.<br>
Le maître dispose d'une console de commande pour envoyer les questions et réceptionne les réponses en temps réel.<br>
Les joueurs disposent d'un matériel connecté (IOT), d'un mobile, d'un portable ou tout autre PC.<br>
QuizMaster est une application écrite entièrement en python django sous license MIT.<br>
La maintenance et et la mise à jour des questions se fait exclusivement à partir de l'administration django.<br>


### REQUIS
Matériels:
- Joueurs:<br>
    Mobiles ou portable, pc.
    
- Maître:<br>
    Pc (Raspberry pi 3, 4, 5) avec point d'accès éventuellement.<br>
    Serveur mosquitto 


### INSTALATION
Exemples de configuration dans etc/conf.<br>
Les serveurs peuvent s'installer dans le réseau local ou public (ssl). On préférera une installation locale<br>
Se reporter au fichier quizmaster/help.install.txt qui détaille les procédures.


- Télécharger le code [ici](https://github.com/deunix-educ/QuizMaster)

        tar xzfv QuizMaster-main.zip
        ou
        git clone git@github.com:deunix-educ/QuizMaster.git
        cd quizmaster
        chmod +x etc/bin/*.sh
        chmod +x quizmaster/*.py
        
- Installer d'abord les packages système

        sudo apt -y install build-essential openssl git pkg-config binutils supervisor mosquitto sqlite3
        sudo cp /etc/supervisor/supervisord.conf /etc/supervisor/supervisord.conf.old
        sudo cat >> /etc/supervisor/supervisord.conf << EOF
        [inet_http_server]
        port=*:9001
        username=root
        password=toor
        EOF    
    
- configurer les serveurs<br>
                    
        mosquitto: adapter etc/conf/mosquitto-local.conf
            sudo cp etc/conf//mosquitto-local.conf /etc/mosquitto/conf.d/
      
        quizmaster: Adapter etc/conf/quiz-service.conf
            sudo cp etc/conf/quiz-service.conf /etc/supervisor/conf.d/
            sudo supervisorctl reread 

        Editer et Configurer les variables d'environnement automation/.env-example
        Configurer correctement les utilisateurs et les mots de passe (superadmin, quizmaster, quizbox)
            cp quizmaster/.env-example quizmaster/.env 
            
        Créer l'environnement python (.venv)
            etc/bin/venv-install.sh etc/install/requirements.txt            
            cd quizmaster
            ./manage.py makemigrations
            ./manage.py migrate
            ./manage.py initapp
            ./manage.py loaddata ../etc/install/quizmaster.json

### Usage
Les accès http://ip.quizmaster/ avec un login/mot de passe

- Machine quizmaster:<br>
    Lancer les services mqttcd et quizmaster (supervisor http://127.0.0.1:9001)

        Accès admin: superadmin
        Accès maître: quizmaster

- Machines des joueurs:<br>
    Elles se connectent au réseau, ou mieux au point d'accès de la machine quizmaster

        Accès jeux: quizbox
