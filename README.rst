
Gino Factory
===========================

| **Install**: ``pip install gino-factory``

**Github**: https://github.com/Basalex/gino_factory

Usage:
~~~~~~~~~~~~~~~~~~

Let's create two gino models

.. code:: python

    class Team(db.Model):
        __tablename__ = 'teams'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255))

    class User(db.Model):
        __tablename__ = 'users'

        id = db.Column(db.Integer, primary_key=True)
        parent_id = db.Column(sa.Integer, sa.ForeignKey(f'users.id', name='parent_id_fkey'))
        username = db.Column(db.String(255), nullable=False, unique=True)
        custom_field = db.Column(db.String(255), nullable=False, unique=True)
        custom_factory = db.Column(db.String(255), nullable=False, unique=True)

Next you need to register this model

.. code:: python

    from gino_factory import GinoFactory

    class Factory(GinoFactory):
        pass

    Factory.register(Team)
    Factory.register(User, custom_field='value', custom_factory=function)

Single objects

.. code:: python

    async def test():
        user = await Factory.user()
        assert user.team_id is not None

        team = await Factory.test()
        user = await Factory.user(team_id=team)

        assert team.id == user.team_id

Iterator objects

.. code:: python

    from itertools import cycle

    async def test():
        teams = await Factory.cycle(10).team()
        users = await Factory.cycle(10).user(team_id=iter(teams))
        assert users[-1].team_id == teams[-1].id

        teams = await Factory.cycle(3).team()  # id: 1,2,3
        users = await Factory.cycle(10).user(team_id=cycle(teams))
        assert [u.team_id for u in users] == [1, 2, 3, 1, 2, 3, 1, 2, 3, 1]

Trees

* **Tree attributes:**
    * amount: int = 50 - maximum amount of total members
    * max_depth: int = 5 - maximum tree depth
    * top_parents_amount: int = 3 - Amount of "top" parents (parent_id=None)
    * top_parents: CRUDModel = None - Pre-generated top-parents
    * parent_field_name: str = 'parent_id' - Name of parent field

Following code generates single head tree with max depth of 3

.. code:: python

    async def test():
        users = await Factory.tree(amount=100, max_depth=3, top_parents_amount=1).user()


or you may fill your database with random data using __random__ method

.. code:: python

    await Factory.__random__()

This method inserts random data to all registered tables