import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import boto3
from botocore.exceptions import ClientError

# DynamoDB config
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("users")  # Change "users" to your table name

app = FastAPI()

class User(BaseModel):
    name: str
    email: EmailStr

class UserOut(User):
    user_id: str

@app.post("/users/", response_model=UserOut)
def create_user(user: User):
    user_id = str(uuid.uuid4())
    item = {"user_id": user_id, "name": user.name, "email": user.email}
    try:
        table.put_item(Item=item)
        return {**item}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: str):
    try:
        resp = table.get_item(Key={"user_id": user_id})
        item = resp.get("Item")
        if not item:
            raise HTTPException(status_code=404, detail="User not found")
        return item
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, user: User):
    try:
        # Only update name and email
        table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set #n=:n, email=:e",
            ExpressionAttributeNames={"#n": "name"},
            ExpressionAttributeValues={":n": user.name, ":e": user.email}
        )
        item = {"user_id": user_id, "name": user.name, "email": user.email}
        return item
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    try:
        table.delete_item(Key={"user_id": user_id})
        return {"message": "User deleted"}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))


for i in range(5):
    print("Hi")
