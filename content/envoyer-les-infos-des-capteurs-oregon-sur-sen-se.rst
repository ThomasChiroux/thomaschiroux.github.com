Envoyer les infos des capteurs oregon sur sen.se
################################################
:date: 2011-08-12 17:18
:category: python
:tags: domotique, internet des objets, oregon, Programmation, Python, rfx-com, xpl
:lang: fr

|thgr328n| 

Depuis quelques temps, je beta-teste `sen.se`_, un site à la `pachube`_ qui est
une sorte de plate-forme pour l'internet des objets. L'objet de cet
article n'est pas (encore) de découvrir et parcourir les différents
fonctionnalités et utilisation de sen.se, mais de décrire comment j'ai
fait pour envoyer les infos de mes capteurs oregon (température,
humidité, etc..) vers la plate-forme.

Récupération des données des capteurs
=====================================

Les capteurs que j'utilise sont des sondes classiques, comme celle qu'on
peut trouver `ici`_. J'ai notamment quelques thgr328 comme celui de la
photo. Je n'utilise pas de "centrale" oregon, mais à la place un
équipement super pratique : le `rfx-com`_ qui est capable de recevoir et
décoder tout un tas de capteurs fonctionnant en 433Mhz. Du coup, on
récupère en LAN des trames venant des capteurs.

Uniformisation et décodage des trames : xpl
===========================================

Les trames venant du rfxcom sont 'brutes', directement au format de
l'émétteur (oregon ici) et pas toujours très simple à lire, du coup on
va les uniformiser dans un protocole simple et pratique : `xpl`_ Pour
gérer le xpl et décoder les trames du rfxcom, j'utilise une librairie en
perl (et oui, en perl... désolé, c'était la plus complète qui tourne sur
linux, il y d'autres libs en développements très prometteuses en python,
mais on verra plus tard :-)) pour l'instant : `xpl-perl`_.

Installation et configuration d'xpl-perl
========================================

Ci-dessous rapidement le chemin à suivre pour installer xpl-perl et le
rendre fonctionnel. Pour ce tuto, je part d'une débian squeeze vide, sur
un `sheeva-plug`_ (arm)

Installer les dépendances perl nécessaires
------------------------------------------

.. code-block:: bash

   apt-get install libconfig-yaml-perl 
   apt-get install libanyevent-perl 
   apt-get install libdatetime-format-dateparse-perl
   apt-get install libsub-name-perl 
   apt-get install librrds-perl 
   apt-get install libio-all-perl

Installer xpl-perl et ses modules
---------------------------------

Ici j'installe la version en cours de développement d'xpl-perl car elle
intègre certains patchs qui permettent de décoder correctement tous mes
capteurs, mais il est possible que son fonctionnement soit un peu
aléatoire (perso je n'ai pas rencontré de problème) Le repository
d'xpl-perl est dispo sur github 

.. code-block:: bash

   git clone https://github.com/beanz/xpl-perl.git
   cd xpl-perl
   perl Makefile.PL
   make
   make test
   make install
   cd
    
   git clone git clone -b "build/master" https://github.com/beanz/device-rfxcom-perl.git
   cd device-rfxcom-perl/
   make
   make install
   cd
    
   git clone https://github.com/beanz/anyevent-mocktcpserver-perl.git
   cd anyevent-mocktcpserver-perl/
   perl Makefile.PL
   make
   make install
   cd
    
   git clone https://github.com/beanz/anyevent-rfxcom-perl.git
   cd anyevent-rfxcom-perl/
   perl Makefile.PL
   make
   make install
   cd
    
lancer xpl-perl (mode test)
---------------------------

Pour que plusieurs modules xpl cohabitent sur une même machine, il est
nécessaire de lancer un HUB-xpl qui va récupérer les messages UDP en
broadcast sur le port 3865 et les redistribuer aux process internes, on
lance donc en premier un hub xpl, puis on lance le premier module pour
recevoir les infos du rfxcom:

.. code-block:: bash

   xpl-hub &
   /usr/bin/perl /usr/local/bin/xpl-rfxcom-rx --verbose 192.168.1.xx

Attention de bien préciser l'ip de votre rfxcom et là le module
fait son job et commence à décoder les trames rfxcom et les envoyer sur
le réseau en xpl. 

Pour vérifier que les trames sont bien transmise,
xpl-perl dispose d'un logger que l'on peut lancer pour tracer les trames:

.. code-block:: bash

   /usr/bin/perl /usr/local/bin/xpl-logger -v

qui au bout de quelques secondes me trace des infos de capteur: 

.. code-block:: bash

   192.168.1.78:49635 [xpl-stat/sensor.basic: bnz-rfxcomrx.debian -> * bthr918n.b1/temp/25.8]
   192.168.1.78:49635 [xpl-stat/sensor.basic: bnz-rfxcomrx.debian -> * bthr918n.b1/humidity/43]
   192.168.1.78:49635 [xpl-stat/sensor.basic: bnz-rfxcomrx.debian -> * bthr918n.b1/pressure/856/hPa]
   192.168.1.78:49635 [xpl-stat/sensor.basic: bnz-rfxcomrx.debian -> * bthr918n.b1/battery/60/%]
   192.168.1.78:49635 [xpl-stat/sensor.basic: bnz-rfxcomrx.debian -> * thgr328n.1a/temp/26.6]
   192.168.1.78:49635 [xpl-stat/sensor.basic: bnz-rfxcomrx.debian -> * thgr328n.1a/humidity/47]
   192.168.1.78:49635 [xpl-stat/sensor.basic: bnz-rfxcomrx.debian -> * thgr328n.1a/battery/90/%]
   
L'important ici, c'est le nom du capteur, sa mesure et la valeur. Ex pour la
première ligne : bthr918n.b1/temp/25.8 correspond donc au capteur
bthr918n.b1 qui nous envoie sa température qui est de 25,8°

Bonus: RRD et RRD graph
~~~~~~~~~~~~~~~~~~~~~~~

xpl perl vient aussi avec un module très pratique : xpl-rrd. Une fois
lancé, il se comporte comme le xpl-logger : il va récupérer
automatiquement les trames envoyées sur le réseau xpl et créer et
alimenter des bases `RRD`_, pas besoin de config, il fait tout
automatiquement. Il faut juste lui préciser un répertoire de destination
et il va créer des bases pour chaque capteur et chaque type de mesure.
ex: 

.. code-block:: bash

   /usr/bin/perl -w /usr/local/bin/xpl-rrd -v /opt/maison/xpl-rrd/ & 

Ensuite, il ne nous reste plus qu'à
grapher, et là aussi xpl-perl fournis un petit outil qui va scanner les
bases rrd et générer les graphiques et les pages html qui vont bien.
Celui-ci, il faut le lancer en cron, par exemple toute les 10 minutes:

.. code-block:: bash

   crontab -e

et placer:

.. code-block:: cron

   0,10,20,30,40,50 \* \* \* \* /usr/local/bin/xpl-rrd-graphs /opt/maison/xpl-rrd/ /opt/maison/xpl-rrd/graphs/

ainsi tous les 10 minutes, les graphs seront mis à jour. Yapuka intégrer ces pages dans
un petit site web (sous lighty par exemple, `voir un autre tuto pour
ça`_) 

|image1|

sen.se
------

Maintenant que l'on a des infos de capteurs au sein de notre réseau, il
reste à écrire un bout de soft qui récupère ces infos et les transmet à
sen.se Bon au préalable, il va vous faloir un compte chez sen.se (comme
c'est actuellement en beta, il faut demander à s'inscrire) et ensuite il
va falloir créer autant de 'devices' que vous avez de capteurs et les
flux au sein de ces devices. 

Ex ici avec un de mes capteurs oregon:
|image2| 

|image3| 

|image4| 

On récupère donc des Feed\_id, c'est ce qui
va nous permettre d'associer chaque mesure : chaque mesure de chaque
capteur sera associé à son propre feed ID. Ensuite il faut un programme
qui fait tout ça, et là on est de retour en python: j'ai écrit un bout
de programme qui va agir comme 'écouteur' du réseau xpl, récupérer les
messages, les traduire au format sen.se et les envoyer à la plate-forme.

Je ne vais pas décrire ici tout le code, mais le source est `disponible
ici sur bitbucket`_ 
Je tiens à remercier l'équipe `domogik`_ (j'y
reviendrais certainement plus tard: c'est ce projet en python qui est
très prometteur dont je parlais tout à l'heure), car j'ai récupéré du
projet la classe de décodage des message xpl: XplMessage (pourquoi
réécrire ce que d'autres ont déjà fait très bien ?). 

Mais à ce stade je n'ai pas voulu faire un plugin de domogik de mon programme car domogik
est un gros projet et je n'avais plus assez de place dans ma sheevaplug
pour le faire tenir. Du coup j'ai préféré faire un petit module autonome
pour l'instant. Il vous faudra donc récupérer le code source: 

.. code-block:: bash

   hg clone https://bitbucket.org/ThomasChiroux/py-xplsensor2net

et créer un fichier de config (en partant du devices.cfg.sample). 

.. code-block:: bash

   cd py-xplsensor2net 
   cp devices.cfg.sample devices.cfg 
   vim devices.cfg

dans ce fichier de config, pour chaque capteur oregon, on va
associer chaque mesure à un feed\_id. Ne pas oublier non plus de
préciser sa clef d'API de sen.se dans la rubrique [GENERAL] ex d'un
fichier de config: 

.. code-block:: bash

   [GENERAL]
   api_key=PUT_YOUR_API_KEY_HERE
    
   # below are the list of sensors in the form:
   # [xplsensorname]
   # name = whatever you choose
   # parameter = feed_id
   # parameter = feed_id
   # ...
    
   [thgr328n.ff]
   name=Living Room
   temp=1234
   humidity=1235
   battery=1236

le capteur thgr328n.ff a
donc 3 flux : 'temp', 'humidity' et 'battery' associés respectivement
aux feed sen.se : 1234, 1235 et 1236 ensuite, lancez le programme:

.. code-block:: bash

   python xplsensor2net.py -i a.b.c.d &

en remplaçant
a.b.c.d par l'adresse IP de la machine sur laquelle vous lancez ce
script. Et voilà c'est tout, les flux vont remonter tout seul vers
sen.se et vous pourrez en faire ce que vous voulez, comme des widgets
graphiques par exemple, mais aussi plein d'autres choses:

|image5|

.. _sen.se: http://open.sen.se/
.. _pachube: https://pachube.com/
.. _ici: http://fr.oregonscientific.com/cat-Stations-M%C3%A9t%C3%A9o-sub-Sondes-and-Accessoires.html
.. _rfx-com: http://www.rfxcom.com/receivers.htm
.. _xpl: http://en.wikipedia.org/wiki/XPL_Protocol
.. _xpl-perl: https://github.com/beanz/xpl-perl/
.. _sheeva-plug: http://fr.wikipedia.org/wiki/SheevaPlug
.. _RRD: http://www.mrtg.org/rrdtool/
.. _voir un autre tuto pour ça: http://www.chiroux.com/installation-dun-serveur-web-securise-sous-ubuntu-9-04server/
.. _disponible ici sur bitbucket: https://bitbucket.org/ThomasChiroux/py-xplsensor2net
.. _domogik: http://wiki.domogik.org/

.. |thgr328n| image:: static/media/images/thgr328n.png
.. |image1| image:: static/media/images/rrd-300x125.png
.. |image2| image:: static/media/images/sense1.png
.. |image3| image:: static/media/images/sense2.png
.. |image4| image:: static/media/images/sense3.png
.. |image5| image:: static/media/images/sense_widgets-1024x566.png
.. |image6| image:: static/media/images/thgr328n.png
