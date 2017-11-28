import logging
import datetime
import uuid
import json

from tornado.httpclient import AsyncHTTPClient
from sqlalchemy import and_, desc, union_all

from model import *

async def sync_acba_sentence(Session):
    try:
        session = Session()
        begin_date = datetime.datetime(2017, 11, 20)
        end_date = datetime.datetime(2017, 11, 28)
        while begin_date <= end_date:
            date = begin_date.strftime('%Y-%m-%d')
            sentence = await acba_sentence(date)
            if not sentence:
                logging.info('获取信息失败')
                continue

            title = sentence.get('title', None)
            content = sentence.get('content', None)
            note = sentence.get('note', None)
            translation = sentence.get('translation', None)
            picture = sentence.get('picture', None)
            picture2 = sentence.get('picture2', None)
            picture3 = sentence.get('picture3', None)

            query = session.query(
                IcbaSentence
            ).filter(
                IcbaSentence.title == title
            )
            query_result = query.one_or_none()
            if not query_result:
                item = IcbaSentence()
                item.uuid = str(uuid.uuid1())
                item.title = title
                item.content = content
                item.note = note
                item.translation = translation
                item.picture = picture
                item.picture2 = picture2
                item.picture3 = picture3
                session.add(item)
            begin_date = begin_date + datetime.timedelta(days=1)
        session.commit()
        return
    except Exception as e:
        logging.error(e)
        session.rollback()
        return None
    finally:
        session.close()


async def acba_sentence(date, try_times=3):
    url = 'http://sentence.iciba.com/index.php?&c=dailysentence&m=getdetail&title=%s' % date
    print(url)
    try:
        http_client = AsyncHTTPClient()
        for i in range(try_times):
            response = await http_client.fetch(url)
            response = json.loads(response.body)
            code = response.get('errno')
            if code != 0:
                logging.error('获取信息失败')
            else:
                break
        return response
    except Exception as e:
        logging.error(e)
        return None
    finally:
        http_client.close()

