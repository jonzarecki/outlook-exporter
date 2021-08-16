from contextlib import contextmanager

import pandas as pd
from sqlalchemy import Column, String
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from utils.config import DB_ENGINE

Base = declarative_base()


class ConvIdToExportName(Base):  # type: ignore
    __tablename__ = "conv_id_to_export_name"
    conversation_id = Column(String, primary_key=True, unique=True, nullable=False)
    exported_name = Column(String)


Base.metadata.create_all(DB_ENGINE)

_Session = sessionmaker(bind=DB_ENGINE)


@contextmanager
def get_session() -> Session:
    """Returns a session object with commit/rollback functionality as a context."""
    session = _Session()
    try:
        yield session
        session.commit()
    except Exception:  # noqa
        session.rollback()
        raise
    finally:
        session.close()


def get_export_name(conversation_id: str) -> str:
    """Returns a safe name for export, if one exists in the DB. returns "" if it doesn't.

    Args:
        conversation_id: unique id for the meeting
    """
    ret_df = pd.read_sql(
        f"""
        select {ConvIdToExportName.exported_name.name} as name
        from {ConvIdToExportName.__tablename__} where {ConvIdToExportName.conversation_id.name}='{conversation_id}'
        """,
        con=DB_ENGINE,
    )

    if len(ret_df) != 0:
        return ret_df.iloc[0]["name"]  # type: ignore
    return ""


def upsert_export_name(conversation_id: str, export_name: str) -> None:
    """Update/Insert an export name of the given conversation_id.

    Args:
        conversation_id: unique id for the meeting
        export_name: name to export for conv
    """
    with get_session() as sess:
        insert_stmt = insert(ConvIdToExportName).values(conversation_id=conversation_id, exported_name=export_name)
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[ConvIdToExportName.conversation_id.name], set_=dict(exported_name=export_name)
        )
        sess.execute(upsert_stmt)

    assert (
        get_export_name(conversation_id) == export_name
    ), f"{get_export_name(conversation_id)} == {export_name}\n {upsert_stmt}"


if __name__ == "__main__":
    # test
    new_exp_name = "abc"
    upsert_export_name("b", new_exp_name)
    retrieved_exp_name = get_export_name("b")
    assert new_exp_name == retrieved_exp_name, "should be the same"
