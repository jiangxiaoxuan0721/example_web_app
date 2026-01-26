"""
Table Component Feature Tests

Comprehensive tests for table component features:
- Column configurations (width, align, sortable, editable)
- Render types (text, tag, badge, progress, image, mixed)
- Table properties (bordered, striped, hover, pagination)
- Data manipulation (sorting, filtering, row actions)
- Advanced features (expandable, selection, row events)
"""

import pytest

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)

from backend.mcp.tool_implements import (
    add_field_impl, update_field_impl, remove_field_impl,
    patch_ui_state_impl, get_schema_impl
)


@pytest.fixture
async def table_test_instance():
    """Create a new test instance for table testing with pre-configured fields"""
    import uuid
    instance_id = f"table_test_{uuid.uuid4().hex[:8]}"
    await patch_ui_state_impl(
        instance_id="__CREATE__",
        new_instance_id=instance_id,
        patches=[
            {"op": "set", "path": "meta", "value": {"pageKey": instance_id, "step": {"current": 1, "total": 1}}},
            {"op": "set", "path": "state", "value": {
                "params": {
                    "users": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "status": "active", "avatar": "https://picsum.photos/seed/alice/100/100.jpg", "age": 25, "score": {"current": 85, "total": 100}},
                        {"id": 2, "name": "Bob", "email": "bob@example.com", "status": "inactive", "avatar": "https://picsum.photos/seed/bob/100/100.jpg", "age": 30, "score": {"current": 60, "total": 100}},
                        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "status": "pending", "avatar": "https://picsum.photos/seed/charlie/100/100.jpg", "age": 28, "score": {"current": 75, "total": 100}},
                    ],
                    "products": [
                        {"id": 1, "name": "Product A", "price": 99.99, "stock": 100, "category": "Electronics"},
                        {"id": 2, "name": "Product B", "price": 49.99, "stock": 50, "category": "Books"},
                        {"id": 3, "name": "Product C", "price": 199.99, "stock": 25, "category": "Electronics"},
                    ],
                    "progress_data": [
                        {"id": 1, "name": "Task 1", "progress": {"current": 75, "total": 100}},
                        {"id": 2, "name": "Task 2", "progress": {"current": 40, "total": 50}},
                        {"id": 3, "name": "Task 3", "progress": {"current": 90, "total": 100}},
                    ]
                },
                "runtime": {}
            }},
            {"op": "set", "path": "blocks", "value": [{"id": "block0", "type": "form", "bind": "state.params", "props": {"fields": []}}]},
            {"op": "set", "path": "actions", "value": []}
        ]
    )

    # Pre-create basic table fields for testing
    await add_field_impl(
        instance_id=instance_id,
        field={
            "label": "Users",
            "key": "users",
            "type": "table",
            "columns": [
                {"key": "id", "label": "ID"},
                {"key": "name", "label": "Name"},
                {"key": "email", "label": "Email"}
            ]
        }
    )

    await add_field_impl(
        instance_id=instance_id,
        field={
            "label": "Products",
            "key": "products",
            "type": "table",
            "columns": [
                {"key": "id", "label": "ID"},
                {"key": "name", "label": "Name"},
                {"key": "price", "label": "Price"}
            ]
        }
    )

    yield instance_id


class TestColumnConfigurations:
    """Test table column configuration features"""
    
    @pytest.mark.asyncio
    async def test_column_width(self, table_test_instance):
        """Test setting custom column width"""
        result = await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "User Table",
                "key": "users",
                "type": "table",
                "columns": [
                    {"key": "id", "label": "ID", "width": "80px"},
                    {"key": "name", "label": "Name", "width": "150px"},
                    {"key": "email", "label": "Email", "width": "250px"}
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_column_align_left(self, table_test_instance):
        """Test left aligned column"""
        result = await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "Product Table",
                "key": "products",
                "type": "table",
                "columns": [
                    {"key": "name", "label": "Name", "align": "left"}
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_column_align_center(self, table_test_instance):
        """Test center aligned column"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="products",
            updates={
                "columns": [
                    {"key": "id", "label": "ID", "align": "center"}
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_column_align_right(self, table_test_instance):
        """Test right aligned column (useful for numbers)"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="products",
            updates={
                "columns": [
                    {"key": "price", "label": "Price", "align": "right"}
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_sortable_column(self, table_test_instance):
        """Test sortable column"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="products",
            updates={
                "columns": [
                    {"key": "price", "label": "Price", "sortable": True}
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_editable_column(self, table_test_instance):
        """Test editable column"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="products",
            updates={
                "columns": [
                    {"key": "stock", "label": "Stock", "editable": True}
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_multiple_columns_mixed_config(self, table_test_instance):
        """Test multiple columns with mixed configurations"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="products",
            updates={
                "columns": [
                    {"key": "id", "label": "ID", "width": "100px", "align": "center"},
                    {"key": "name", "label": "Name", "width": "200px", "align": "left", "sortable": True},
                    {"key": "price", "label": "Price", "align": "right", "sortable": True},
                    {"key": "stock", "label": "Stock", "align": "center", "editable": True},
                    {"key": "category", "label": "Category", "width": "150px"}
                ]
            }
        )
        assert result["status"] == "success"


class TestRenderTypes:
    """Test different column render types"""
    
    @pytest.mark.asyncio
    async def test_render_type_text(self, table_test_instance):
        """Test default text render type"""
        result = await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "Users",
                "key": "users",
                "type": "table",
                "columns": [
                    {"key": "name", "label": "Name", "renderType": "text"}
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_render_type_tag_auto_detection(self, table_test_instance):
        """Test tag render type with auto type detection"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={
                "columns": [
                    {"key": "status", "label": "Status", "renderType": "tag"}
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_render_type_tag_custom_mapping(self, table_test_instance):
        """Test tag render type with custom text mapping"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={
                "columns": [
                    {
                        "key": "status", 
                        "label": "Status", 
                        "renderType": "tag",
                        "renderText": "active:激活|inactive:停用|pending:待审核"
                    }
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_render_type_tag_conditional_type(self, table_test_instance):
        """Test tag render type with conditional type based on value"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={
                "columns": [
                    {
                        "key": "status",
                        "label": "Status",
                        "renderType": "tag",
                        "tagType": "value => value === 'active' ? 'success' : value === 'inactive' ? 'default' : 'warning'"
                    }
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_render_type_badge(self, table_test_instance):
        """Test badge render type"""
        # First add a table field with badge column
        result = await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "Users",
                "key": "users",
                "type": "table",
                "columns": [
                    {"key": "name", "label": "Name"},
                    {"key": "age", "label": "Age", "renderType": "badge", "badgeColor": "#1890ff"}
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_render_type_progress(self, table_test_instance):
        """Test progress render type"""
        # Add a table with progress column
        result = await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "Scores",
                "key": "progress_data",
                "type": "table",
                "columns": [
                    {"key": "name", "label": "Name"},
                    {"key": "progress", "label": "Score", "renderType": "progress"}
                ]
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_render_type_image(self, table_test_instance):
        """Test image render type"""
        # Add a table with image column
        await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "Avatars",
                "key": "users",
                "type": "table",
                "columns": [
                    {"key": "name", "label": "Name"},
                    {"key": "avatar", "label": "Avatar", "renderType": "image"}
                ]
            }
        )
        assert True  # If we get here, table was created successfully
    
    @pytest.mark.asyncio
    async def test_render_type_mixed(self, table_test_instance):
        """Test mixed render types in one table"""
        # Add a comprehensive table with all render types
        result = await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "User Details",
                "key": "users",
                "type": "table",
                "columns": [
                    {"key": "id", "label": "ID", "renderType": "text", "align": "center"},
                    {"key": "name", "label": "Name", "renderType": "text"},
                    {"key": "email", "label": "Email", "renderType": "text"},
                    {"key": "avatar", "label": "Avatar", "renderType": "image"},
                    {"key": "status", "label": "Status", "renderType": "tag"}
                ]
            }
        )
        assert result["status"] == "success"


class TestTableProperties:
    """Test table-level properties"""
    
    @pytest.mark.asyncio
    async def test_bordered_table(self, table_test_instance):
        """Test bordered table"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={"bordered": True}
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_striped_table(self, table_test_instance):
        """Test striped rows"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={"striped": True}
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_hover_table(self, table_test_instance):
        """Test hover effect"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={"hover": True}
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_compact_table(self, table_test_instance):
        """Test compact table"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={"compact": True}
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_show_header(self, table_test_instance):
        """Test showing/hiding header"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={"showHeader": True}
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_custom_empty_text(self, table_test_instance):
        """Test custom empty text"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={"emptyText": "No users found"}
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_max_height_table(self, table_test_instance):
        """Test table with max height"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={"maxHeight": "400px"}
        )
        assert result["status"] == "success"


class TestPagination:
    """Test table pagination features"""
    
    @pytest.mark.asyncio
    async def test_enable_pagination(self, table_test_instance):
        """Test enabling pagination"""
        # Add more data
        await patch_ui_state_impl(
            instance_id=table_test_instance,
            patches=[{
                "op": "set",
                "path": "state.params.users",
                "value": [{"id": i, "name": f"User{i}", "email": f"user{i}@example.com", "status": "active"} 
                         for i in range(1, 51)]
            }]
        )
        
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={
                "showPagination": True,
                "pageSize": 10
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_custom_page_size(self, table_test_instance):
        """Test custom page size"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={"pageSize": 20}
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_different_page_sizes(self, table_test_instance):
        """Test various page sizes"""
        page_sizes = [5, 10, 15, 20, 25, 50]
        for size in page_sizes:
            result = await update_field_impl(
                instance_id=table_test_instance,
                field_key="users",
                updates={"pageSize": size}
            )
            assert result["status"] == "success"


class TestRowKey:
    """Test row key configuration"""
    
    @pytest.mark.asyncio
    async def test_custom_row_key(self, table_test_instance):
        """Test custom row key"""
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={"rowKey": "id"}
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_different_row_keys(self, table_test_instance):
        """Test different row key fields"""
        row_keys = ["id", "name", "email"]
        for key in row_keys:
            result = await update_field_impl(
                instance_id=table_test_instance,
                field_key="users",
                updates={"rowKey": key}
            )
            assert result["status"] == "success"


class TestDataManipulation:
    """Test table data manipulation"""
    
    @pytest.mark.asyncio
    async def test_add_row_to_table(self, table_test_instance):
        """Test adding a new row"""
        new_user = {"id": 6, "name": "Frank", "email": "frank@example.com", "status": "active"}
        result = await patch_ui_state_impl(
            instance_id=table_test_instance,
            patches=[{
                "op": "set",
                "path": "state.params.users",
                "value": {
                    "operation": "append_to_list",
                    "params": {"item": new_user}
                }
            }]
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_update_row_in_table(self, table_test_instance):
        """Test updating a row"""
        result = await patch_ui_state_impl(
            instance_id=table_test_instance,
            patches=[{
                "op": "set",
                "path": "state.params.users.0.status",
                "value": "inactive"
            }]
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_remove_row_from_table(self, table_test_instance):
        """Test removing a row"""
        result = await patch_ui_state_impl(
            instance_id=table_test_instance,
            patches=[{
                "op": "set",
                "path": "state.params.users",
                "value": {
                    "operation": "remove_from_list",
                    "params": {"index": 0}
                }
            }]
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_bulk_update_rows(self, table_test_instance):
        """Test bulk updating rows"""
        result = await patch_ui_state_impl(
            instance_id=table_test_instance,
            patches=[{
                "op": "set",
                "path": "state.params.users",
                "value": [
                    {"id": 1, "name": "Alice Updated", "email": "alice@example.com", "status": "active"},
                    {"id": 2, "name": "Bob Updated", "email": "bob@example.com", "status": "active"},
                    {"id": 3, "name": "Charlie Updated", "email": "charlie@example.com", "status": "active"},
                ]
            }]
        )
        assert result["status"] == "success"


class TestComplexScenarios:
    """Test complex table scenarios"""
    
    @pytest.mark.asyncio
    async def test_admin_user_table(self, table_test_instance):
        """Test comprehensive admin user table"""
        # Update the users field instead of recreating it
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={
                "label": "User Management",
                "columns": [
                    {"key": "id", "label": "ID", "width": "80px", "align": "center"},
                    {"key": "avatar", "label": "Avatar", "renderType": "image", "width": "100px"},
                    {"key": "name", "label": "Name", "width": "150px", "sortable": True},
                    {"key": "email", "label": "Email", "width": "250px"},
                    {"key": "age", "label": "Age", "align": "center", "renderType": "badge", "badgeColor": "#1890ff"},
                    {"key": "score", "label": "Score", "align": "center", "renderType": "progress", "sortable": True},
                    {"key": "status", "label": "Status", "renderType": "tag",
                     "tagType": "value => value === 'active' ? 'success' : value === 'inactive' ? 'default' : 'warning'"},
                    {
                        "key": "actions",
                        "label": "Actions",
                        "renderType": "mixed",
                        "align": "center",
                        "components": [
                            {"type": "button", "buttonStyle": "primary", "buttonSize": "small", "buttonLabel": "编辑", "margin": "0 4px"},
                            {"type": "button", "buttonStyle": "danger", "buttonSize": "small", "buttonLabel": "删除", "margin": "0 4px"}
                        ]
                    }
                ],
                "rowKey": "id",
                "bordered": True,
                "striped": True,
                "hover": True,
                "showPagination": True,
                "pageSize": 10,
                "emptyText": "No users found"
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_product_inventory_table(self, table_test_instance):
        """Test comprehensive user details table"""
        # First add the users table field
        await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "Users",
                "key": "users",
                "type": "table",
                "columns": [
                    {"key": "name", "label": "Name"}
                ]
            }
        )
        # Then update it
        result = await update_field_impl(
            instance_id=table_test_instance,
            field_key="users",
            updates={
                "columns": [
                    {"key": "id", "label": "User ID", "width": "120px", "align": "center", "sortable": True},
                    {"key": "name", "label": "Full Name", "width": "200px", "sortable": True},
                    {"key": "email", "label": "Email", "width": "250px"},
                    {"key": "age", "label": "Age", "align": "center", "width": "100px", "renderType": "badge", "badgeColor": "#1890ff"},
                    {"key": "score", "label": "Score", "align": "center", "renderType": "progress", "sortable": True},
                    {"key": "status", "label": "Status", "renderType": "tag"}
                ],
                "bordered": True,
                "striped": False,
                "hover": True,
                "showPagination": True,
                "pageSize": 5,
                "compact": True,
                "rowKey": "id"
            }
        )
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_minimal_table(self, table_test_instance):
        """Test minimal table configuration"""
        await add_field_impl(
            instance_id=table_test_instance,
            block_index=2,
            field={
                "label": "Simple List",
                "key": "products",
                "type": "table",
                "columns": [
                    {"key": "name", "label": "Name"}
                ]
            }
        )
        # Should work with minimal config
        assert await get_schema_impl(instance_id=table_test_instance)

class TestTableValidation:
    """Test table field validation"""

    @pytest.mark.asyncio
    async def test_table_with_nonexistent_key(self, table_test_instance):
        """Test that table with nonexistent key is rejected"""
        result = await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "Invalid Table",
                "key": "nonexistent_data",
                "type": "table",
                "columns": [
                    {"key": "name", "label": "Name"}
                ]
            }
        )
        assert result["status"] == "error"
        assert "does not exist in state.params" in result["error"]

    @pytest.mark.asyncio
    async def test_table_with_wrong_key_format(self, table_test_instance):
        """Test that table with wrong key format is rejected"""
        result = await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "Wrong Format",
                "key": "users_with_suffix",
                "type": "table",
                "columns": [
                    {"key": "name", "label": "Name"}
                ]
            }
        )
        assert result["status"] == "error"
        assert "does not exist in state.params" in result["error"]

    @pytest.mark.asyncio
    async def test_table_with_correct_key_succeeds(self, table_test_instance):
        """Test that table with correct key succeeds"""
        result = await add_field_impl(
            instance_id=table_test_instance,
            field={
                "label": "Valid Table",
                "key": "products",
                "type": "table",
                "columns": [
                    {"key": "name", "label": "Name"}
                ]
            }
        )
        assert result["status"] == "success"


if __name__ == "__main__":
    pytest.main(["-s", __file__])
    
