from backend.core.defaults import get_default_instances

schemas = get_default_instances()
demo = schemas['demo']

# 查看表格配置
table_field = demo.blocks[0].props.fields[0]

print('=== Table Field Config ===')
print(f'Label: {table_field.label}')
print(f'Key: {table_field.key}')
print(f'Show header: {table_field.show_header}')
print(f'Show pagination: {table_field.show_pagination}')
print(f'Page size: {table_field.page_size}')
print(f'Number of columns: {len(table_field.columns)}')

print('\n=== Columns ===')
for i, col in enumerate(table_field.columns):
    print(f'Column {i}:')
    print(f'  Key: {col.key}')
    print(f'  Title: {col.title}')
    print(f'  Align: {col.align}')
    print(f'  Render type: {col.renderType}')
    print(f'  Tag type: {col.tagType}')

print('\n=== State Params Users Count ===')
print(f'Users: {len(demo.state.params.get("users", []))}')
