from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db
from app.models.flow import Scoring

router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/update", dependencies=[Depends(require_auth)])
def update_scoring(payload: dict, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    if payload is None:
        raise HTTPException(status_code=400, detail="invalid_payload")
    scoring = db.query(Scoring).filter(Scoring.id == 1).first()
    if not scoring:
        scoring = Scoring(id=1, data=payload)
        db.add(scoring)
    else:
        scoring.data = payload
    db.commit()
    db.refresh(scoring)
    return {"status": "updated", "scoring": scoring.data}
