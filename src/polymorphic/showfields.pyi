from typing import Pattern

RE_DEFERRED: Pattern[str]

class ShowFieldBase:
    polymorphic_query_multiline_output: bool
    polymorphic_showfield_type: bool
    polymorphic_showfield_content: bool
    polymorphic_showfield_deferred: bool
    polymorphic_showfield_max_line_width: None | int
    polymorphic_showfield_max_field_width: int
    polymorphic_showfield_old_format: bool

class ShowFieldType(ShowFieldBase):
    polymorphic_showfield_type: bool

class ShowFieldContent(ShowFieldBase):
    polymorphic_showfield_content: bool

class ShowFieldTypeAndContent(ShowFieldBase):
    polymorphic_showfield_type: bool
    polymorphic_showfield_content: bool
