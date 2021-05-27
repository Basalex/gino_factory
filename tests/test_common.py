import pytest


@pytest.mark.asyncio
async def test_single_object(factory):
    user = await factory.user()
    assert user.id is not None
    assert user.team_id is not None


@pytest.mark.asyncio
async def test_single_object_with_fk(factory):
    team = await factory.team()
    user_1 = await factory.user(team_id=team)
    user_2 = await factory.user(team_id=team.id)
    assert user_1.team_id == team.id
    assert user_2.team_id == team.id


@pytest.mark.asyncio
async def test_cycle(factory):
    teams = await factory.cycle(10).team()
    assert len(teams) == 10


@pytest.mark.asyncio
async def test_cycle_fk_iterator(factory):
    teams = await factory.cycle(10).team()
    users = await factory.cycle(10).user(team_id=iter(teams))
    assert [t.id for t in teams] == [user.team_id for user in users]
