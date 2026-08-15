from railroad.dao.mow import MowDAO


def test_mow_dao_can_be_created() -> None:
    dao = MowDAO()

    assert isinstance(dao, MowDAO)

