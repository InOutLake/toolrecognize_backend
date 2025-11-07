 domain.shared import ID_TYPE, Domain


class SessionTool(Domain):
    tool_id: ID_TYPE
    tool_name: str | None = None
    quantity_given: int | None = None
    quantity_returned: int | None = None
