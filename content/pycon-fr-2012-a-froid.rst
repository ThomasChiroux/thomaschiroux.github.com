Ce qui a changé dans ma pratique après PyCon FR 2012
====================================================
:date: 2012-12-12
:category: python
:tags: python, programmation
:lang: fr
:slug: temp
:status: draft

Comme je n'avais pas eu le temps d'écrire directement après Pycon FR, j'ai
pris le parti de regarder, presque 3 mois après la manifestation
ce j'ai changé, appris ou simplement utilisé.

Voici donc bon bilan à froid du Pycon FR 2012

Ce qui a changé directement dans ma façon de coder
--------------------------------------------------

logging
*******

Merci à Feth qui a mis le doigt sur une mauvaise pratique souvent utilisée:

Au lieu d'invoquer logging de cette façon:

.. code-block:: python

    logging.debug('message : %s' % info)

il faut préférer ainsi:

.. code-block:: python

    logging.debug('message : %s', info)

Honnêtement c'est dur de se l'appliquer tous les jours tellement j'ai le réflexe du '%'.
Mais au moins en relecture de code je le corrige à présent.

Virtualenvwrapper
*****************

Je ne sais même plus s'il y a une presentation spécifiquement dessus, c'est peut-être
en préparant le sprint que je m'y suis mis.
Auparavant, j'utilisais mes virtualenv à la main:

.. code-block:: python

    virtualenv myvenv
    source myvenv/bin/activate

et maintenant:

.. code-block:: python

    mkvirtualenv myvenv
    workon myvenv

Vu comme ça, on se dit que bof, cela ne change pas grand chose et c'est ce que
je me disais aussi... avant de m'y mettre vraiment.

En fait, à l'usage au jour le jour, cela change vraiment.

* le fait que tous les venv soient bien rangés dans ton ~/.virtualenv rend les choses
  beaucoup plus clean: pas besoin de gitignorer ton venv dans ton repo, rend plus
  simple l'usage d'un même virtualenv sur plusieurs projets connexes, etc...
* les hooks preactivate et postactivate (et les équivalents deactivate)
  permettent de lancer des actions en arrivant (ou ressortant) d'un virtual env.
  La plupart du temps je les utilise pour me placer dans le bon répertoire de developpement.


en allant plus loin
^^^^^^^^^^^^^^^^^^^

`autoenv`_ permet de faire en plus simple: on active un virtualenv simplement
en allant dans un répertoire.

.. warning:: Attention toutefois de ne pas cumuler `autoenv`_ et les scripts
   postactivate: vous risquez d'entrer dans une boucle infinie: le postactivate
   vous place dans le répertoire (cd xxx) et du coup le hook de autoenv s'excute
   et va essayer de charger le virtualenv... qui va changer de répertoire, etc..


Packaging
*********

Le packaging en python, c'est un serpent... de mer.
Plein d'outils existants, une cible:`distutils2`_ (?), mais pas utilisable à ce jour.

En préparant le sprint, j'ai passé un peu de temps à nettoyer et organiser
mes setups, notamment pour `dipplanner`_
Perso j'utilise setuptools et donc un fichier setup.py et honnêtement
j'aurais du mal à m'en passer, notamment parce que j'utilise des fonctions
qui numérotent automatiquement mes builds basés sur les tags et les commits
mercurial et git.
En distutils2, je ne sais pas comment faire ça.
(un article spécial "ma recette de setup" est à venir)

Pendant le Pycon, il y a eu une présentation intéressante sur `tooth.paste`_
je l'ai un peu utilisé, mais au final comme cela génère un projet tout simple
qui ne contient pas mes spécificités, je continue à me cloner un projet vide
pour en démarrer un nouveau.


ReadTheDoc
**********

Pour dipplanner, j'ai basculé la `doc <http://dipplanner.readthedocs.org/en/latest/>`_
sur `readthedoc`_, ce qui me permet de bénéficier de la génération automatique
de la doc à chaque push grâce aux hooks de github. C'est super pratique.


Ce que j'ai changé au boulot
----------------------------

fabric & co
***********

La présentation sur `fabtools`_ a été un déclencheur qui à la fois m'a fait
creuser le sujet et développer les premières recettes utilisant fabric et les
outils associés.

Et en creusant, je me suis aussi mis à utiliser `cuisine`_ qui est également
un outils qui vient au dessus de fabric et qui est relativement complémentaire
à fabtools.

Du coup j'utilise maintenant les 3 et j'aime cette façon de déployer qui est plus
bas niveau qu'un `puppet`_ par exemple mais qui me permet de mieux maitriser ce que je fait.
(et en plus c'est en python).

Ce que je n'ai pas encore eu le temps de faire
----------------------------------------------

circus
******

Nous utilisons au boulot une sorte de supervisord mais développé en custom car
nous avions des besoins particuliers (xmpp, watchdog spécifique, etc...)

Il me parait intéressant de regarder circus de plus prêt et de voir comment on
pourrait juste ajouter les 2/3 fonctionnalités manquantes pour pouvoir basculer
sur cette solution plus standard.

Pour l'instant je n'ai pas eu le temps de m'y pencher mais c'est dans la todolist.


network-enabled unittests
*************************

Ce Pycon m'a mis en tête de trouver des façons simples de faire des tests
unitaires pour des application network-enabled (http ou, en particulier, sockets)


Pymite sur stm32f4
******************

On a juste gratté la surface d'un python embarqué avec l'atelier
de `jon1012 <http://www.twitter.com/jon1012>`_ sur
`Pymite`_, et depuis je n'ai plus eu le temps de continuer.

Il faudrait vraiment collectivement qu'on trouve un peu de temps à passer sur
ce projet qui est vraiment prometteur.


Divers
------

impress.js
**********

Pas mal de présentation étaient réalisées avec `impress.js`_ et je me suis dit
en sortie de conférence qu'il serait sympa d'avoir un outils ReST -> impress.js

Le temps de me l'écrire dans *ma todo list d'un jour si j'ai le temps*, que
`gawel <http://twitter.com/gawel_>`_ avait réalisé le projet: http://gawel.github.com/impress/

Il est donc maintenant possible d'écrire ses slides en ReST très proprement
et d'obtenir une super présentation sous impress.js. Merci à lui !


Références
----------

* `autoenv`_
* `distutils2`_
* `tooth.paste`_
* `fabric`_
* `fabtools`_
* `cuisine`_
* `circus`_
* Pymite sur stm32f4

  * `Pymite`_ official repository
  * `les slides de l'atelier <http://www.slideshare.net/jonathanschemoul/atelier-pymite-sur-stm32f4-pyconfr-2012>`_
  * https://bitbucket.org/tuck/pymite_stm32f4


Autres résumés de la Pycon FR 2012 avec plein de liens vers les confs:

* http://yjost.com/de-retour-de-la-pyconfr.html
* http://tech.novapost.fr/pyconfr-2012-a-la-villette-le-resume.html

.. _autoenv: https://github.com/kennethreitz/autoenv
.. _distutils2: http://packages.python.org/Distutils2/
.. _tooth.paste: https://github.com/maikroeder/tooth.paste
.. _dipplanner: http://dipplanner.org
.. _fabric: http://fabfile.org
.. _fabtools: https://github.com/ronnix/fabtools
.. _cuisine: https://github.com/sebastien/cuisine
.. _circus: https://github.com/mozilla-services/circus
.. _readthedoc: https://readthedocs.org/
.. _puppet: http://puppetlabs.com/
.. _atelier de jon1012:
.. _Pymite: http://code.google.com/p/python-on-a-chip/
.. _impress.js: http://bartaz.github.com/impress.js/#/bored
