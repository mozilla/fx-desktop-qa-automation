"""
Agreed DTE-5557 decisions for adapting STARfox suite conftests to the Firefox tree.

Everything else is decided from the inventory: a suite fixture whose code is
identical to the Firefox root fixture it would shadow is dropped, and the rest
is kept.
"""

# Fixtures whose consumer is gone in the Firefox tree, with the reason they go.
DROP = {
    "hard_quit": "replaced by the Firefox driver's dom.disable_beforeunload default",
}

# STARfox root fixtures that only one suite needs, copied into that suite.
MOVE_TO_SUITE = {
    # Keeps the Faker data password_manager generates identical to STARfox's.
    "faker_seed": ["password_manager"],
}
