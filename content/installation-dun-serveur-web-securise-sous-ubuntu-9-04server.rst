Installation d'un serveur web sécurisé sous Ubuntu server (9.04 à 10.04)
########################################################################
:date: 2009-08-18 00:58
:category: Administration Système
:tags: 9.04, configuration, installation, jaunty, lighttpd, linux, mysql, php, ubuntu
:slug: installation-dun-serveur-web-securise-sous-ubuntu-9-04server
:lang: fr

.. image:: media/images/ubuntu-logo.png
   :height: 100 px
   :width: 105 px
   :alt: ubuntu logo

Cet article est le premier d'une série sur l'admin
système linux. On va donc commencer par les bases : installer un ubuntu
server avec une sécurité correcte et on en profite pour installer un
LLMP dessus (c'est LAMP mais avec Lighttpd à la place de apache :-))
Pour ce tuto, j'ai choisi d'utiliser `un serveur virtuel de chez gandi`_
: je profite d'une offre d'été qui propose un serveur gratuit pendant un
mois. J'avais beta testé cette offre il y a un an et demi, mais les trop
gros problèmes d'accès disque (lenteurs notamment) m'avaient incité à
partir prendre un RPS chez OVH. Maintenant la situation change : l'offre
de gandi est plus mûre (et l'archi disque a notamment changée : c'est
maintenant du SAS directement sur les serveurs) et les `RPS d'ovh vont
disparaitre`_. Je vais donc profiter de cette installation pour faire
quelques benchs sur l'offre gandi et voir si je (re)bascule dessus ou
pas ensuite. En attendant, voici de quoi installer le serveur

Du côté de gandi
----------------

-  Administration / Hebergement : cliquer sur créer un serveur
-  Valider le nombre de parts
-  Choisir Installation expert et Ubuntu 9.04
-  Choisir un hostname, un nom d'utilisateur et un mot de passe [si
   possible, choisir un nom de user non standard, pour améliorer la
   sécurité]
-  Valider, et attendre le mail de confirmation avec l'@IP du serveur
-  Ensuite, on peut se connecter en SSH sur le serveur avec le login et
   pass entré juste avant.

Ajouter un disque de données :

-  sur l'interfance gandi, onglet Gestion des disque, cliquer sur Créer
   un disque
-  choisir un nom pour le disque, la taille souhaitée et le filesystem
-  enfin, une fois le disque créé, cliquer sur le petit logo 'link'
   attacher le disque à un serveur
-  choisir le serveur et valider
-  le volume est dynamiquement ajouté au serveur dans
   /srv/nomduvolumechoisi

Organiser les users
-------------------

Le login créé (ici: testuser) n'est pas par défaut dans la liste des
sudoers, donc pas de sudo possible. Le mot de passe root par défaut est
le même que celui du user testuser

On va donc d'abord autoriser le sudo pour testuser :
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

en tant que root : 

.. code-block:: bash

   visudo

et ajouter à la fin du fichier: 

.. code-block:: bash

   # Members of the admin group may gain
   root privileges %admin ALL=(ALL) ALL 

Ensuite on va ajouter testuser dans le groupe admin :
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

toujours en tant que root : 

.. code-block:: bash

   usermod -G admin testuser

Enfin on change le mot de passe root
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

en tant que root:

.. code-block:: bash

   passwd

et entrer un bon mot de passe bien sécurisé A partir de maintenant, sauf mention
spécifique, le reste des commandes sera réalisée avec le user testuser

Mise à jour du système
----------------------

Afin de démarrer sur un système tout propre 

.. code-block:: bash
   
   sudo apt-get update sudo apt-get upgrade

Installer et configurer de quoi bien travailler
-----------------------------------------------

pour 9.04
~~~~~~~~~

.. code-block:: bash

   sudo apt-get install vim-python

pour 10.04
~~~~~~~~~~

.. code-block:: bash

   sudo apt-get install vim-nox

puis 

.. code-block:: bash

   vim ~/.vimrc [/code] 

et coller le texte suivant: 

.. code-block:: bash

   syntax on
   set number
   set background=dark
   set tabstop=2
   set shiftwidth=2
   set softtabstop=2
   set expandtab
   set autoindent
   autocmd BufRead *.py set smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class
   autocmd BufWritePre *.py normal m`:%s/\s\+$//e ``
   map <F12> :set number!<CR>
   map <F10> :set paste!<CR>

enfin : 

.. code-block:: bash

   vim ~/.bashrc 

et vers la fin du fichier, décommenter les 3 lignes suivantes: 
**mise à jour:** cette étape n'est plus nécessaire en 10.04 

.. code-block:: bash
   
   alias ll='ls -l' 
   alias la='ls -A' 
   alias l='ls -CF'

L'heure et ntp
~~~~~~~~~~~~~~

Dans mon système livré par gandi, l'heure est par défaut en heure UTC,
si on veut la mettre à l'heure locale (Paris, France pour moi): 

.. code-block:: bash

   sudo dpkg-reconfigure tzdata 

et choisir : Europe,
puis Paris 

Pour NTP : [édit: Comme le remarque justement Daniel dans les
commentaires, paramétrer ntp pour un serveur virtuel n'est
vraisemblablement pas nécessaire car il va hériter de la date de son
hôte. Je laisse ici l'info au cas où votre serveur n'est pas un
hébergement gandi] 

.. code-block:: bash

   sudo vim /etc/cron.daily/ntpdate

et coller les commandes suivantes: 

.. code-block:: bash

   #!/bin/sh
   #On lance une synchro ntp 
   ntpdate fr.pool.ntp.org

enfin 

.. code-block:: bash

   sudo chmod a+x /etc/cron.daily/ntpdate

Ainsi notre serveur resynchronisera son horloge tous les jours automatiquement.

Sécurité
--------

ssh : autoriser uniquement certains users en ssh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ici, on va limiter le ssh uniquement pour notre user : testuser

.. code-block:: bash

   sudo vim /etc/ssh/sshd\_config

Bien vérifier que dans la zone 'Authentication' on a bien: 

.. code-block:: bash

   PermitRootLogin without-password

sinon modifier le paramètre.
ensuite, en bas du fichier, ajouter: 

.. code-block:: bash

   # Allow only a certain list of users 
   AllowUsers testuser

**Attention, il faut
être vigilant en insérant cette ligne : une erreur dans le nom du user
interdirait toute connexion ultérieure en ssh et bloquerait l'accès au
serveur. Il est conseillé de garder sa session actuelle ouverte et de
tester une nouvelle connexion supplémentaire pour bien vérifier qu'on
puisse encore se connecter.**

On recharge la config ssh 

.. code-block:: bash

   sudo /etc/init.d/ssh reload

Fail2ban
~~~~~~~~

Fail2ban analyse les logs (ssh notament) et banni les IP qui attaque en
force brute sur ssh via des configurations automatiques dans iptables.

.. code-block:: bash

   sudo apt-get install fail2ban

modification des paramètres de fail2ban: 

.. code-block:: bash

   sudo vim /etc/fail2ban/jail.conf 

pour ma part, j'ai juste changé deux
paramètres : le bantime et le nombre d'essais : 

.. code-block:: bash

   bantime = 1800 
   maxretry = 3 

.. code-block:: bash

   sudo /etc/init.d/fail2ban restart

IPtables
~~~~~~~~

Iptable a été installé avec fail2ban, on va maintenant le configurer
pour nos applications Pour cela, on va créer un fichier de commande qui
se lancera au boot du serveur et que l'on peut relancer à volonté pour
reconfigurer le firewall.

.. code-block:: bash

   sudo vim /etc/init.d/server\_iptables 

et coller les commandes suivantes :

.. code-block:: bash

   #!/bin/bash
   # reset iptables
   iptables -F
 
   # Autorise les connections sortantes et sur l'interface "loopback"
   iptables -P OUTPUT ACCEPT
   iptables -A INPUT -i lo -j ACCEPT
   iptables -A INPUT -d 127.0.0.0/8 -i ! lo -j DROP
 
   # Autorise les connections deja etablies
   iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
 
   # Autorise HTTP, SSH, ICMP-ping
   iptables -A INPUT -p tcp -i eth0 --dport ssh -j ACCEPT
   iptables -A INPUT -p tcp -i eth0 --dport 80 -j ACCEPT
   iptables -A INPUT -p icmp -i eth0 -j ACCEPT
 
   #  Refuse a priori ce qui vient de l'exterieur
   iptables -P INPUT DROP
   iptables -P FORWARD DROP

Ensuite on le rend executable et on l'installe au boot:

.. code-block:: bash

   sudo chmod +x /etc/init.d/server_iptables
   sudo update-rc.d server_iptables defaults

Sécuriser le kernel
~~~~~~~~~~~~~~~~~~~

ça doit être lié à Xen, mais le kernel de gandi est assez ancien (à la
date de cet article c'est un 2.6.18, alors que le kernel en cours est un
2.6.28 On va modifier quelques paramètres du kernel pour le rendre plus
solide aux attaques Ici, il faut se mettre directement en root pour que
ces commandes passent: 

.. code-block:: bash

   sudo su

Se protéger contre les Smurf Attack:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

celui ci est déjà bon dans l'install que j'ai testé: 

.. code-block:: bash

   echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts

Eviter le source routing:
^^^^^^^^^^^^^^^^^^^^^^^^^

celui ci est déjà bon dans l'install que j'ai testé: 

.. code-block:: bash

   echo "0" > /proc/sys/net/ipv4/conf/all/accept_source_route

Se protéger des attaques de type Syn Flood:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

celui ci est déjà bon dans l'install que j'ai testé: [

.. code-block:: bash

   echo "1" > /proc/sys/net/ipv4/tcp_syncookies 
   echo "1024" > /proc/sys/net/ipv4/tcp_max_syn_backlog 
   echo "1" > /proc/sys/net/ipv4/conf/all/rp_filter

Désactiver l’autorisation des redirections ICMP:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   echo "0" > /proc/sys/net/ipv4/conf/all/accept_redirects
   echo "0" > /proc/sys/net/ipv4/conf/all/secure_redirects

Eviter le log des paquets icmp erroné:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

celui ci est déjà bon dans l'install que j'ai testé: 

.. code-block:: bash

   echo "1" > /proc/sys/net/ipv4/icmp_ignore_bogus_error_responses

Active le logging des packets aux adresses sources falficiées ou non routables:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   echo "1" > /proc/sys/net/ipv4/conf/all/log_martians

on quitte le user root 

.. code-block:: bash

   exit

Installation Lighttpd et php
----------------------------

.. code-block:: bash

  sudo apt-get install lighttpd 
  sudo apt-get install php5-cgi 
  sudo apt-get install php5-mysql 
  sudo lighty-enable-mod cgi 
  sudo /etc/init.d/lighttpd force-reload

edit le fichier de conf de lighttpd et ajouter le mod fastcgi: 

.. code-block:: bash

   sudo vim /etc/lighttpd/lighttpd.conf

les modules activés sont les suivants (j'ai mis mod\_rewrite et mod\_redirect en plus, car cela sert
toujours finalement)

.. code-block:: bash

   server.modules = (
               "mod_access",
               "mod_alias",
               "mod_accesslog",
               "mod_compress",
               "mod_fastcgi",
               "mod_rewrite",
               "mod_redirect",
   #           "mod_evhost",
   #           "mod_usertrack",
   #           "mod_rrdtool",
   #           "mod_webdav",
   #           "mod_expire",
   #           "mod_flv_streaming",
   #           "mod_evasive"
   )

puis aller chercher
dans le fichier la variable : server.dir-listing et la passer à disable: 

.. code-block:: bash

   server.dir-listing = "disable"

Installation Mysql
------------------

.. code-block:: bash

   apt-get install mysql-server-5.0

Quand il le
demande, entrer un mot de passe root pour mysql (choisir un vrai mot de
passe bien sécurisé) On va 'forcer' l'utf8 partout : 

.. code-block:: bash

   sudo vim /etc/mysql/conf.d/caractersencoding.cnf

et coller la
configuration suivante: 

.. code-block:: bash

   [mysqld]
     #Set the default character set.
     default-character-set=utf8
     #Set the default collation.
     default-collation=utf8_general_ci
     #   
     character-set-server=utf8
     skip-character-set-client-handshake
     init-connect='SET NAMES utf8'

on redémarre pour vérifier que tout est bon 

.. code-block:: bash

   sudo /etc/init.d/mysql restart

Mysql est maintenant installé
dans ses répertoires par défaut, et notamment les bases seront crées
dans /var/lib/mysql 

[ceci est une spécificité liée à l'installation
gandi, vous pouvez passer ce point si votre serveur est 'normal']

/var/lib est dans le disque 'système' de gandi qui fait uniquement 3Go.
En fonction de ce qu'on prévoi de faire avec son serveur mysql, il est
peut-etre judicieux de le déplacer sur le disque de données: 

.. code-block:: bash

   sudo /etc/init.d/mysql stop 
   sudo mv /var/lib/mysql /srv/nomdurepertoiregandi/mysql 
   sudo ln -s /srv/nomdurepertoiregandi/mysql /var/lib/mysql 
   sudo /etc/init.d/mysql start

Configuration de lighttpd pour un site de test
----------------------------------------------

Afin de voir si tout va bien, on va créer un site de test

.. code-block:: bash

   sudo mkdir /srv/nomdurepertoiregandi/www 
   sudo chown www-data:www-data /srv/nomdurepertoiregandi/www 
   sudo -u www-data mkdir /srv/nomdurepertoiregandi/www/sitetest1

ensuite on va configurer lighty: 

.. code-block:: bash

   sudo vim /etc/lighttpd/lighttpd.conf

ajouter sous la conf des modules: 

.. code-block:: bash

   # Config pour sitetest
   $HTTP["host"] == "111.111.111.111" {
        server.document-root       = "/srv/nomdurepertoiregandi/www/sitetest1/"
  
        # FAST CGI POUR PHP
        fastcgi.server = ( ".php" => ((
                            "bin-path" => "/usr/bin/php-cgi",
                            "socket" => "/tmp/php.socket",
                            "max-procs" => 1,
                            "bin-environment" => (
                                "PHP_FCGI_CHILDREN" => "4",
                                "PHP_FCGI_MAX_REQUESTS" => "10000"
                            ),
                            "bin-copy-environment" => (
                                "PATH", "SHELL", "USER"
                            ),
                            "broken-scriptfilename" => "enable"
        )))
   }

en remplaçant l'ip
111.111.111.111 par l'ip ou le nom de domaine du site que vous voulez
ajouter ensuite on redémarre lighty

.. code-block:: bash

   sudo /etc/init.d/lighttpd restart

mettre un fichier de test
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo -u www-data vim /srv/nomdurepertoiregandi/www/sitetest1/testinfo.php

et coller le code suivant: 

.. code-block:: php

  <?php phpinfo(); ?>

et voilà, le site est normalement accessible sur l'IP (ou le nom de
domaine) que vous avez précisé dans la conf et l'url (en prenant mon
exemple ci-dessus) : http://111.111.111.111/testinfo.php affiche toutes
les infos de php.

Conclusion
----------

On a maintenant un serveur ubuntu jaunty prêt à fonctionner, léger et
sécurisé. Il prends peu de ressources, très peu de ram et pourra servir
de base aux reste des tutos à venir.

.. _un serveur virtuel de chez gandi: https://www.gandi.net/hebergement/
.. _RPS d'ovh vont disparaitre: http://forum.ovh.com/showthread.php?t=49747

