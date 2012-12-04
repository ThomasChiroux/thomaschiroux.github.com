Bonnes pratiques (?) pour l'héritage multiple en python
=======================================================
:date: 2012-12-03 00:56
:category: python
:tags: python, programmation, objet
:lang: fr
:slug: bonnes-pratiques-pour-lheritage-multiple-en-python

.. figure:: static/media/images/superman_truck.jpg
   :height: 222 px
   :width: 341 px
   :alt: Man of steel - CC - auteur: http://www.flickr.com/photos/thomashawk/2344049327/

   Man of steel - CC - `auteur <http://www.flickr.com/photos/thomashawk/2344049327/>`_

Gné ?
-----

Récemment je me suis retrouvé confronté à un problème bizarre, incompréhensible
au premier abord qui m'a fait réfléchir sur mes pratiques en python concernant
la gestion des objets de l'héritage.
Voici un état de ma réfléxion à ce sujet.

Héritage, simple, multiple et les new-style-classes
---------------------------------------------------

Depuis python 2.2 a été introduit les new-style-classes, qui héritent toutes
de object.

Par exemple, avant, c'était:

.. code-block:: python

   class Vehicule:
       pass

et maintant, on écrit (en python <= 2.7.x):

.. code-block:: python

   class Vehicule(object):
       pass

En python 2 donc, hériter de object est la marque de fabrique des new-style-classes.

.. tip::

   En python 3, on peut à nouveau écrire les classes de l'ancienne
   façon et ce seront quand même des new-styles-classes.

Je vous passe toutes les différences old-new, ce qui va nous intéresser ici
c'est la gestion de l'héritage et donc l'appel aux méthodes des classes parentes.


Prenons un exemple un peu plus complet: (les exemples ci-dessous fonctionnent en python2 et python3 (testé en 3.3))

.. code-block:: python

    class Vehicule(object):
        """Classe decrivant un vehicule
        """
        def __init__(self, nombre_de_roues, moteur, couleur):
            """Constucteur de vehicule

            Keyword arguments:
            :nombre_de_roues: (int); le nombre de roues du vehicule
            :moteur: (boolean): est-ce qu'il a un moteur ou non
            :couleur: (str): la couleur du vehicule
            """
            print('Vehicule constructor')
            self.nombre_de_roues = nombre_de_roues
            self.moteur = moteur
            self.couleur = couleur

    class Remorque(object):
        """Un conteneur d'une certaine capacite
        """

        def __init__(self, capacite):
            """Constructeur de Remorque

            Keyword arguments:
            :capacite: (float): capactite de stockage en kg
            """
            print('Remorque constructor')
            self.capacite = capacite

    class Camion(Vehicule, Remorque):
        """Un camion quoi !
        """

        def __init__(self, marque, nombre_de_roues, moteur, couleur, capacite):
            """Constuctor du Camion
            """
            print('Camion constructor')
            self.marque = marque
            self.nombre_de_roues = nombre_de_roues
            self.moteur = moteur
            self.couleur = couleur
            self.capacite = capacite

    if __name__ == '__main__':
        # on constuit un camion bleu de 35T
        mon_beau_camion = Camion('Daf', 4, True, 'bleu', 35000)

        print("Mon beau camion %s %s a %s roues et transporte %sT"
              % (mon_beau_camion.marque,
                 mon_beau_camion.couleur,
                 mon_beau_camion.nombre_de_roues,
                 mon_beau_camion.capacite / 1000))


en l'exécutant, on obtient ceci:

::

    Camion constructor
    Mon beau camion Daf bleu a 4 roues et transporte 35.0T


Cela fonctionne, mais on ne profite pas vraiment de l'héritage: on
a redéfinit dans notre constructeur de Camion ce que faisait déjà
les contructeurs de Vehicule et de Remorque.

C'est là que `super() <http://docs.python.org/2/library/functions.html#super>`_
entre en jeu: grâce à super(), on va pouvoir appeler
les constructeurs des classes parentes.


On va changer le constructeur de Camion et essayer d'appeler super():

.. code-block:: python

    class Camion(Vehicule, Remorque):
        """Un camion quoi !
        """

        def __init__(self, marque, nombre_de_roues, moteur, couleur, capacite):
            """Constuctor du Camion
            """
            print('Camion constructor')
            super(Camion, self).__init__()
            self.marque = marque

Mais on est confronté à un premier problème: super() étant super-intelligent
il va se débrouiller pour appeler les __init__ de chaque classe parente, le
tout une seule fois (voir plus bas).
Mais nos __init__ de Vehicule et Remorque n'ont pas les mêmes arguments en
entrée, donc comment va faire super ?
Testons avec l'exemple ci-dessus en ne mettant aucun argument:

::

    Camion constructor
    Traceback (most recent call last):
      File "ex2.py", line 46, in <module>
        mon_beau_camion = Camion(4, True, 'bleu', 35000)
      File "ex2.py", line 38, in __init__
        super(Camion, self).__init__()
    TypeError: __init__() missing 3 required positional arguments: 'nombre_de_roues', 'moteur', and 'couleur'


bah ouai, logique, on a appelé un constructeur qui veut 3 args avec zéro arg.

Alors comment faire ?
Si j'appelle __init__ avec les 3 args requis, j'aurais un problème quand super() appellera
le __init__ de Remorque qui n'attend qu'un seul argument.

C'est ici qu'on défini donc une première bonne pratique: l'usage de \*\*kwargs

\*\*kwargs
----------

\*\*kwargs nous permet de passer ce qu'on veut comme arguments à une fonction
(ou méthode), dans laquelle on ira piocher ce qui nous intesse:

Voici une première implémentation possible:

.. code-block:: python

    class Vehicule(object):
        """Classe decrivant un vehicule
        """
        def __init__(self, nombre_de_roues, moteur, couleur, **kwargs):
            """Constucteur de vehicule

            Keyword arguments:
            :nombre_de_roues: (int); le nombre de roues du vehicule
            :moteur: (boolean): est-ce qu'il a un moteur ou non
            :couleur: (str): la couleur du vehicule
            """
            print('Vehicule constructor')
            self.nombre_de_roues = nombre_de_roues
            self.moteur = moteur
            self.couleur = couleur

    class Remorque(object):
        """Un conteneur d'une certaine capacite
        """

        def __init__(self, capacite, **kwargs):
            """Constructeur de Remorque

            Keyword arguments:
            :capacite: (float): capactite de stockage en kg
            """
            print('Remorque constructor')
            self.capacite = capacite

    class Camion(Vehicule, Remorque):
        """Un camion quoi !
        """

        def __init__(self, marque, **kwargs):
            """Constuctor du Camion
            """
            print('Camion constructor')
            super(Camion, self).__init__(**kwargs)
            self.marque = marque

    if __name__ == '__main__':
        # on constuit un camion bleu de 35T
        mon_beau_camion = Camion(marque='Daf',
                                 nombre_de_roues=4,
                                 moteur=True,
                                 couleur='bleu',
                                 capacite=35000)

        print("Mon beau camion %s %s a %s roues et transporte %sT"
              % (mon_beau_camion.marque,
                 mon_beau_camion.couleur,
                 mon_beau_camion.nombre_de_roues,
                 mon_beau_camion.capacite / 1000))


Il y a un premier impact d'utiliser \*\*kwargs: on va devoir nommer
tous nos arguments à l'appel de la méthode.
Pour tout dire, on pourrait aussi utiliser \*args en plus de \*\*kwargs pour
récupérer les arguments non nommés, mais cela ne marcherait qu'au premier niveau
(et encore, il faut vraiment savoir ce que l'on fait), donc on va l'éviter et
s'obliger à nommer les arguments lors des appels.
C'est d'ailleurs une bonne pratique générale à toujours utiliser: cela rend
le code plus lisible

.. admonition:: Bonne pratique

   Toujours appeller une fonction ou une méthode en nommant chaque argument

Donc que se passe-t-il dans nos appels (en théorie):

1. on appelle __init__ de Camion avec 5 arguments nommés.
2. le constructeur de Camion attend lui un argument en particulier: marque
   Il va donc récupérer pour lui l'argument marque et laisser tous les autres
   dans un dict-like: kwargs
3. on appelle super() avec \*\*kwargs, du coup chaque constructeur de Vehicule et
   Remorque va récupérer les 4 arguments restant qui chacun prendrons
   ce dont ils ont besoin.

Dans cet exemple, cela devrait donc bien fonctionner.
Par contre on pourrait imaginer un exemple plus complexe ou une classe parente
aurait aussi un argument 'marque' dans son constructeur. Et là, comme marque a
été 'attrapé' par le contructeur de Camion, il ne serait pas passé aux constructeurs
Parent.
On va donc procéder d'une manière un peu moins souple, mais plus générique:
utiliser uniquement \*\*kwargs:

.. code-block:: python

    class Vehicule(object):
        """Classe decrivant un vehicule
        """
        def __init__(self, **kwargs):
            """Constucteur de vehicule

            Keyword arguments:
            :nombre_de_roues: (int); le nombre de roues du vehicule
            :moteur: (boolean): est-ce qu'il a un moteur ou non
            :couleur: (str): la couleur du vehicule
            """
            print('Vehicule constructor')
            self.nombre_de_roues = kwargs['nombre_de_roues']
            self.moteur = kwargs['moteur']
            self.couleur = kwargs['couleur']

    class Remorque(object):
        """Un conteneur d'une certaine capacite
        """

        def __init__(self, **kwargs):
            """Constructeur de Remorque

            Keyword arguments:
            :capacite: (float): capactite de stockage en kg
            """
            print('Remorque constructor')
            self.capacite = kwargs['capacite']

    class Camion(Vehicule, Remorque):
        """Un camion quoi !
        """

        def __init__(self, **kwargs):
            """Constuctor du Camion
            """
            print('Camion constructor')
            super(Camion, self).__init__(**kwargs)
            self.marque = kwargs['marque']

    if __name__ == '__main__':
        # on constuit un camion bleu de 35T
        mon_beau_camion = Camion(marque='Daf',
                                 nombre_de_roues=4,
                                 moteur=True,
                                 couleur='bleu',
                                 capacite=35000)

        print("Mon beau camion %s %s a %s roues et transporte %sT"
              % (mon_beau_camion.marque,
                 mon_beau_camion.couleur,
                 mon_beau_camion.nombre_de_roues,
                 mon_beau_camion.capacite / 1000))

Bon clairement c'est plus moche, mais c'est le moyen de correctement passer
les arguments aux méthodes des classes parentes.

Si vous maitrisez parfaitement vos APIs, vous pouvez utiliser la première méthode,
mais pour __init__ je pense qu'il vaut mieux faire comme ci-dessus.

Alors, maintenant lançons ce programme:

::

    Camion constructor
    Vehicule constructor
    Traceback (most recent call last):
      File "ex2.py", line 53, in <module>
        mon_beau_camion.capacite / 1000))
    AttributeError: 'Camion' object has no attribute 'capacite'

Merde ça ne marche pas !
Que se passe-t-il ?

On voit, avant le traceback qu'on est bien passé par le constructeur de Camion
puis celui de Vehicule. Mais c'est tout...
Où est passé le constructeur de Remorque ?
Visiblement il n'a pas été appelé.

Alors que normalement c'est le boulot de super() de bien appeler tous les
constructeursquivontbien.
Alors que ce passe-t-il ?

.. note::

    le MRO c'est quoi ?
    La signification du terme c'est: **Method Resolution Order**

    En résumé, c'est le système qu'utilise python pour passer dans chaque classe
    de l'arbre des héritages, de façon a ne passer qu'une fois dans une classe donnée
    et de manière à éviter les boucles ou les résolutions impossibles.

    L'accès au MRO calculé par python est simple, il suffit d'aller regarder __mro__
    pour une Classe donnée.

    Un bon article (en anglais) décrit le mode de calcul du MRO: `MRO description`_

Regardons donc le __mro__ de notre class Camion:

.. code-block:: python

    >>> print Camion.__mro__
    (<class '__main__.Camion'>,
     <class '__main__.Vehicule'>,
     <class '__main__.Remorque'>,
     <class 'object'>)

Dans notre exemple, python ira chercher la méthode de Camion, puis a chaque appel de super()
celle de Vehicule, Remorque et enfin object.

Alors donc pourquoi notre programme ne va pas appeler Remorque.__init__() ?
Et bien c'est parce que on a cassé l'arbre de résolution en omettant d'appeler
super() dans le constructeur de Véhicule.

Si on ajoute dans Vehicule.__init__:

.. code-block:: python

    super(Vehicule, self).__init__(**kwargs)

et que l'on relance notre programme, on obtient ceci:

::

    Camion constructor
    Vehicule constructor
    Remorque constructor
    Mon beau camion Daf bleu a 4 roues et transporte 35.0T

Cela fonctionne.
Pourtant il manque encore un appel de super() dans le constructeur de Remorque.
Ici cela ne porte pas à conséquence, car selon le mro, Remorque est le dernier appelé
avant object. Donc on a cassé la résolution mais à la toute fin.

Toutefois, si on inversait l'ordre d'héritage dans Camion en mettant:

.. code-block:: python

    class Camion(Remorque, Vehicule):

au lieu de:

.. code-block:: python

    class Camion(Vehicule, Remorque):

et que l'on relance le programme, on obtient à nouveau une erreur:

::

    Camion constructor
    Remorque constructor
    Traceback (most recent call last):
      File "ex3.py", line 51, in <module>
        mon_beau_camion.couleur,
    AttributeError: 'Camion' object has no attribute 'couleur'

En effet, nous nous arretons au constructeur de Remorque par manque de l'appel de super().

Comme nous ne pouvons pas deviner dans quel ordre un programmeur choisira de faire
hériter ses classes, il vaut donc mieux mettre l'appel à super() dans toutes les classes.

Cela donne donc le code complet suivant:

.. code-block:: python

    class Vehicule(object):
        """Classe decrivant un vehicule
        """
        def __init__(self, **kwargs):
            """Constucteur de vehicule

            Keyword arguments:
            :nombre_de_roues: (int); le nombre de roues du vehicule
            :moteur: (boolean): est-ce qu'il a un moteur ou non
            :couleur: (str): la couleur du vehicule
            """
            print('Vehicule constructor')
            super(Vehicule, self).__init__(**kwargs)
            self.nombre_de_roues = kwargs['nombre_de_roues']
            self.moteur = kwargs['moteur']
            self.couleur = kwargs['couleur']

    class Remorque(object):
        """Un conteneur d'une certaine capacite
        """

        def __init__(self, **kwargs):
            """Constructeur de Remorque

            Keyword arguments:
            :capacite: (float): capactite de stockage en kg
            """
            print('Remorque constructor')
            super(Remorque, self).__init__(**kwargs)
            self.capacite = kwargs['capacite']

    class Camion(Vehicule, Remorque):
        """Un camion quoi !
        """

        def __init__(self, **kwargs):
            """Constuctor du Camion
            """
            print('Camion constructor')
            super(Camion, self).__init__(**kwargs)
            self.marque = kwargs['marque']

    if __name__ == '__main__':
        # on constuit un camion bleu de 35T
        mon_beau_camion = Camion(marque='Daf',
                                 nombre_de_roues=4,
                                 moteur=True,
                                 couleur='bleu',
                                 capacite=35000)
        print("Mon beau camion %s %s a %s roues et transporte %sT"
              % (mon_beau_camion.marque,
                 mon_beau_camion.couleur,
                 mon_beau_camion.nombre_de_roues,
                 mon_beau_camion.capacite / 1000))

et donc au final deux bonnes pratiques supplémentaires:

.. admonition:: Bonne pratique

   Toujours ajouter \**kwargs dans les méthodes et appeler super() avec
   \**kwargs comme argument.

   Pour la méthode __init__(), si possible utiliser uniquement \**kwargs

.. admonition:: Bonne pratique

   Même pour les classes héritant directement de object, il faut
   quand même appeler super(), en particulier pour __init__().

Controverses et conclusion
--------------------------

L'utilisation de super() ne fait pas l'unanimité, notamment à cause des
contraintes décrites plus haut.

Si tout le monde (en particulier les modules qui ne sont pas les vôtres) n'utilise
pas ces 'bonnes' pratiques, alors il y a un sérieux risque de casser l'arbre en
cours de route et que votre programme ne marche pas... alors qu'à la base ce n'est
pas de votre faute.

En regardant rapidement les modules standards python, très peu utilisent aujourd'hui
super(), même en 3.3
J'imagine que c'est la même chose dans les modules de la communauté, notamment Pypi.

Du coup il faut être très vigilant lorsque vous programmez des classes a héritage
multiple avec des modules tiers. Si vous héritez d'un seul module tiers (y compris ceux de la stdlib),
mettez le en dernier: ainsi s'il casse la résolution, cela ne devrait pas porter
à conséquence.

Je pense que la controverse concernant l'utilisation de super() est justement
due à la faible utilisation de cette fonction, notamment dans les modules standard.
C'est une histoire de poule et d'oeuf.

Enfin, perso je trouve la bonne pratique d'utilisation systématique de \**kwargs
relativement peu élégante, notamment en utilisation systématique dans __init__.
Peut-être une évolution du langage à ce niveau serait souhaitable.

Si de votre côté, vous avez d'autres pratiques pour gérer ces cas, n'hésitez
pas à les proposer en commentaire.

Références
----------

* `super considered armful... or not`_
* `super considered super`_
* `MRO description`_
* `MRO history`_

.. _super considered armful... or not: https://fuhm.net/super-harmful/
.. _super considered super: http://rhettinger.wordpress.com/2011/05/26/super-considered-super/
.. _MRO history: http://python-history.blogspot.fr/2010/06/method-resolution-order.html
.. _`MRO description`: http://www.cafepy.com/article/python_attributes_and_methods/python_attributes_and_methods.html#method-resolution-order
