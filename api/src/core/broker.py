from typing import Annotated

from fastapi import Depends
from .settings import SETTINGS
from faststream.rabbit import RabbitBroker

broker = RabbitBroker(SETTINGS.rabbit_url)


def get_broker():
    return broker


BrokerDep = Annotated[RabbitBroker, Depends(get_broker)]

