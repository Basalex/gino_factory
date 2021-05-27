import pytest


@pytest.mark.asyncio
async def test_tree_amount(factory):
    user_tree = await factory.tree(amount=25).user()
    assert len(user_tree) == 25


@pytest.mark.parametrize("top_parents_amount", (1, 3, 10))
@pytest.mark.asyncio
async def test_tree_top_parents_amount(factory, top_parents_amount):
    users = await factory.tree(top_parents_amount=top_parents_amount, amount=50).user()
    assert len([u for u in users if u.parent_id is None]) == top_parents_amount
    assert len(users) == 50


@pytest.mark.asyncio
async def test_tree_max_depth(factory):
    users = await factory.tree(max_depth=3, amount=100).user()
    users_dict = {u.id: u.parent_id for u in users}
    max_depth = 0
    for user in users:
        if user.parent_id is None:
            continue
        depth = 0
        last_parent_id = user.parent_id
        while True:
            last_parent_id = users_dict[last_parent_id]
            if last_parent_id is not None:
                depth += 1
            else:
                break
        if depth > max_depth:
            max_depth = depth

    assert max_depth == 3


@pytest.mark.asyncio
async def test_tree_custom_parents(factory):
    users = await factory.cycle(5).user()
    user_tree = await factory.tree(top_parents=users).user()
    assert not ({u.id for u in users} - {u.parent_id for u in user_tree})
