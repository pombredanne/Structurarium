Structurarium
-------------

**This is under developpement use it at your own risks**

Structurarium is a set of networked databases written in Python

Here is the list of available databases:

  - *structurarium.memo*: In memory dictionnary, with options to make it
    persistent, easily customised with changes only needed server side 
    thanks to a smart (yet simple) client and a plugin system.
  - *structurarium.taskqueue*: Also known as the persistent set. ``add`` a 
    document, ``pop`` it later.
  - *structurarium.graph*: A presistent shema-less database supported by a graph
    datastructure similar to `Neo4j <http://neo4j.org/>`_
    or `OrientDB <http://www.orientechnologies.com/>`_;


Getting started
~~~~~~~~~~~~~~~

::

  ~ pip install Structurarium
  ~ structurarium.graph  127.0.0.1 8000 /tmp

In a Python REPL::

  >>> from structurarium.graph.client.graph import Graph
  >>> db = Graph(address=('127.0.0.1', 8000))
  >>> bleu = db.Vertex()
  >>> bleu.save()
  >>> MachineTranslation = db.Vertex()
  >>> machine_translation.save()
  >>> link = db.Edge(bleu, machine_translation)
  >>> link.save()

You can also save the above subgraph in one ``save()`` because they are
all connected::


  >>> from structurarium.graph.client.graph import Graph
  >>> db = Graph(address=('127.0.0.1', 8000))
  >>> bleu = db.Vertex()
  >>> MachineTranslation = db.Vertex()
  >>> machine_translation.save()
  >>> link = db.Edge(bleu, machine_translation)
  >>> link.save()

You can get edges and vertices with ``db.get(identifier)``::

  >>> bleu = db.get(bleu.identifier)

Fetch the element with ``bleu.identifier`` as identifier. The
same method can be used for both edge and vertex.

Then you have access to 4 kinds of queries:

 - ``query()`` will start a query starting from this element
 - ``outgoings()`` will query outgoing edges on vertex
 - ``incomings()`` will query incoming edges on vertex

The following example query for the edge outgoing from ``bleu``::

  >>> link = bleu.outgoings().object()

Every query should end with ``object()`` or ``objects()`` depending 
whether you want one object or several.

You can fetch both ends of the link, this triggers a new query:

  >>> machine_translation = link.end()

The same can be achieved with a chained query::

  >>> link = bleu.outgoings().end().object()

It's also possible to get and set properties on the elements::

  >>> link.kind = 'hyperlink'
  >>> link.save()
  >>> link = bleu.outgoings().object()
  >>> link.kind
  'hyperlink'

Don't forget to have a look at the documentation.

Links
-----

 - https://github.com/amirouche/Structurarium
