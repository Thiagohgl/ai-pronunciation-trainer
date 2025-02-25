from typing import Annotated, Optional, TypeAlias, TypedDict

import annotated_types


Category: TypeAlias = Annotated[int, annotated_types.Ge(0), annotated_types.Le(4)]
PositiveFloat: TypeAlias = Annotated[float, annotated_types.Ge(0)]


class ParsedWordInfo(TypedDict):
    word: str
    start_ts: PositiveFloat
    end_ts: PositiveFloat
