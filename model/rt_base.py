import logging
import datetime
from copy import deepcopy

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Integer

from sqlalchemy import and_

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.ext.declarative import declarative_base


BaseModel = declarative_base()


class RTCommonModel(object):
    """
    支持软删除，乐观锁等功能
    """
    # 主键
    uuid = Column('uuid', String(64), primary_key=True)

    # 备注
    remark = Column('remark', String(512))

    # 创建时间
    created_at = Column('created_at', DateTime, default=datetime.datetime.now)
    # 更新时间
    updated_at = Column('updated_at', DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    # 软删除
    deleted_at = Column('deleted_at', DateTime)
    # 乐观锁
    version_id = Column(Integer, nullable=False)
    __mapper_args__ = {
        "version_id_col": version_id
    }

    @classmethod
    def get_one_from_db_by_uuid(cls, uuid, session):
        """
        从数据库获取对象
        :param uuid:
        :param session:
        :return:
        """
        try:
            one = session.query(cls).filter(
                and_(cls.deleted_at.is_(None),
                     cls.uuid == uuid)
            ).one()
        except MultipleResultsFound as e:
            logging.error(e)
            return None
        except NoResultFound as e:
            logging.error(e)
            return None
        except Exception as e:
            logging.error(e)
            return None
        else:
            return one

    @classmethod
    def get_one_from_db_by_uuid_hard(cls, uuid, session):
        """
        从数据库获取软删除的对象
        :param uuid:
        :param session:
        :return:
        """
        try:
            one = session.query(cls).filter(
                cls.uuid == uuid
            ).one()
        except MultipleResultsFound as e:
            logging.error(e)
            return None
        except NoResultFound as e:
            logging.error(e)
            return None
        except Exception as e:
            logging.warning(e)
            return None
        else:
            return one

    def to_dict(self):
        """
        将对象转化为字典
        :return:
        """
        res = dict()
        res.update()
        for field in self.__table__.columns:
            if not hasattr(field, 'name'):
                continue
            else:
                value = getattr(self, field.name)
                res[field.name] = deepcopy(value)
        return res
