import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from model.account import Account
from model.general import SuccessModel, ErrorModel
from model.product import ReturnProduct, CreateProductForm, ReturnCreateProduct, UpdateProductForm
from utils import auth
from utils.db_process import get_all_results, execute_query, dict_to_sql_command, dict_delete_none

router = APIRouter(
    tags=["product"]
)

@router.get(
    "/", tags=["get"], responses={
        status.HTTP_200_OK: {
            "model": ReturnProduct
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel
        }
    }
)
async def get_product(
        shop_uuid: str
):
    sql = """
        SELECT * FROM `Product` WHERE shop_uuid = %s;
    """
    result = get_all_results(sql, (shop_uuid,))
    if result:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {
                    "msg": "Success",
                    "data": result
                }
            )
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder(
            {
                "msg": "Fail"
            }
        )
    )

@router.post(
    "/", tags=["create"], responses={
        status.HTTP_200_OK: {
            "model": ReturnCreateProduct
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel
        }
    }
)
async def create_product(
        account: Annotated[Account, Depends(auth.get_current_active_user)],
        product_form: CreateProductForm = Depends(CreateProductForm.as_form)
):
    shop_uuid = product_form.shop_uuid
    if not await auth.if_account_owns_shop(account.account_uuid, shop_uuid):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                {
                    "msg": f"Account {account.account_uuid} does not own shop {shop_uuid}"
                }
            )
        )

    product_form = product_form.model_dump()
    product_id = str(uuid.uuid4())
    sql = """
        INSERT INTO `Product`
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, DEFAULT);
    """
    result = execute_query(sql, (str(product_id),) + tuple(product_form.values()))
    if result:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "msg": "Success",
                "data": product_id
            }
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder(
            {
                "msg": "Fail"
            }
        )
    )

@router.put(
    "/", tags=["update"], responses={
        status.HTTP_200_OK: {
            "model": SuccessModel
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorModel
        }
    }
)
async def update_product(
        account: Annotated[Account, Depends(auth.get_current_active_user)],
        product_form: UpdateProductForm = Depends(UpdateProductForm.as_form)
):
    product_uuid = product_form.product_uuid
    shop_uuid = product_form.shop_uuid
    if not await auth.if_account_owns_product(account.account_uuid, shop_uuid, product_uuid):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                {
                    "msg": f"Account {account.account_uuid} does not own product {product_uuid}"
                }
            )
        )
    product_form = product_form.model_dump()
    product_form = dict_delete_none(product_form)
    sql_set_text, sql_set_values = dict_to_sql_command(product_form)
    sql = f"""
        UPDATE `Product` SET {sql_set_text}
        WHERE product_uuid = %s;
    """
    result = execute_query(sql, (sql_set_values + (product_form["product_uuid"],)))
    if result:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                {
                    "msg": "Success"
                }
            )
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder(
            {
                "msg": "Fail"
            }
        )
    )