from sqlalchemy import Column, String, Float, ForeignKey, Integer, Boolean

from .rt_base import BaseModel
from .rt_base import RTCommonModel


def default_open_time():
    return '9:00-19:00'


# 爱词霸每日一句
class IcbaSentence(BaseModel, RTCommonModel):
    __tablename__ = 'icba_sentence'
    #
    title = Column('title', String(256))
    #
    content = Column('content', String(256))
    #
    note = Column('note', String(256))
    #
    translation = Column('translation', String(256))
    #
    picture = Column('picture', String(256))
    #
    picture2 = Column('picture2', String(256))
    #
    picture3 = Column('picture3', String(256))






