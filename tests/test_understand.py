from hermes.understand import UnderstoodMessage, build_understood


def test_build_understood_carries_fields():
    history = [{"role": "user", "content": "earlier"}]
    msg = build_understood(owner_id=42, text="hello", history=history)
    assert isinstance(msg, UnderstoodMessage)
    assert msg.owner_id == 42
    assert msg.text == "hello"
    assert msg.history == history
    assert msg.intent == ""


def test_history_is_copied_not_shared():
    history = [{"role": "user", "content": "earlier"}]
    msg = build_understood(owner_id=42, text="hello", history=history)
    history.append({"role": "user", "content": "mutated"})
    assert msg.history == [{"role": "user", "content": "earlier"}]
