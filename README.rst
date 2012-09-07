GraphitiDB
----------

Structurarium is a set of networked databases written in Python, compatible
with PyPy.

Here is the list of available databases:

  - *structurarium.memo*: In memory dictionnary, with options to make it
                          persistent, easily customised with changes only
                          needed server side thanks to a smart (yet simple)
                          client and a plugin system.
  - *structurarium.pset*: Also known as the persistent set. ``add`` a document,
                          ``pop`` it later.
  - *structurarium.graph*: A presistent database supported by a graph
                           datastructure similar to `Neo4j <http://neo4j.org/>`
                           or `OrientDB <http://www.orientechnologies.com/>`.


Getting started
~~~~~~~~~~~~~~~

::

  ~ pip install Structurarium
  ~ structurarium.graph --password supersecret
  Strucurarium's Graph is running on /tmp/tmp8a4qds9d1qs23

In a Python REPL::

  >>> from structurarium.databases.graph import Rex as Rex
  >>> rex = Rex('supersecret', address='/tmp/tmp8a4qds9d1qs23')
  >>> one = rex.create_node()
  >>> one.save()
  >>> two = rex.create_node()
  >>> two.save()
  >>> edge = rex.create_edge(one, two)
  >>> edge.save()
  >>> loaded_one = rex.load(n1.identifier)
  >>> queried_two = loaded_n2.outgoings().end().object()


That is all.

Links
-----

 - structurarium-project.com
 - forge
