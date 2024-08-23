import codecs
import constants
import json
import logging
import psycopg2
import typing


def get_db_connection() -> psycopg2.extensions.connection:
    logging.info("Connecting to %s on %s:%s", constants.DB_NAME, constants.DB_HOST, constants.DB_PORT)
    return psycopg2.connect(
        dbname=constants.DB_NAME,
        user=constants.DB_USER,
        password=constants.DB_PASS,
        host=constants.DB_HOST,
        port=constants.DB_PORT
    )


def get_vectors() -> typing.Tuple[typing.List[int], typing.List[typing.List[float]]]:
    with codecs.open("movie_recommender/movie_vectors.txt", "r", encoding="utf-8", errors="ignore") as movie_vectors_fh:
        lines: typing.List[str] = movie_vectors_fh.readlines()

        # Example vector:
        # 1:[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 43.17698669433594, 0.0, 0.0, 0.0, 6.857442855834961, 0.0, 0.0, 0.0, 0.0, ...
        _ids: typing.List[int] = [int(line.split(":")[0]) for line in lines]
        _embeddings: typing.List[typing.List[float]] = []
        for line in lines:
            _embeddings.append(json.loads(line.strip().split(":")[1]))
        return _ids, _embeddings
