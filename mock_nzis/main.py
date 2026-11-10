from fastapi import FastAPI, HTTPException, Request

app = FastAPI(title="Mock NZIS")

received: list[dict] = []
state = {"fail_next": 0}


@app.post("/fhir/Observation", status_code=201)
async def receive_observation(request: Request):
    if state["fail_next"] > 0:
        state["fail_next"] -= 1
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    body = await request.json()
    if body.get("resourceType") != "Observation":
        raise HTTPException(status_code=400, detail="Expected an Observation resource")
    received.append(body)
    return {"resourceType": "Observation", "id": str(len(received))}


@app.post("/admin/fail-next")
def fail_next(count: int = 3):
    state["fail_next"] = count
    return state


@app.get("/admin/received")
def get_received():
    return {"count": len(received), "last": received[-3:]}