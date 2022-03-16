from cgi import test
import time
from turtle import pos
from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
# For Schema
from pydantic import BaseModel
# Driver for connecting with database (Postgres)
import psycopg2
from psycopg2.extras import RealDictCursor
# random num
from random import randrange
app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


# Database Connection
while True:
    try:
        """cursor_factory will give both column name and values, otherwise it will only give values """
        conn = psycopg2.connect(
            host='localhost', database='fastapi', user='postgres', password="root", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database Connected")
        break

    except Exception as error:
        print("Connection to db failed")
        print(error)
        # Wait for 5 seconds before trying to connect
        time.sleep(5)


@app.get("/")
async def root():
    return{"message": "Hello World!!!!"}


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM old_posts""")
    posts = cursor.fetchall()
    print(posts)
    return{"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
# post is the variable in which we store the data entered by the user
# Post is the schema name
# post has access to the values present in the POST
def create_posts(post: Post):
    cursor.execute("""INSERT INTO old_posts(title,content,published) VALUES(%s, %s,%s) RETURNING*""",
                   (post.title, post.content, post.published))
    # To get the return value from the database, it is not enough to just use the RETURNIN* statement.
    # The below code should be used to get the value back
    new_post = cursor.fetchone()
    # Saving the changes to database
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
# We have access to the id because we are using it in /posts/{id}
# {id} is known as path parameter, path parameters are converted to strings by default
# id:int means, I am expecting an integer. This is given by fast api
def get_post(id: int, response: Response):

    cursor.execute("""SELECT * from old_posts where id= %s""", (str(id)))
    post = cursor.fetchone()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id : {id}, not found")

    return{"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(
        """DELETE FROM old_posts where id = %s returning *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id : {id}, does not exist")


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content= %s, published= %s WHERE id =%s RETURNING*""", (post.title, post.content, post.published, str(id),))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id : {id}, does not exist")

    return {"data": updated_post}
