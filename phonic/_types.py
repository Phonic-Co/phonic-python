from typing_extensions import Literal

PhonicSTSTool = Literal["send_dtmf_tone", "end_conversation"]


class _NotGivenType:
    """Sentinel class for distinguishing None from not given."""

    def __repr__(self) -> str:
        return "NOT_GIVEN"


NOT_GIVEN = _NotGivenType()
NotGiven = _NotGivenType
