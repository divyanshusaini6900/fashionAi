import json
from app.main import app

def generate_schema():
    """Generates the OpenAPI schema and saves it to openapi.json"""
    openapi_schema = app.openapi()
    with open("openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("openapi.json generated successfully.")

if __name__ == "__main__":
    generate_schema() 