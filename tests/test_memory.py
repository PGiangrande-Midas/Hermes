from hermes.memory import Memory


def test_append_and_history(tmp_path):
    mem = Memory(str(tmp_path / "c.json"), cap=10)
    mem.append("user", "hi")
    mem.append("assistant", "hello")
    assert mem.history() == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]


def test_history_is_capped(tmp_path):
    mem = Memory(str(tmp_path / "c.json"), cap=2)
    mem.append("user", "a")
    mem.append("assistant", "b")
    mem.append("user", "c")
    assert mem.history() == [
        {"role": "assistant", "content": "b"},
        {"role": "user", "content": "c"},
    ]


def test_reset_clears(tmp_path):
    mem = Memory(str(tmp_path / "c.json"), cap=10)
    mem.append("user", "hi")
    mem.reset()
    assert mem.history() == []


def test_persists_across_instances(tmp_path):
    path = str(tmp_path / "c.json")
    Memory(path, cap=10).append("user", "remember me")
    reloaded = Memory(path, cap=10)
    assert reloaded.history() == [{"role": "user", "content": "remember me"}]
