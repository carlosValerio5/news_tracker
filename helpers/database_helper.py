from sqlalchemy.dialects.postgresql import insert
from logging import Logger

'''
Module with class methods for data base operations
'''

class DataBaseHelper:
    '''
    Helper encapsulating methods for data base operations. Targeted towards postgresql databases.
    '''

    @staticmethod
    def write_batch_of_objects(object_type, session_factory, objects_to_write: list[object], logger: Logger):
        '''
        Writes objects to data base from the suplied list of objects.

        :param object_type: The class which is mapped to the data base table
        :param session_factory: Function to create a data base session.
        :param objects_to_commit: List of objects to be written.
        '''
        try:
            with session_factory() as session:
                stmt = insert(object_type).values(objects_to_write).on_conflict_do_nothing
                result = session.execute(stmt)
                session.commit()
                logger.info(f'Keywords saved succesfully, keyword count: {result.rowcount}')
        except Exception as e:
            logger.error(f'Failed to commit objects to database.\n{e}')
            raise Exception(e)

        return result
