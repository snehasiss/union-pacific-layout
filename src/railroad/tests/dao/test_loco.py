from railroad.dao.loco import LocoDAO


def test_loco_dao_can_be_created() -> None:
    dao = LocoDAO()

    assert isinstance(dao, LocoDAO)

