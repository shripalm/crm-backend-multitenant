import subprocess
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.schemas.response import StandardResponse
from app.utils.response import success_response
from app.db.session import get_db
from app.services import upload

router = APIRouter()


class MockUploadFile:
    def __init__(self, file_path: str):
        self.filename = file_path.split('/')[-1]
        self.file_path = file_path

    async def read(self):
        with open(self.file_path, 'rb') as f:
            return f.read()


def run_python_script(script_path: str) -> list:
    """
    Runs a Python script and returns its logs as a list of lines.
    """
    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )
    logs = result.stdout + "\n" + result.stderr
    return logs.split('\n')

def run_shell(shellCommands: list = []) -> list:
    """
    Runs a Python script and returns its logs as a list of lines.
    """
    result = subprocess.run(
        shellCommands,
        capture_output=True,
        text=True
    )
    logs = result.stdout + "\n" + result.stderr
    return logs.split('\n')


@router.get("/db_drop_all", response_model=StandardResponse[dict])
async def db_drop_all(request: Request):
    """Drop all client databases or admin database based on client header. admin/all clients."""
    client = request.headers.get("client")
    if client == "admin":
        logs = run_python_script("scripts/drop_admin_db.py")
        return success_response(data={
            "status": "DB Drop Admin Service ran successfully",
            "logs": logs
        })
    else:
        logs = run_python_script("scripts/drop_all_client_dbs.py")
        return success_response(data={
            "status": "DB Drop All Service ran successfully",
            "logs": logs
        })


@router.get("/db_migrate", response_model=StandardResponse[dict])
async def db_migrate():
    """Migrate all databases along with admin database."""
    logs = run_python_script("scripts/migrate_all_clients.py")
    return success_response(data={
        "status": "DB Migration Service ran successfully",
        "logs": logs
    })

@router.get("/db_seed", response_model=StandardResponse[dict])
async def db_seed(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Seed the database with dummy data based on client header."""
    try:
        client = request.headers.get("client")
        if client == "admin":
            # Use admin database session
            from app.db.admin_session import get_admin_db
            async for admin_db in get_admin_db():
                try:
                    # Read and execute admin seed data
                    with open("admin_dummy_data_insert.sql", "r") as f:
                        sql_script = f.read()

                    statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]

                    for stmt in statements:
                        await admin_db.execute(text(stmt))

                    await admin_db.commit()
                    return success_response(data={"status": "Admin DB Seeding Service ran successfully"})
                except Exception as e:
                    await admin_db.rollback()
                    raise HTTPException(status_code=500, detail=f"Admin DB seeding failed: {str(e)}")
        else:
            # Regular client database seeding
            with open("dummy_data_insert.sql", "r") as f:
                sql_script = f.read()

            statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]

            for stmt in statements:
                await db.execute(text(stmt))

            await db.commit()

            # Process the CSV file for contact imports
            try:
                csv_file_path = "uploading-files/test_uploadCSV_200.csv"
                mock_file = MockUploadFile(csv_file_path)
                file_content = await mock_file.read()
                upload_result = await upload.process_file(
                    db=db,
                    file_content=file_content,
                    filename="test_uploadCSV_200.csv"
                )
            except Exception as e:
                # Log the error but don't fail the seeding
                print(f"File upload processing skipped or failed: {str(e)}")

            return success_response(data={"status": "DB Seeding Service ran successfully"})
    except Exception as e:
        if 'db' in locals():
            await db.rollback()
        raise HTTPException(status_code=500, detail=f"DB seeding failed: {str(e)}")

@router.get("/db_downgrade", response_model=StandardResponse[dict])
async def db_downgrade(request: Request, db: AsyncSession = Depends(get_db)):
    """Downgrade all client databases or admin database based on client header."""
    client = request.headers.get("client")
    if client == "admin":
        logs = run_shell(["scripts/admin_db.sh", "rollback"])
        return success_response(data={
            "status": "Admin DB Downgrade Service ran successfully",
            "logs": logs
        })
    else:
        logs = run_python_script("scripts/downgrade_1_alembic.py")
        return success_response(data={
            "status": "DB Downgrade Service ran successfully",
            "logs": logs
        })

@router.get("/db_version_check", response_model=StandardResponse[dict])
async def db_version_check(db: AsyncSession = Depends(get_db)):
    """Check Alembic versions for all client databases along with admin database."""
    logs = run_python_script("scripts/fetch_curr_version.py")
    return success_response(data={
        "status": "DB Version Check Service ran successfully",
        "logs": logs
    })