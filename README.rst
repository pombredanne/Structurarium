Structurarium
--------------

Structurarium is a set of networked databases written in Python

Here is the list of available databases:

  - *structurarium.memo*: In memory dictionnary, with options to make it
                          persistent, easily customised with changes only
                          needed server side thanks to a smart (yet simple)
                          client and a plugin system.
  - *structurarium.taskqueue*: Also known as the persistent set. ``add`` a document,
                          ``pop`` it later.
  - *structurarium.graph*: A presistent database supported by a graph
                           datastructure similar to `Neo4j <http://neo4j.org/>`_
                           or `OrientDB <http://www.orientechnologies.com/>`_.


Getting started
~~~~~~~~~~~~~~~

::

  ~ pip install Structurarium
  ~ structurarium.graph  127.0.0.1 8000 /tmp

In a Python REPL::

  >>> from structurarium.graph.client.graph import Graph
  >>> db = Graph(address=('127.0.0.1', 8000))
  >>> one = db.Vertex()
  >>> one.save()
  >>> two = db.Vertex()
  >>> two.save()
  >>> edge = db.Edge(one, two)
  >>> edge.save()
  >>> loaded_one = db.load(one.identifier)
  >>> queried_two = loaded_one.outgoings().end().object()


That is all.

Links
-----

 - https://github.com/amirouche/Structurarium
