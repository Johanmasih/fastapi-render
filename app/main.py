
"""
Design a FastAPI endpoint for cardless withdrawals that validates an 8-character alphanumeric transaction_code,
    6-digit atm_pin_code (with external service validation and retry on 500 errors), 
    and an amount between 100-1000 in multiples of 100, while ensuring proper error handling 
    and security best practices?
"""

from pydantic import BaseModel, Field, field_validator
from fastapi import FastAPI, Body
from fastapi.exceptions import HTTPException
import re
import asyncio
import httpx
from contextlib import asynccontextmanager
from app.tasks import routes
from .database.db import Base, engine

app = FastAPI(title="Task API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables (DEV ONLY — use Alembic in prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: (optional) clean-up resources if needed
    # await engine.dispose()  # uncomment if you want to close DB pool on shutdown

app = FastAPI(
    title="Task API",
    lifespan=lifespan
)

app.include_router(routes.router)







MAX_RETRIES = 3
RETRY_DELAY = 1
EXTERNAL_URL = ""

class WithdrawResponse(BaseModel):
    message : str 
    trasanction_code : str  
    pin_code : str 
    amount : int 


class WithdrawRequest(BaseModel):
    trasanction_code : str = Field(..., min_length=8, max_length=8)
    pin_code : str = Field(..., min_length=6, max_length=8)
    amount : int = Field(..., ge=100, le=5000)

    @field_validator('trasanction_code')
    def validate_transaction_code(cls, val):
        if not re.match(r'^[A-Za-z0-9]{8}$', val):
            raise ValueError("trasanction_code must be 8 chars alphnumeric!")
        return val
    
    @field_validator('amount')
    def validate_amount(cls, val):
        if val % 100 != 0:
            raise ValueError("Amount must be multiple of 100!")
        return val
    

async def validate_pin_code(pin_code):
    return True

    for attempt in range(MAX_RETRIES+1):
        try:
            async with httpx.AsyncClient(timeout=0.5) as client:
                response = client.post(EXTERNAL_URL, json={'pin_code': pin_code})
                if response.status == 200:
                    return response.json().get('valid', False)
                elif response.status >= 500:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    return False
        except httpx.RequestError:
            if attempt == MAX_RETRIES:
                raise HTTPException(detail="Pincode validation service not available", status_code=503)
            await asyncio.sleep(RETRY_DELAY)
    return False
    

@app.post('/withdraw', status_code=200, response_model=WithdrawResponse)
async def cardless_withdraw(data: WithdrawRequest = Body(...)):
    is_valid_pin = await validate_pin_code(data.pin_code)
    
    if not is_valid_pin:
        raise HTTPException(status_code=400, detail="Invalid pin code!")

    return {
        "message": "success",
        "trasanction_code": f"Hello",
        "pin_code": "pin_code",
        "pin_code": "1000",
        "amount": 1000
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port="8000")








































# # from db import SessionLocal
# # from fastapi import FastAPI, Depends
# # from sqlalchemy.orm import Session
# # from db import Base, engine
# # from fastapi.exceptions import HTTPException
# # from schema import CreateBook, UpdateBook
# # from model import Book

# # app = FastAPI()
# # from model import Book


# # Base.metadata.create_all(bind=engine)

# # def get_db():
# #     db = SessionLocal()
# #     try:
# #         yield db
# #     finally:
# #         db.close()


# # @app.get("/get-book/{book_id}")
# # async def get_books(book_id: int, db: Session = Depends(get_db)):
# #     book = db.query(Book).filter(Book.id == book_id).first()
# #     if not book:
# #         raise HTTPException(status_code=404, detail="Book not found!")
# #     return book


# # @app.post("/create-book/", response_model=CreateBook)
# # async def get_books(book_data: CreateBook, db: Session = Depends(get_db)):
# #     book = Book(**book_data.dict())
# #     db.add(book)
# #     db.commit()
# #     db.refresh(book)
# #     return book


# # @app.put("/update-book/{book_id}", response_model=UpdateBook)
# # async def get_books(book_id: int, book_data: UpdateBook, db: Session = Depends(get_db)):
# #     book = db.query(Book).filter(Book.id == book_id).first()
# #     if not book:
# #         raise HTTPException(status_code=404, detail="Book not found to Update!")
    
# #     for key, value in book_data.dict(exclude_unset=True).items():
# #         setattr(book, key, value)

# #     db.add(book)
# #     db.commit()
# #     db.refresh(book)
# #     return book

# # from fastapi.responses import JSONResponse

# # @app.delete("/delete-book/{book_id}")
# # async def get_books(book_id: int, db: Session = Depends(get_db)):
# #     book = db.query(Book).filter(Book.id == book_id).first()
# #     if not book:
# #         raise HTTPException(status_code=404, detail="Book not found to Delete!")
    
    
# #     db.delete(book)
# #     db.commit()
# #     return JSONResponse({
# #         "message": "Book deleted!",
# #         "success": True,
# #     }, status_code=200)

    
