from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta, datetime, timezone
import jwt
from typing import Optional

# These imports come from the new helper files to prevent circular import crashes
from schemas import Userlogin, UserRegister, TokenResponse, PredictionResponse, AuthenticatedPredictionRequest
from ml_utils import get_prediction

# Configurations
SECRET_KEY = 'Sample_key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTE = 30

# Security Scheme
security = HTTPBearer()
auth_router = APIRouter()

# Fake Database (Keys now match usernames so login works)
fake_users_db = {
    "saksham": {
        'username': 'saksham',
        'password': 'Bodybulking@96',
        'disabled': False
    },
    "user1": {
        'username': 'user1',
        'password': 'user1pass',
        'disabled': False
    }
}

# --- Utility Functions ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def authentication_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or user['password'] != password:
        return None
    return user

# --- Routes ---

@auth_router.post('/register', response_model=TokenResponse)
async def register_user(user: UserRegister):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already entered")
    
    fake_users_db[user.username] = {
        'username': user.username,
        'password': user.password,
        'disabled': False
    }
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)
    access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)
    
    return {
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE_MINUTE * 60
    }

@auth_router.post('/login', response_model=TokenResponse)
async def login(user: Userlogin):
    user_data = authentication_user(user.username, user.password)
    if not user_data:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)
    access_token = create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)
    
    return {
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE_MINUTE * 60
    }

@auth_router.post('/predict/auth', response_model=PredictionResponse)
async def predict_auth(request: AuthenticatedPredictionRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    # 1. Verify the token
    username = verify_token(credentials.credentials)
    print(f"User {username} accessed the prediction endpoint")
    
    # 2. Make prediction safely using the utils file
    try:
        # We pass the customer data as a dictionary to the prediction utility
        result = get_prediction(request.customer.model_dump())
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))