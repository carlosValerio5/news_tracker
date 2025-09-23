from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
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
    def write_batch_of_objects_and_return(object_type, session_factory, objects_to_write: list[object], logger: Logger, return_columns: list=None, conflict_index: list= None) -> list:
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
                    # Update is undesired, but returning is still needed for repeated rows
                    dummy_col = list(object_type.__table__.primary_key.columns)[0].name
                    stmt = stmt.on_conflict_do_update(
                        index_elements=conflict_index,
                        set_={dummy_col: getattr(object_type.__table__.c, dummy_col)} # does not update
                    )

                if return_columns:
                    stmt = stmt.returning(*return_columns)

                result = session.execute(stmt)
                session.commit()

                if return_columns:
                    rows = list(result)
                    logger.info(f'Keywords saved successfully, keyword count: {len(rows)}')
                    return [dict(row._mapping) for row in rows]

                logger.info(f'Keywords saved succesfully, keyword count: {result.rowcount}')
                return result
        except Exception as e:
            logger.error(f'Failed to commit objects to database.\n{e}')
            raise 

    @staticmethod
    def write_orm_objects(objects_to_write: list, session_factory, logger):
        '''
        Writes a single sqlalchemy object to db.

        :param objects_to_write: List of objects to write.
        :param session_factory: Factory function to create a data base session.
        :param logger: Logger object to handle logging logic.
        '''
        try:
            with session_factory() as session:
                session.add_all(objects_to_write)
                session.commit()
        except Exception:
            logger.error(f"Failed to write object to database.")
            raise

    @staticmethod
    def check_database_connection(session_factory, logger):
        '''
        Checks the database connection.

        :param session_factory: Factory method to create a data base connection.
        :param logger: Logger object to handle logging logic.
        '''

        try:
            with session_factory() as session:
                session.execute('SELECT 1')
        except (SQLAlchemyError):
            logger.error('Connection to data base failed.')
            raise

