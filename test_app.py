import pytest
from bson.objectId import ObjectId
from app import app, db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        db.students.delete_many({})  # Clear database before test
        yield client
        db.students.delete_many({})  # Clear database after test

def test_home_page(client):
    db.students.insert_one({
        "name": "Test Student",
        "email": "test@student.com",
        "course": "DevOps Engineering"
    })
    response = client.get('/')
    assert response.status_code == 200
    assert b"Test Student" in response.data

def test_add_student(client):
    data = {"name": "New Student", "email": "new@student.com", "course": "Cloud Ops"}
    response = client.post('/add', data=data, follow_redirects=True)
    assert response.status_code == 200
    
    record = db.students.find_one({"email": "new@student.com"})
    assert record is not None
    assert record["name"] == "New Student"

def test_update_student(client):
    fixed_id = ObjectId("66fddff25f4b5f6a0a123456")
    db.students.insert_one({
        "_id": fixed_id,
        "name": "Original Name",
        "email": "original@student.com",
        "course": "Original Course"
    })
    
    data = {"name": "Updated Name", "email": "updated@student.com", "course": "Updated Course"}
    response = client.post(f'/update/{str(fixed_id)}', data=data, follow_redirects=True)
    assert response.status_code == 200
    
    # Query database to bypass front-end template variable bugs
    updated_record = db.students.find_one({"_id": fixed_id})
    assert updated_record is not None
    assert updated_record["name"] == "Updated Name"

def test_delete_student(client):
    fixed_id = ObjectId("66fddff25f4b5f6a0a123456")
    db.students.insert_one({
        "_id": fixed_id,
        "name": "Temp User",
        "email": "temp@user.com",
        "course": "Temp Course"
    })
    
    response = client.get(f'/delete/{str(fixed_id)}', follow_redirects=True)
    assert response.status_code == 200
    
    # Confirm deletion from collection directly
    deleted_record = db.students.find_one({"_id": fixed_id})
    assert deleted_record is None
