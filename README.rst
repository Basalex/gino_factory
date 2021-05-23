
Gino Factory
===========================

| **Install**: ``pip install gino-factory``

**Github**: https://github.com/Basalex/gino_factory

Examples of usage:
~~~~~~~~~~~~~~~~~~

Let's create gino model

.. code:: python

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.BigInteger(), primary_key=True)
        parent_id = db.Column(db.BigInteger(), primary_key=True)
        username = db.Column(db.String(255), nullable=False, unique=True)
        custom_field = db.Column(db.String(255), nullable=False, unique=True)
        custom_factory = db.Column(db.String(255), nullable=False, unique=True)

Next you need to register this model

.. code:: python

    from gino_factory import GinoFactory

    class Factory(GinoFactory):
        pass

    Factory.register(User, custom_field='value', custom_factory=function)

And use this class for testing purposes

.. code:: python

    async def test():
        user = await Factory.user()
        ten_users = await Factory.cycle(10).user()
        user_tree = await Factory.tree().user()

or you may fill your database with random data using __random__ method

.. code:: python

    await Factory.__random__()

This method inserts random data to all registered tables