import codecs
import constants
import logging
import psycopg2
import typing
import util

logging.getLogger().setLevel(logging.INFO)

conn: psycopg2.extensions.connection = util.get_db_connection()

ourdb: psycopg2.extensions.cursor = conn.cursor()

ourdb.execute("DROP TABLE movies;")
conn.commit()

ourdb.execute("SELECT EXISTS(SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME=%s)", (constants.MOVIES_TABLE_NAME,))
movies_table_exists: bool = ourdb.fetchone()[0]

if not movies_table_exists:
    logging.info("Table %s does not exist, creating it", constants.MOVIES_TABLE_NAME)
    ourdb.execute(f"CREATE TABLE {constants.MOVIES_TABLE_NAME} (id integer, title text, genres text, vector real[]);")

    ids, embeddings = util.get_vectors()
    embedding_mapping: typing.Dict[int, typing.List[float]] = dict(zip(ids, embeddings))
    dimensions: int = len(embeddings[0])
    logging.info("Found %s embeddings with dimensionality %s", len(embedding_mapping), dimensions)

    with codecs.open("movie_recommender/movies.dat", "r", encoding="utf-8", errors="ignore") as movies_data_fh:
        for line in movies_data_fh.readlines():
            if len(line.strip()) == 0:
                continue
            # Example data:
            # 1::Toy Story (1995)::Animation|Children's|Comedy
            movie_data = line.strip().split("::")
            id = int(movie_data[0])
            title = movie_data[1]
            genres = movie_data[2]

            corresponding_embedding = embedding_mapping[id]
            ourdb.execute(f"INSERT INTO {constants.MOVIES_TABLE_NAME} (id, title, genres, vector) VALUES (%s, %s, %s, %s);", (id, title, genres, corresponding_embedding,))
    conn.commit()
    # Construct index using Lantern Hierarchical Navigable Small Worlds algo
    # Use L2-norm for distance
    logging.info("Creating L2 Norm index on %s", constants.MOVIES_TABLE_NAME)
    ourdb.execute(f"CREATE INDEX ON {constants.MOVIES_TABLE_NAME} USING hnsw (vector dist_l2sq_ops) WITH (dim={dimensions});")
else:
    logging.info("Table %s already exists, will skip initialization", constants.MOVIES_TABLE_NAME)

logging.info("Terminating db connection")
conn.commit()
ourdb.close()
