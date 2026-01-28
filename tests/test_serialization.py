from backend.core.defaults import get_default_instances
import json

schemas = get_default_instances()
demo = schemas['demo']
table_field = demo.blocks[0].props.fields[0]

# 测试序列化
print('=== With by_alias=True ===')
columns_with_alias = [col.model_dump(by_alias=True) for col in table_field.columns]
for col in columns_with_alias:
    print(json.dumps(col, ensure_ascii=False))

print('\n=== Without by_alias ===')
columns_without_alias = [col.model_dump(by_alias=False) for col in table_field.columns]
for col in columns_without_alias:
    print(json.dumps(col, ensure_ascii=False))
