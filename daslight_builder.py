from gdtf_builder import build_channel_csv


def build_daslight_wolfmix_placeholder(fixture: dict) -> bytes:
    # First MVP: export a clean CSV fixture map for Daslight/Wolfmix manual fixture creation.
    # Later this module can be replaced with a native SSL2/Wolfmix exporter once the target format is finalized.
    return build_channel_csv(fixture)
