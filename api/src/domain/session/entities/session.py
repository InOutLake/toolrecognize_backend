from datetime import datetime, timezone
from domain.shared import ID_TYPE, Domain
from pydantic import ConfigDict, Field
from domain.session import SessionStatus
from .session_tool import SessionTool
from domain.session import ToolQuantity


class Session(Domain):
    """Session is core entity in business logic.
    It tracks tools inventarization session status
    as well as tools being given and returned."""

    receiver_id: ID_TYPE
    giver_id: ID_TYPE
    location_id: ID_TYPE
    kit_id: ID_TYPE

    # Hash map simplifies process of finding whether new detection tool is already
    # exist in the session tools list
    session_tools: dict[ID_TYPE, SessionTool] = Field(default_factory=dict)

    given_image_key: str | None = None
    returned_image_key: str | None = None

    status: SessionStatus = SessionStatus.CREATED

    given_at: datetime | None = None
    returned_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls,
        receiver_id: ID_TYPE,
        giver_id: ID_TYPE,
        location_id: ID_TYPE,
        kit_id: ID_TYPE,
    ) -> "Session":
        return cls(
            receiver_id=receiver_id,
            giver_id=giver_id,
            location_id=location_id,
            kit_id=kit_id,
            session_tools={},
        )

    def preopen(self, image_key: str, detections: list[ToolQuantity]):
        """Business logic flow:
        - Aggregate given tools from detections
        - Save image
        - Update status
        """
        tools = {
            detection.tool_id: SessionTool(
                tool_id=detection.tool_id,
                quantity_given=detection.quantity,
            )
            for detection in detections
        }
        self.session_tools = tools
        self.given_image_key = image_key
        self.status = SessionStatus.OPEN_WAITING_FOR_APPROVAL

    def open(self):
        """Business logic flow:
        - Given tool set is complete and confirmed by employee
        """
        if self.status != SessionStatus.OPEN_WAITING_FOR_APPROVAL:
            raise ValueError(f"Cannot open session from {self.status}")
        self.status = SessionStatus.OPENED
        self.given_at = datetime.now(timezone.utc)

    def preclose(self, image_key: str, detections: list[ToolQuantity]):
        """Business logic flow:
        - Aggregate returned tools from detections
        - Save image
        - Update status
        """
        if self.status != SessionStatus.OPENED:
            raise ValueError(f"Cannot preclose session from {self.status}")
        for detection in detections:
            if detection.tool_id in self.session_tools.keys():
                self.session_tools[
                    detection.tool_id
                ].quantity_returned = detection.quantity
            else:
                self.session_tools[detection.tool_id] = SessionTool(
                    tool_id=detection.tool_id,
                    quantity_given=0,
                    quantity_returned=detection.quantity,
                )

        self.returned_image_key = image_key
        self.status = SessionStatus.CLOSE_WAITING_FOR_APPROVAL

    def close(self):
        """Business logic flow:
        - Returned tool set is complete and confirmed by employee
        """
        if self.status != SessionStatus.CLOSE_WAITING_FOR_APPROVAL:
            raise ValueError(f"Cannot close session from {self.status}")
        self.status = SessionStatus.CLOSED
        self.returned_at = datetime.now(timezone.utc)
