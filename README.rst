
Gino Factory
===========================

| **Install**: ``pip install gino-factory``

**Github**: https://github.com/Basalex/gino_factory

Examples of usage:
~~~~~~~~~~~~~~~~~~

Using gino model bellow

.. code:: python

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.BigInteger(), primary_key=True)
        parent_id = db.Column(db.BigInteger(), primary_key=True)
        username = db.Column(db.String(255), nullable=False, unique=True)
        custom_field = db.Column(db.String(255), nullable=False, unique=True)
        custom_factory = db.Column(db.String(255), nullable=False, unique=True)

Then, you would want to use MainRouter class

.. code:: python

    from gino_factory import GinoFactory

    class Factory(GinoFactory):
        pass

    Factory.register(User, custom_field='value', custom_factory=function)

Using in tests example:

.. code:: python

    async def test():
        user = await Factory.user()
        ten_users = await Factory.cycle(10).user()
        user_tree = await Factory.cycle(10).user()
