import logging
import psycopg2
import constants
import util
import sys
import typing

logging.getLogger().setLevel(logging.INFO)

def main():
    args = sys.argv[1:]
    assert len(args) == 1
    conn: psycopg2.extensions.connection = util.get_db_connection()
    ourdb = conn.cursor()
    query_movie_id: int = int(args[0])
    ids, embeddings = util.get_vectors()
    embedding_mapping: typing.Dict[int, typing.List[float]] = dict(zip(ids, embeddings))

    ourdb.execute(f"SELECT * FROM {constants.MOVIES_TABLE_NAME} WHERE id={query_movie_id};")
    results = ourdb.fetchall()
    logging.info("Input query: %s, %s", results[0][1], results[0][2])

    # Compels PostgreSQL to use the custom index
    ourdb.execute("SET enable_seqscan = false;")
    ourdb.execute(f"SELECT id, title, genres FROM {constants.MOVIES_TABLE_NAME} WHERE id != {query_movie_id} ORDER BY vector <-> ARRAY{embedding_mapping[query_movie_id]} LIMIT 10;")
    results = ourdb.fetchall()
    for result in results:
        logging.info("Similar movie: %s, %s", result[1], result[2])

    conn.commit()
    ourdb.close()

if __name__ == "__main__":
    main()
