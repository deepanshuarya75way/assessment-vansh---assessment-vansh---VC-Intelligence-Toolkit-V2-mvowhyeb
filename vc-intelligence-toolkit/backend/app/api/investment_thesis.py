
from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database.session import get_sessionmaker
from app.models.investment_thesis import InvestmentThesisRule, ScreeningResult
from app.schemas.investment_thesis import (
    InvestmentThesisRuleCreate,
    InvestmentThesisRuleUpdate,
    StartupScreenRequest,
)
from app.services.investment_thesis_service import screen_candidate

router = APIRouter(
    prefix="/api/investment-thesis",
    tags=["investment thesis"],
)


def rule_dict(rule: InvestmentThesisRule) -> dict:
    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "field_name": rule.field_name,
        "operator": rule.operator,
        "expected_value": rule.expected_value,
        "weight": rule.weight,
        "is_mandatory": rule.is_mandatory,
        "is_active": rule.is_active,
        "created_at": rule.created_at,
    }


@router.post("/rules", status_code=status.HTTP_201_CREATED)
async def create_rule(payload: InvestmentThesisRuleCreate):
    async with get_sessionmaker()() as session:
        rule = InvestmentThesisRule(**payload.model_dump())
        session.add(rule)

        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise HTTPException(
                status_code=409,
                detail="A rule with this name already exists",
            ) from exc

        await session.refresh(rule)
        return rule_dict(rule)


@router.get("/rules")
async def list_rules(active_only: bool = False):
    async with get_sessionmaker()() as session:
        query = select(InvestmentThesisRule).order_by(
            InvestmentThesisRule.id
        )

        if active_only:
            query = query.where(
                InvestmentThesisRule.is_active.is_(True)
            )

        rules = (await session.scalars(query)).all()
        return [rule_dict(rule) for rule in rules]


@router.patch("/rules/{rule_id}")
async def update_rule(
    rule_id: int,
    payload: InvestmentThesisRuleUpdate,
):
    async with get_sessionmaker()() as session:
        rule = await session.get(InvestmentThesisRule, rule_id)

        if rule is None:
            raise HTTPException(404, "Rule not found")

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(rule, key, value)

        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise HTTPException(
                status_code=409,
                detail="A rule with this name already exists",
            ) from exc

        await session.refresh(rule)
        return rule_dict(rule)


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_rule(rule_id: int):
    async with get_sessionmaker()() as session:
        rule = await session.get(InvestmentThesisRule, rule_id)

        if rule is None:
            raise HTTPException(404, "Rule not found")

        await session.delete(rule)
        await session.commit()

    return Response(status_code=204)


@router.post("/screen")
async def screen_startup(payload: StartupScreenRequest):
    async with get_sessionmaker()() as session:
        try:
            return await screen_candidate(
                session,
                payload.candidate_id,
                payload.startup_data,
            )
        except LookupError as exc:
            raise HTTPException(404, str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc


@router.get("/screen/{candidate_id}/latest")
async def latest_screening(candidate_id: int):
    async with get_sessionmaker()() as session:
        query = (
            select(ScreeningResult)
            .where(ScreeningResult.candidate_id == candidate_id)
            .order_by(ScreeningResult.created_at.desc())
        )

        result = (await session.scalars(query)).first()

        if result is None:
            raise HTTPException(
                404,
                "No screening result found for this candidate",
            )

        return {
            "id": result.id,
            "candidate_id": result.candidate_id,
            "compatibility_score": result.compatibility_score,
            "status": result.status,
            "matrix": result.matrix,
            "created_at": result.created_at,
        }
