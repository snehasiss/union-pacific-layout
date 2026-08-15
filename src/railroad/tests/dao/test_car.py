from railroad.dao.car import CarDAO


def test_car_dao_can_be_created() -> None:
    dao = CarDAO()

    assert isinstance(dao, CarDAO)

