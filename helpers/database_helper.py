from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, text
from sqlalchemy import select, update
from logging import Logger

from database.models import Users
from exceptions.auth_exceptions import GoogleIDMismatchException, UserNotFoundException

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
                logger.info(f'Keywords saved succesfully, keyword count: {result.rowcount}', extra={'keywords':objects_to_write})
        except Exception as e:
            logger.error(f'Failed to commit objects to database.', extra={'error': e})
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
                    logger.info(f'Keywords saved succesfully, keyword count: {len(rows)}', extra={'keywords':objects_to_write})
                    return [dict(row._mapping) for row in rows]

                logger.info(f'Keywords saved succesfully, keyword count: {result.rowcount}', extra={'keywords':objects_to_write})
                return result
        except Exception as e:
            logger.error(f'Failed to commit objects to database.', extra={'error':e})
            raise 

    @staticmethod
    def write_orm_objects(objects_to_write: list|object, session_factory, logger):
        '''
        Writes a single sqlalchemy object to db.

        :param objects_to_write: List of objects or single object to write.
        :param session_factory: Factory function to create a data base session.
        :param logger: Logger object to handle logging logic.
        '''
        list_of_objects = []
        if not isinstance(objects_to_write, list):
            objects_to_write = [objects_to_write]

        list_of_objects.extend(objects_to_write)
        try:
            with session_factory() as session:
                session.add_all(list_of_objects)
                session.commit()
        except Exception as e:
            logger.error("Failed to write object to database.", extra={'error':e})
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
                session.execute(text('SELECT 1'))
        except (SQLAlchemyError) as e:
            logger.exception('Connection to data base failed.', extra={'error':e})
            raise

    @staticmethod
    def check_or_create_user(user_info: dict, session_factory, logger):

        stmt = select(Users).where(Users.google_id == user_info["sub"])
        try:
            with session_factory() as session:
                user = session.execute(stmt).scalars().first()
                if user:
                    logger.info(f"User found: {user_info['sub']}")
                    user.last_login = func.now()
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    return DataBaseHelper.orm_object_to_dict(user)
    
                stmt = select(Users).where(Users.email == user_info["email"])
                existing_user = session.execute(stmt).scalars().first()
                if existing_user:
                    logger.error(f"Google ID and email mismatch: {user_info['email']}")
                    raise GoogleIDMismatchException(f"Google ID and email mismatch: {user_info['email']}")


                # User not found, create new user
                insert_stmt = insert(Users).returning(Users).values({
                    "google_id": user_info["sub"],
                    "email": user_info["email"],
                    "role": "u"
                })
                new_user = session.execute(insert_stmt).scalars().first()
                session.commit()
                logger.info(f"Created new user: {user_info['email']}")
                return DataBaseHelper.orm_object_to_dict(new_user)
        except SQLAlchemyError as e:
            logger.exception("Error checking or creating user.", extra={"error": e})
            raise
        except Exception as e:
            logger.exception("Unexpected error checking or creating user.", extra={"error": e})
            raise

    @staticmethod
    def orm_object_to_dict(orm_object) -> dict:
        '''
        Converts a sqlalchemy orm object to a dictionary.

        :param orm_object: The sqlalchemy orm object to convert.
        '''
        if not orm_object:
            return {}

        return {column.name: getattr(orm_object, column.name) for column in orm_object.__table__.columns}

    @staticmethod
    def create_admin(email: str, session_factory, logger):
        '''
        Creates an admin user in the database.

        :param email: Email address of the admin user.
        :param session_factory: Factory method to create a data base connection.
        :param logger: Logger object to handle logging logic.
        '''
        try:
            with session_factory() as session:
                stmt = update(Users).where(Users.email == email).values(role='a').returning(Users)
                result = session.execute(stmt)
                session.commit()
                updated_user = result.scalars().first()
                if updated_user:
                    logger.info(f"User {email} promoted to admin.")
                    return DataBaseHelper.orm_object_to_dict(updated_user)
                else:
                    logger.warning(f"User {email} not found.")
                    raise UserNotFoundException(f"User {email} not found.")
        except SQLAlchemyError as e:
            logger.exception("Error promoting user to admin.", extra={"error": e})
            raise
        except Exception as e:
            logger.exception("Unexpected error promoting user to admin.", extra={"error": e})
            raise