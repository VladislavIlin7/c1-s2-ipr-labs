from src.storage import get_quadrant


def test_do_now_quadrant():
    assert get_quadrant(True, True) == "do_now"


def test_schedule_quadrant():
    assert get_quadrant(True, False) == "schedule"


def test_delegate_quadrant():
    assert get_quadrant(False, True) == "delegate"


def test_delete_quadrant():
    assert get_quadrant(False, False) == "delete"
