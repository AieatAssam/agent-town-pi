"""affect_core plugin for Agent Town. The CLIs' Stop hooks book every finished visit as a reply,
but a visit's last message is a note to nobody. Residents run `acted` themselves after each real post,
so a hook-finished turn only consolidates."""


def register(core):
    core.on("pre_turn_update", lambda core, turn: {**turn, "kind": "skip"})
