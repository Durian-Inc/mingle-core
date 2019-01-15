"""All models for the application are exported here"""
from .BaseModel import BaseModel
from .User import User
from .AuthId import AuthId
from .Theme import Theme
from .Chat import Chat
from .Participation import Participation

tables = [User, AuthId, Chat, Participation, Theme]
