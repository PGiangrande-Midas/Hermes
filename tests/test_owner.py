from hermes.owner import Owner


def test_owner_unset_initially(tmp_path):
    owner = Owner(str(tmp_path / "owner.json"))
    assert owner.is_set() is False
    assert owner.is_owner(123) is False


def test_register_then_recognises_owner(tmp_path):
    owner = Owner(str(tmp_path / "owner.json"))
    owner.register(123)
    assert owner.is_set() is True
    assert owner.is_owner(123) is True
    assert owner.is_owner(999) is False


def test_owner_persists_across_instances(tmp_path):
    path = str(tmp_path / "owner.json")
    Owner(path).register(123)
    reloaded = Owner(path)
    assert reloaded.is_owner(123) is True
