import json
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .models import Food, HotelTable, Order


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Hotel Management System")

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class OrderRequest(BaseModel):
    table_id: int
    items: list[dict]


@app.on_event("startup")
def seed_database():

    db = SessionLocal()

    if db.query(Food).count() == 0:

        foods = [

            Food(
                name="Masala Dosa",
                description="Crispy dosa with potato masala",
                price=80,
                image="https://images.unsplash.com/photo-1630383249896-424e482df921?w=700"
            ),

            Food(
                name="Idli Sambar",
                description="Soft idlis with sambar",
                price=60,
                image="https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=700"
            ),

            Food(
                name="Veg Biryani",
                description="Aromatic vegetable biryani",
                price=150,
                image="https://images.unsplash.com/photo-1563379091339-03246963d51a?w=700"
            ),

            Food(
                name="Paneer Tikka",
                description="Grilled paneer with spices",
                price=180,
                image="https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=700"
            ),

            Food(
                name="Fresh Lime Soda",
                description="Chilled lime soda",
                price=50,
                image="https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=700"
            ),

            Food(
                name="Gulab Jamun",
                description="Warm sweet dumplings",
                price=70,
                image="https://images.unsplash.com/photo-1666190094762-1c8b5b1b5f75?w=700"
            )
        ]

        db.add_all(foods)

    if db.query(HotelTable).count() == 0:

        tables = []

        for i in range(1, 13):

            table = HotelTable(
                id=i,
                label=f"Table {i}",
                x=((i - 1) % 4) * 22 + 5,
                y=((i - 1) // 4) * 30 + 10,
                status="free"
            )

            tables.append(table)

        db.add_all(tables)

    db.commit()
    db.close()


@app.get("/")
def home():

    return FileResponse(
        BASE_DIR / "static" / "index.html"
    )


@app.get("/admin")
def admin():

    return FileResponse(
        BASE_DIR / "static" / "admin.html"
    )


@app.get("/api/foods")
def get_foods(db: Session = Depends(get_db)):

    return db.query(Food).filter(
        Food.available == True
    ).all()


@app.get("/api/tables")
def get_tables(db: Session = Depends(get_db)):

    return db.query(HotelTable).all()


@app.post("/api/orders")
def create_order(
    request: OrderRequest,
    db: Session = Depends(get_db)
):

    table = db.get(
        HotelTable,
        request.table_id
    )

    if not table:

        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )

    if table.status != "free":

        raise HTTPException(
            status_code=409,
            detail="Table is not free"
        )

    total = 0

    for item in request.items:

        food = db.get(
            Food,
            item["food_id"]
        )

        if not food:

            raise HTTPException(
                status_code=400,
                detail="Food item not found"
            )

        quantity = int(
            item["quantity"]
        )

        total += food.price * quantity

    order = Order(
        table_id=request.table_id,
        items_json=json.dumps(request.items),
        total=total,
        status="pending"
    )

    table.status = "occupied"

    db.add(order)

    db.commit()

    db.refresh(order)

    return {
        "message": "Order placed successfully",
        "id": order.id,
        "total": total,
        "status": order.status
    }


@app.get("/api/orders")
def get_orders(
    db: Session = Depends(get_db)
):

    return db.query(Order).order_by(
        Order.id.desc()
    ).all()


@app.put("/api/orders/{order_id}/{status}")
def update_order(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    allowed = {
        "pending",
        "preparing",
        "ready",
        "completed",
        "cancelled"
    }

    if status not in allowed:

        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    order = db.get(
        Order,
        order_id
    )

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    order.status = status

    if status in {
        "completed",
        "cancelled"
    }:

        table = db.get(
            HotelTable,
            order.table_id
        )

        if table:

            table.status = "free"

    db.commit()

    return {
        "message": "Order updated successfully"
    }


@app.put("/api/tables/{table_id}/{status}")
def update_table(
    table_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    if status not in {
        "free",
        "occupied"
    }:

        raise HTTPException(
            status_code=400,
            detail="Invalid table status"
        )

    table = db.get(
        HotelTable,
        table_id
    )

    if not table:

        raise HTTPException(
            status_code=404,
            detail="Table not found"
        )

    table.status = status

    db.commit()

    return {
        "message": "Table updated successfully"
    }
