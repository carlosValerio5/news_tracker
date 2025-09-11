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
                stmt = insert(object_type).values(objects_to_write).on_conflict_do_nothing()
                result = session.execute(stmt)
                session.commit()
                logger.info(f'Keywords saved succesfully, keyword count: {result.rowcount}')
        except Exception as e:
            logger.error(f'Failed to commit objects to database.\n{e}')
            raise Exception(e)


    @staticmethod
    def write_batch_of_objects_returning(object_type, session_factory, objects_to_write: list[object], logger: Logger, return_columns: list=None, conflict_index: list= None) -> list:
        '''
        Writes objects to data base from the suplied list of objects returning the specified columns.

        :param object_type: The class which is mapped to the data base table
        :param session_factory: Function to create a data base session.
        :param objects_to_commit: List of objects to be written.
        :param return_columns: List of columns to return.
        :param conflict_index: List of index elements that make conflicts.
        '''
        try:
            with session_factory() as session:
                stmt = insert(object_type).values(objects_to_write)

                if conflict_index:
                    # Update is undesired, but returning is still neded for repeated rows
                    dummy_col = list(object_type.__table__.primary_key.columns)[0].name
                    stmt = stmt.on_conflict_do_update(
                        index_elements=conflict_index,
                        set_={dummy_col: getattr(insert(object_type).excluded, dummy_col)} # does not update
                    )

                if return_columns:
                    stmt = stmt.returning(*return_columns)

                result = session.execute(stmt)
                session.commit()

                logger.info(f'Keywords saved succesfully, keyword count: {result.rowcount}')
                if return_columns:
                    return [dict(row) for row in result]
                return result
        except Exception as e:
            logger.error(f'Failed to commit objects to database.\n{e}')
            raise 

