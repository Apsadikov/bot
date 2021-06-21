import psycopg2


def init_database_connection():
    return psycopg2.connect(
        host="ec2-18-215-111-67.compute-1.amazonaws.com",
        password="c957b820b5fb90d297def602ee8e527f1123146d89c2fc033af5e6d10e34eba6",
        user="ztopumznvxdhor",
        database="dcem5c93ucaddk"
    )
