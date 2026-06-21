from fastapi import FastAPI
from backend.app.api import router
from backend.app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dynamic Noise Aware Lexicon–Transformer Fusion Framework Backend", version="0.1.0")
app.include_router(router)


@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.get('/ready')
def ready():
    return {'status': 'ready'}
