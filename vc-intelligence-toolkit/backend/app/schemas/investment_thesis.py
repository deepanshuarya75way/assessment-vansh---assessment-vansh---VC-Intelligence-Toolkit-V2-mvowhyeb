
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Operator = Literal[
    "eq", "neq", "gt", "gte", "lt", "lte", "in", "contains"
]


class InvestmentThesisRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    field_name: str = Field(min_length=1, max_length=255)
    operator: Operator
    expected_value: Any
    weight: float = Field(gt=0, le=100)
    is_mandatory: bool = False
    is_active: bool = True

    @model_validator(mode="after")
    def validate_expected_value(self):
        if self.operator == "in" and not isinstance(
            self.expected_value, (list, tuple, set, str, dict)
        ):
            raise ValueError("'in' requires a collection or string")
        if self.operator == "contains" and not isinstance(
            self.expected_value, (str, list, tuple, set, dict)
        ):
            raise ValueError("'contains' requires a container")
        if self.operator in {"gt", "gte", "lt", "lte"} and not isinstance(
            self.expected_value, (int, float)
        ):
            raise ValueError("Numeric comparison operators require a number")
        return self


class InvestmentThesisRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    field_name: str | None = Field(default=None, min_length=1, max_length=255)
    operator: Operator | None = None
    expected_value: Any = None
    weight: float | None = Field(default=None, gt=0, le=100)
    is_mandatory: bool | None = None
    is_active: bool | None = None


class InvestmentThesisRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    field_name: str
    operator: str
    expected_value: Any
    weight: float
    is_mandatory: bool
    is_active: bool


class StartupScreenRequest(BaseModel):
    candidate_id: int = Field(gt=0)
    startup_data: dict[str, Any] = Field(default_factory=dict)
