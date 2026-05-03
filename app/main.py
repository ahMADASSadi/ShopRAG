import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from sqladmin import Admin, ModelView

from app.config import get_settings
from app.adapters.db.session import init_db, engine
from app.adapters.db.models import ProductModel, PriceUpdateModel
from app.api.routes import products, price_updates

settings = get_settings()

# Configure loguru
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.DEBUG else "INFO",
)
logger.add(
    "logs/shoprag.log",
    rotation="10 MB",
    retention="1 week",
    compression="gz",
    level="INFO",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A RAG-powered shop price comparison and update system",
    lifespan=lifespan,
)

# Admin panel
admin = Admin(app, engine, title="ShopRAG Admin")


class ProductAdmin(ModelView, model=ProductModel):
    column_list = [
        ProductModel.id,
        ProductModel.name,
        ProductModel.sku,
        ProductModel.category,
        ProductModel.price,
        ProductModel.stock,
    ]
    column_searchable_list = [ProductModel.name, ProductModel.sku]
    column_sortable_list = [ProductModel.id, ProductModel.price, ProductModel.name]
    name = "Product"
    name_plural = "Products"
    icon = "fa-solid fa-box"


class PriceUpdateAdmin(ModelView, model=PriceUpdateModel):
    column_list = [
        PriceUpdateModel.id,
        PriceUpdateModel.product_id,
        PriceUpdateModel.old_price,
        PriceUpdateModel.new_price,
        PriceUpdateModel.created_at,
    ]
    can_create = False
    can_edit = False
    can_delete = False
    name = "Price Update"
    name_plural = "Price Updates"
    icon = "fa-solid fa-tag"


admin.add_view(ProductAdmin)
admin.add_view(PriceUpdateAdmin)

# Routes
app.include_router(products.router, prefix="/api/v1")
app.include_router(price_updates.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
