from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from password_manager import PasswordManager
import uuid

app = FastAPI()

# Instantiate PasswordManager
password_manager = PasswordManager()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define pydantic models
class UserRegistration(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordEntry(BaseModel):
    website: str
    username: str
    password: str

class PasswordUpdate(BaseModel):
    website: str
    username: str
    new_password: str

# Helper function to get session
def get_session_id(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=403, detail="No session ID found")
    return session_id

# Route to register a new user
@app.post("/register")
def register(user: UserRegistration):
    if not password_manager.register_user(user.username, user.password):
        raise HTTPException(status_code=400, detail="User already exists")
    return {"message": "User registered successfully"}

# Route for user login (returns a session cookie)
@app.post("/login")
def login(user: UserLogin, response: Response):
    session_id = password_manager.login_user(user.username, user.password)
    if session_id is None:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    response.set_cookie(key="session_id", value=session_id, httponly=False)
    return {"message": "Login successful", "session_id": session_id}

# Route to log out a user
@app.post("/logout")
def logout(request: Request, response: Response):
    session_id = get_session_id(request)
    password_manager.logout_user(session_id)
    response.delete_cookie("session_id")
    return {"message": "Logout successful"}

# Route to add a password entry (requires session)
@app.post("/add-password")
def add_password(password_entry: PasswordEntry, request: Request):
    session_id = get_session_id(request)
    if not password_manager.validate_session(session_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    success = password_manager.add_password(password_entry.website, password_entry.username, password_entry.password)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add password")
    return {"success": True, "message": "Password added successfully"}

# Route to get all password entries (requires session)
@app.get("/get-passwords")
def get_passwords(request: Request):
    session_id = get_session_id(request)
    if not password_manager.validate_session(session_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    passwords = password_manager.get_all_passwords()
    if passwords is None:
        raise HTTPException(status_code=404, detail="No passwords found")
    return {"passwords": passwords}

# Route to update an existing password (requires session)
@app.put("/update-password")
def update_password(password_update: PasswordUpdate, request: Request):
    session_id = get_session_id(request)
    if not password_manager.validate_session(session_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    success = password_manager.update_password(password_update.website, password_update.username, password_update.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update password")
    return {"success": True, "message": "Password updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", port=5000, reload=True)
