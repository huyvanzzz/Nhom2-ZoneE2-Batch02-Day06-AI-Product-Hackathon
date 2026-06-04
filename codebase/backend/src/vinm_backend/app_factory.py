from fastapi import FastAPI

from vinm_backend.models import AssistRequest
from vinm_backend.orchestrator import ResearchFlow


def create_app(flow: ResearchFlow) -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/v1/assist")
    async def assist(payload: AssistRequest):
        return await flow.run(payload)

    return app
