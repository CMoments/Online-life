from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.session import get_db
from app.core.auth import get_current_admin_user

router = APIRouter(prefix="/api/database", tags=["database"])

@router.options("/tables")
async def options_tables():
    """处理预检请求"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true",
        }
    )

@router.get("/tables")
async def get_all_tables(
    db: AsyncSession = Depends(get_db)
):
    """获取所有表名"""
    try:
        # MySQL查询所有表名
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
        """)
        result = await db.execute(query)
        tables = [row[0] for row in result]
        return JSONResponse(
            content={"success": True, "data": tables},
            headers={
                "Access-Control-Allow-Origin": "http://localhost:5173",
                "Access-Control-Allow-Credentials": "true",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.options("/table/{table_name}")
async def options_table_data():
    """处理预检请求"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true",
        }
    )

@router.get("/table/{table_name}")
async def get_table_data(
    table_name: str,
    page: int = 1,
    per_page: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """获取指定表的数据"""
    try:
        # 获取表的列信息
        columns_query = text("""
            SELECT 
                column_name,
                data_type,
                column_comment
            FROM information_schema.columns 
            WHERE table_schema = DATABASE()
            AND table_name = :table_name
            ORDER BY ordinal_position
        """)
        columns_result = await db.execute(columns_query, {"table_name": table_name})
        columns = [(row[0], row[1], row[2]) for row in columns_result]

        # 获取总记录数
        count_query = text(f"SELECT COUNT(*) FROM `{table_name}`")
        count_result = await db.execute(count_query)
        total = count_result.scalar()

        # 获取分页数据
        offset = (page - 1) * per_page
        data_query = text(f"""
            SELECT * FROM `{table_name}`
            LIMIT :limit OFFSET :offset
        """)
        data_result = await db.execute(
            data_query,
            {"limit": per_page, "offset": offset}
        )
        rows = [dict(zip([col[0] for col in columns], row)) for row in data_result]

        return JSONResponse(
            content={
                "success": True,
                "data": {
                    "columns": [{"name": col[0], "type": col[1], "comment": col[2]} for col in columns],
                    "rows": rows,
                    "total": total,
                    "page": page,
                    "per_page": per_page
                }
            },
            headers={
                "Access-Control-Allow-Origin": "http://localhost:5173",
                "Access-Control-Allow-Credentials": "true",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.options("/table/{table_name}/schema")
async def options_table_schema():
    """处理预检请求"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true",
        }
    )

@router.get("/table/{table_name}/schema")
async def get_table_schema(
    table_name: str,
    db: AsyncSession = Depends(get_db)
):
    """获取指定表的结构信息"""
    try:
        query = text("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                column_default,
                is_nullable,
                column_comment,
                column_key,
                extra
            FROM information_schema.columns 
            WHERE table_schema = DATABASE()
            AND table_name = :table_name
            ORDER BY ordinal_position
        """)
        result = await db.execute(query, {"table_name": table_name})
        columns = [
            {
                "name": row[0],
                "type": row[1],
                "max_length": row[2],
                "default": row[3],
                "nullable": row[4],
                "comment": row[5],
                "key": row[6],
                "extra": row[7]
            }
            for row in result
        ]
        return JSONResponse(
            content={"success": True, "data": columns},
            headers={
                "Access-Control-Allow-Origin": "http://localhost:5173",
                "Access-Control-Allow-Credentials": "true",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 