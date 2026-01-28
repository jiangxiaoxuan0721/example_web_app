from backend.core.defaults import get_default_instances
from backend.fastapi.models.response_models import SchemaResponse
import json

schemas = get_default_instances()
demo = schemas['demo']

# 测试 SchemaResponse 序列化
response = SchemaResponse(
    status="success",
    ui_schema=demo,
    partial=False
)

print('=== SchemaResponse with by_alias=True ===')
print(json.dumps(response.model_dump(by_alias=True), indent=2, ensure_ascii=False))

print('\n=== SchemaResponse without by_alias ===')
print(json.dumps(response.model_dump(by_alias=False), indent=2, ensure_ascii=False))
