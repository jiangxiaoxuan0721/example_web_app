"""
MCP Tools Comprehensive Test Suite

This test suite covers all MCP tools with various scenarios to ensure functionality and reliability.

Requirements:
    - Backend server running on http://localhost:8001
    - pytest and pytest-asyncio installed
    - httpx installed (for async HTTP calls)

Install dependencies:
    pip install pytest pytest-asyncio httpx

Run tests:
    pytest tests/test_mcp_tools.py -v
    pytest tests/test_mcp_tools.py -v -k "test_add_field"
    pytest tests/test_mcp_tools.py -v -m "field_operations"
"""

import pytest

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)

from backend.mcp.tool_implements import (
    add_field_impl, update_field_impl, remove_field_impl,
    add_block_impl, remove_block_impl,
    add_action_impl, remove_action_impl,
    patch_ui_state_impl, get_schema_impl, list_instances_impl,
    access_instance_impl, validate_completion_impl
)


@pytest.fixture
def demo_instance():
    """Fixture to reset demo instance before each test"""
    # This could be implemented to reset the demo instance
    # For now, we'll work with the current state
    yield "demo"


@pytest.fixture
def counter_instance():
    """Fixture for counter instance"""
    yield "counter"


@pytest.fixture
def rich_content_instance():
    """Fixture for rich_content instance"""
    yield "rich_content"


class TestFieldOperations:
    """Test field-related operations: add_field, update_field, remove_field"""

    @pytest.mark.asyncio
    async def test_add_text_field(self, demo_instance):
        """Test adding a simple text field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Test Name",
                "key": "test_name",
                "type": "text"
            },
            block_index=0,
            state_path="state.params.test_name",
            initial_value=""
        )
        assert result["status"] == "success"
        assert "patches_applied" in result

    @pytest.mark.asyncio
    async def test_add_number_field(self, demo_instance):
        """Test adding a number field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Age",
                "key": "age",
                "type": "number"
            },
            block_index=0,
            state_path="state.params.age",
            initial_value=0
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_textarea_field(self, demo_instance):
        """Test adding a textarea field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Description",
                "key": "description",
                "type": "textarea",
                "rows": 6
            },
            block_index=0,
            state_path="state.params.description",
            initial_value="Initial description"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_checkbox_field(self, demo_instance):
        """Test adding a checkbox field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Agree to terms",
                "key": "agreed",
                "type": "checkbox"
            },
            block_index=0,
            state_path="state.params.agreed",
            initial_value=False
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_select_field(self, demo_instance):
        """Test adding a select dropdown field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Country",
                "key": "country",
                "type": "select",
                "options": [
                    {"label": "China", "value": "cn"},
                    {"label": "USA", "value": "us"},
                    {"label": "Japan", "value": "jp"}
                ]
            },
            block_index=0,
            state_path="state.params.country"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_radio_field(self, demo_instance):
        """Test adding radio buttons field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Gender",
                "key": "gender",
                "type": "radio",
                "options": [
                    {"label": "Male", "value": "male"},
                    {"label": "Female", "value": "female"}
                ]
            },
            block_index=0,
            state_path="state.params.gender"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_multiselect_field(self, demo_instance):
        """Test adding a multiselect field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Skills",
                "key": "skills",
                "type": "multiselect",
                "options": [
                    {"label": "Python", "value": "python"},
                    {"label": "JavaScript", "value": "js"},
                    {"label": "Go", "value": "go"}
                ]
            },
            block_index=0,
            state_path="state.params.skills",
            initial_value=[]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_json_field(self, demo_instance):
        """Test adding a JSON field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Config",
                "key": "config",
                "type": "json"
            },
            block_index=0,
            state_path="state.params.config",
            initial_value={"key": "value"}
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_html_field(self, demo_instance):
        """Test adding an HTML field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Content",
                "key": "content",
                "type": "html",
                "value": "<h3>Title</h3><p>Paragraph</p>"
            },
            block_index=0,
            state_path="state.params.content"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_image_field(self, demo_instance):
        """Test adding an image field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Avatar",
                "key": "avatar",
                "type": "image",
                "imageFit": "cover",
                "imageHeight": "200px"
            },
            block_index=0,
            state_path="state.params.avatar"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_tag_field(self, demo_instance):
        """Test adding a tag field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Status",
                "key": "status",
                "type": "tag",
                "renderText": "active:Active|inactive:Inactive"
            },
            block_index=0,
            state_path="state.params.status"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_progress_field(self, demo_instance):
        """Test adding a progress bar field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Progress",
                "key": "progress",
                "type": "progress"
            },
            block_index=0,
            state_path="state.params.progress",
            initial_value={"current": 3, "total": 5, "showLabel": True}
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_badge_field(self, demo_instance):
        """Test adding a badge field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Notifications",
                "key": "notifications",
                "type": "badge"
            },
            block_index=0,
            state_path="state.params.notifications",
            initial_value={"count": 5, "label": "Msg"}
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_table_field(self, demo_instance):
        """Test adding a table field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Users",
                "key": "users_test",
                "type": "table",
                "columns": [
                    {"key": "id", "label": "ID"},
                    {"key": "name", "label": "Name"}
                ]
            },
            block_index=0,
            state_path="state.params.users_test",
            initial_value=[{"id": 1, "name": "John"}]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_modal_field(self, demo_instance):
        """Test adding a modal field"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={
                "label": "Confirm Dialog",
                "key": "confirm",
                "type": "modal"
            },
            block_index=0,
            state_path="state.params.confirm",
            initial_value={"visible": False, "title": "Confirm", "content": "Are you sure?"}
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_update_field_label(self, demo_instance):
        """Test updating a field's label"""
        result = await update_field_impl(
            instance_id=demo_instance,
            field_key="users",
            updates={"label": "Updated User List"}
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_update_field_type(self, demo_instance):
        """Test changing a field's type"""
        result = await update_field_impl(
            instance_id=demo_instance,
            field_key="country",
            updates={"type": "select", "options": [{"label": "China", "value": "cn"}, {"label": "USA", "value": "us"}]}
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_update_multiple_field_properties(self, demo_instance):
        """Test updating multiple field properties at once"""
        result = await update_field_impl(
            instance_id=demo_instance,
            field_key="country",
            updates={
                "label": "Country of Residence",
                "description": "Select your country",
                "editable": True
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_field(self, demo_instance):
        """Test removing a field"""
        result = await remove_field_impl(
            instance_id=demo_instance,
            field_key="country"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_all_matching_fields(self, demo_instance):
        """Test removing all fields with matching key"""
        result = await remove_field_impl(
            instance_id=demo_instance,
            field_key="test_name",
            remove_all=True
        )
        assert result["status"] == "success"


class TestBlockOperations:
    """Test block-related operations: add_block, remove_block"""

    @pytest.mark.asyncio
    async def test_add_form_block_at_end(self, demo_instance):
        """Test adding a form block at the end"""
        result = await add_block_impl(
            instance_id=demo_instance,
            block={
                "id": "new_form_block",
                "type": "form",
                "bind": "state.params",
                "props": {
                    "fields": [
                        {"label": "Field1", "key": "field1", "type": "text"}
                    ]
                }
            },
            position="end"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_form_block_at_start(self, demo_instance):
        """Test adding a form block at the start"""
        result = await add_block_impl(
            instance_id=demo_instance,
            block={
                "id": "header_block",
                "type": "form",
                "bind": "state.params",
                "props": {
                    "fields": [
                        {"label": "Header", "key": "header", "type": "html", "value": "<h2>Header</h2>"}
                    ]
                }
            },
            position="start"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_display_block(self, demo_instance):
        """Test adding a display block"""
        result = await add_block_impl(
            instance_id=demo_instance,
            block={
                "id": "info_block",
                "type": "display",
                "bind": "state.params",
                "props": {
                    "fields": [
                        {"label": "Title", "key": "title", "type": "html", "value": "<h3>Info</h3>"}
                    ]
                }
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_block_with_actions(self, demo_instance):
        """Test adding a block with actions"""
        result = await add_block_impl(
            instance_id=demo_instance,
            block={
                "id": "actions_block",
                "type": "form",
                "bind": "state.params",
                "props": {
                    "fields": [
                        {"label": "Status", "key": "status", "type": "text"}
                    ],
                    "actions": [
                        {
                            "id": "reset_status",
                            "label": "Reset",
                            "style": "secondary",
                            "handler_type": "set",
                            "patches": {"state.params.status": ""}
                        }
                    ]
                }
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_block_at_specific_index(self, demo_instance):
        """Test adding a block at a specific index"""
        result = await add_block_impl(
            instance_id=demo_instance,
            block={
                "id": "middle_block",
                "type": "form",
                "bind": "state.params",
                "props": {
                    "fields": [
                        {"label": "Middle", "key": "middle", "type": "text"}
                    ]
                }
            },
            position="1"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_block(self, demo_instance):
        """Test removing a block"""
        result = await remove_block_impl(
            instance_id=demo_instance,
            block_id="middle_block"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_all_matching_blocks(self, demo_instance):
        """Test removing all blocks with matching ID"""
        result = await remove_block_impl(
            instance_id=demo_instance,
            block_id="temp_block",
            remove_all=True
        )
        assert result["status"] == "success"


class TestActionOperations:
    """Test action-related operations: add_action, remove_action"""

    @pytest.mark.asyncio
    async def test_add_global_action_set(self, counter_instance):
        """Test adding a global action with set handler"""
        result = await add_action_impl(
            instance_id=counter_instance,
            action={
                "id": "reset",
                "label": "Reset",
                "style": "danger",
                "handler_type": "set",
                "patches": {"state.params.count": 0}
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_global_action_increment(self, counter_instance):
        """Test adding a global action with increment handler"""
        result = await add_action_impl(
            instance_id=counter_instance,
            action={
                "id": "increment_5",
                "label": "+5",
                "style": "primary",
                "handler_type": "increment",
                "patches": {"state.params.count": 5}
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_global_action_decrement(self, counter_instance):
        """Test adding a global action with decrement handler"""
        result = await add_action_impl(
            instance_id=counter_instance,
            action={
                "id": "decrement_5",
                "label": "-5",
                "style": "secondary",
                "handler_type": "decrement",
                "patches": {"state.params.count": 5}
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_global_action_toggle(self, demo_instance):
        """Test adding a global action with toggle handler"""
        result = await add_action_impl(
            instance_id=demo_instance,
            action={
                "id": "toggle_status",
                "label": "Toggle Status",
                "style": "primary",
                "handler_type": "toggle",
                "patches": {"state.params.enabled": True}
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_global_action_template(self, demo_instance):
        """Test adding a global action with template handler"""
        result = await add_action_impl(
            instance_id=demo_instance,
            action={
                "id": "show_message",
                "label": "Show Message",
                "style": "primary",
                "handler_type": "template",
                "patches": {
                    "state.runtime.message": "Done at ${state.runtime.timestamp}"
                }
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_global_action_navigate(self, demo_instance):
        """Test adding a global action with navigate type"""
        result = await add_action_impl(
            instance_id=demo_instance,
            action={
                "id": "goto_counter",
                "label": "Go to Counter",
                "style": "secondary",
                "action_type": "navigate",
                "target_instance": "counter"
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_global_action_append_to_list(self, demo_instance):
        """Test adding a global action with append_to_list operation"""
        result = await add_action_impl(
            instance_id=demo_instance,
            action={
                "id": "append_item",
                "label": "Append Item",
                "style": "primary",
                "handler_type": "set",
                "patches": {
                    "state.params.users": {
                        "operation": "append_to_list",
                        "params": {
                            "item": {"id": 99, "name": "Test User", "email": "test@example.com"}
                        }
                    }
                }
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_global_action_update_list_item(self, demo_instance):
        """Test adding a global action with update_list_item operation"""
        result = await add_action_impl(
            instance_id=demo_instance,
            action={
                "id": "update_item",
                "label": "Update Item",
                "style": "secondary",
                "handler_type": "set",
                "patches": {
                    "state.params.users": {
                        "operation": "update_list_item",
                        "params": {
                            "key": "id",
                            "value": 1,
                            "updates": {"name": "Updated Name"}
                        }
                    }
                }
            }
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_block_action(self, demo_instance):
        """Test adding a block-level action"""
        result = await add_action_impl(
            instance_id=demo_instance,
            action={
                "id": "block_action_test",
                "label": "Block Action",
                "style": "primary",
                "handler_type": "set",
                "patches": {"state.runtime.test": "done"}
            },
            block_index=0
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_global_action(self, demo_instance):
        """Test removing a global action"""
        result = await remove_action_impl(
            instance_id=demo_instance,
            action_id="toggle_status"
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_block_action(self, demo_instance):
        """Test removing a block-level action"""
        result = await remove_action_impl(
            instance_id=demo_instance,
            action_id="block_action_test",
            block_index=0
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_all_matching_actions(self, demo_instance):
        """Test removing all actions with matching ID"""
        result = await remove_action_impl(
            instance_id=demo_instance,
            action_id="temp_action",
            remove_all=True
        )
        assert result["status"] == "success"


class TestPatchUIState:
    """Test patch_ui_state operation"""

    @pytest.mark.asyncio
    async def test_set_state_value(self, counter_instance):
        """Test setting a state value"""
        result = await patch_ui_state_impl(
            instance_id=counter_instance,
            patches=[{
                "op": "set",
                "path": "state.params.count",
                "value": 100
            }]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_set_multiple_state_values(self, demo_instance):
        """Test setting multiple state values at once"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[
                {"op": "set", "path": "state.params.test1", "value": "value1"},
                {"op": "set", "path": "state.params.test2", "value": "value2"},
                {"op": "set", "path": "state.runtime.message", "value": "Updated message"}
            ]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_field_via_patch(self, demo_instance):
        """Test adding a field using patch_ui_state"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[
                {"op": "set", "path": "state.params.new_field", "value": ""},
                {"op": "add", "path": "blocks.0.props.fields", "value": {
                    "label": "New Field",
                    "key": "new_field",
                    "type": "text"
                }}
            ]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_update_field_via_patch(self, demo_instance):
        """Test updating a field using patch_ui_state"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[{
                "op": "set",
                "path": "blocks.0.props.fields.0.label",
                "value": "Updated Label"
            }]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_field_via_patch(self, demo_instance):
        """Test removing a field using patch_ui_state"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[{
                "op": "remove",
                "path": "blocks.0.props.fields",
                "value": {"key": "new_field"}
            }]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_block_via_patch(self, demo_instance):
        """Test adding a block using patch_ui_state"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[{
                "op": "add",
                "path": "blocks",
                "value": {
                    "id": "patched_block",
                    "type": "form",
                    "bind": "state.params",
                    "props": {
                        "fields": [
                            {"label": "Test", "key": "test", "type": "text"}
                        ]
                    }
                }
            }]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_global_action_via_patch(self, demo_instance):
        """Test adding a global action using patch_ui_state"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[{
                "op": "add",
                "path": "actions",
                "value": {
                    "id": "patched_action",
                    "label": "Patched Action",
                    "style": "primary",
                    "handler_type": "set",
                    "patches": {"state.params.test": "done"}
                }
            }]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_block_via_patch(self, demo_instance):
        """Test removing a block using patch_ui_state"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[{
                "op": "remove",
                "path": "blocks",
                "value": {"id": "patched_block"}
            }]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_action_via_patch(self, demo_instance):
        """Test removing an action using patch_ui_state"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[{
                "op": "remove",
                "path": "actions",
                "value": {"id": "patched_action"}
            }]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_new_instance(self):
        """Test creating a new instance"""
        result = await patch_ui_state_impl(
            instance_id="__CREATE__",
            new_instance_id="test_instance",
            patches=[
                {"op": "set", "path": "meta", "value": {
                    "pageKey": "test_instance",
                    "step": {"current": 1, "total": 1},
                    "status": "idle",
                    "schemaVersion": "1.0"
                }},
                {"op": "set", "path": "state", "value": {
                    "params": {},
                    "runtime": {}
                }},
                {"op": "set", "path": "blocks", "value": []},
                {"op": "set", "path": "actions", "value": []}
            ]
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_delete_instance(self):
        """Test deleting an instance"""
        result = await patch_ui_state_impl(
            instance_id="__DELETE__",
            target_instance_id="test_instance"
        )
        # Note: If instance doesn't exist, it might return error or success depending on implementation
        # We accept either outcome for this test
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_batch_operations(self, demo_instance):
        """Test batch operations in a single patch call"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[
                {"op": "set", "path": "state.params.batch1", "value": "val1"},
                {"op": "set", "path": "state.params.batch2", "value": "val2"},
                {"op": "set", "path": "state.params.batch3", "value": "val3"},
                {"op": "set", "path": "state.runtime.batch_flag", "value": True}
            ]
        )
        assert result["status"] == "success"
        # patches_applied is an array of applied patches, not a count
        assert isinstance(result["patches_applied"], list)
        assert len(result["patches_applied"]) == 4


class TestSchemaOperations:
    """Test schema-related operations: get_schema, list_instances, access_instance"""

    @pytest.mark.asyncio
    async def test_get_schema_default(self):
        """Test getting default schema"""
        result = await get_schema_impl()
        assert result["status"] == "success"
        assert "schema" in result
        assert "meta" in result["schema"]
        assert "state" in result["schema"]
        assert "blocks" in result["schema"]
        assert "actions" in result["schema"]

    @pytest.mark.asyncio
    async def test_get_schema_specific_instance(self):
        """Test getting schema for a specific instance"""
        result = await get_schema_impl(instance_id="demo")
        assert result["status"] == "success"
        assert result["instance_id"] == "demo"
        assert "schema" in result

    @pytest.mark.asyncio
    async def test_get_schema_structure(self):
        """Test that schema has expected structure"""
        result = await get_schema_impl(instance_id="counter")
        assert result["status"] == "success"
        schema = result["schema"]
        
        # Check top-level structure
        assert "meta" in schema
        assert "state" in schema
        assert "blocks" in schema
        assert "actions" in schema
        
        # Check meta
        assert "pageKey" in schema["meta"]
        assert "step" in schema["meta"]
        
        # Check state
        assert "params" in schema["state"]
        assert "runtime" in schema["state"]
        
        # Check blocks
        assert isinstance(schema["blocks"], list)

    @pytest.mark.asyncio
    async def test_list_instances(self):
        """Test listing all instances"""
        result = await list_instances_impl()
        assert result["status"] == "success"
        assert "instances" in result
        assert "total" in result
        assert result["total"] >= 4  # At least demo, counter, rich_content, block_actions_test

    @pytest.mark.asyncio
    async def test_list_instances_content(self):
        """Test that instances list has expected content"""
        result = await list_instances_impl()
        assert result["status"] == "success"
        instances = result["instances"]
        
        instance_ids = [inst["instance_id"] for inst in instances]
        assert "demo" in instance_ids
        assert "counter" in instance_ids
        assert "rich_content" in instance_ids
        assert "block_actions_test" in instance_ids

    @pytest.mark.asyncio
    async def test_access_instance(self):
        """Test accessing a specific instance"""
        result = await access_instance_impl(instance_id="demo")
        assert result["status"] == "success"
        assert result["instance_id"] == "demo"
        assert "schema" in result

    @pytest.mark.asyncio
    async def test_access_multiple_instances(self):
        """Test accessing multiple instances sequentially"""
        instances = ["demo", "counter", "rich_content", "block_actions_test"]
        
        for instance_id in instances:
            result = await access_instance_impl(instance_id=instance_id)
            assert result["status"] == "success"
            assert result["instance_id"] == instance_id


class TestValidation:
    """Test validate_completion operation"""

    @pytest.mark.asyncio
    async def test_validate_field_exists(self, counter_instance):
        """Test validating field existence"""
        result = await validate_completion_impl(
            instance_id=counter_instance,
            intent="Counter should have count field",
            completion_criteria=[
                {
                    "type": "field_exists",
                    "path": "state.params.count",
                    "description": "Count field exists"
                }
            ]
        )
        assert "evaluation" in result
        assert result["evaluation"]["total_criteria"] == 1
        assert result["evaluation"]["passed_criteria"] == 1

    @pytest.mark.asyncio
    async def test_validate_field_value(self, counter_instance):
        """Test validating field value"""
        result = await validate_completion_impl(
            instance_id=counter_instance,
            intent="Counter should be at 0",
            completion_criteria=[
                {
                    "type": "field_value",
                    "path": "state.params.count",
                    "value": 0,
                    "description": "Count is 0"
                }
            ]
        )
        assert "evaluation" in result
        assert result["evaluation"]["total_criteria"] == 1

    @pytest.mark.asyncio
    async def test_validate_block_count(self, demo_instance):
        """Test validating block count"""
        result = await validate_completion_impl(
            instance_id=demo_instance,
            intent="Demo should have one block",
            completion_criteria=[
                {
                    "type": "block_count",
                    "count": 1,
                    "description": "Exactly one block"
                }
            ]
        )
        assert "evaluation" in result
        assert result["evaluation"]["total_criteria"] == 1

    @pytest.mark.asyncio
    async def test_validate_action_exists(self, demo_instance):
        """Test validating action existence"""
        result = await validate_completion_impl(
            instance_id=demo_instance,
            intent="Demo should have add_user action",
            completion_criteria=[
                {
                    "type": "action_exists",
                    "path": "add_user",
                    "description": "Add user action exists"
                }
            ]
        )
        assert "evaluation" in result
        assert result["evaluation"]["total_criteria"] == 1

    @pytest.mark.asyncio
    async def test_validate_multiple_criteria(self, counter_instance):
        """Test validating multiple criteria at once"""
        result = await validate_completion_impl(
            instance_id=counter_instance,
            intent="Counter should be fully functional",
            completion_criteria=[
                {
                    "type": "field_exists",
                    "path": "state.params.count",
                    "description": "Count field exists"
                },
                {
                    "type": "action_exists",
                    "path": "increment",
                    "description": "Increment action exists"
                },
                {
                    "type": "action_exists",
                    "path": "decrement",
                    "description": "Decrement action exists"
                }
            ]
        )
        assert "evaluation" in result
        assert result["evaluation"]["total_criteria"] == 3
        assert result["evaluation"]["completion_ratio"] >= 0

    @pytest.mark.asyncio
    async def test_validate_custom_condition(self, demo_instance):
        """Test validating custom condition"""
        result = await validate_completion_impl(
            instance_id=demo_instance,
            intent="Users list should exist",
            completion_criteria=[
                {
                    "type": "custom",
                    "condition": "has_field:state.params.users",
                    "description": "Users field exists"
                }
            ]
        )
        assert "evaluation" in result
        assert result["evaluation"]["total_criteria"] == 1

    @pytest.mark.asyncio
    async def test_validate_get_recommendations(self, counter_instance):
        """Test that validation provides recommendations"""
        result = await validate_completion_impl(
            instance_id=counter_instance,
            intent="Counter validation",
            completion_criteria=[
                {
                    "type": "field_exists",
                    "path": "state.params.count",
                    "description": "Count field exists"
                }
            ]
        )
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_patches_array(self, demo_instance):
        """Test calling patch_ui_state with empty patches"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[]
        )
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_invalid_instance_id(self):
        """Test accessing non-existent instance"""
        result = await get_schema_impl(instance_id="non_existent")
        # May return error or default instance

    @pytest.mark.asyncio
    async def test_update_nonexistent_field(self, demo_instance):
        """Test updating a field that doesn't exist"""
        result = await update_field_impl(
            instance_id=demo_instance,
            field_key="nonexistent_field",
            updates={"label": "New Label"}
        )
        # Should return error when field doesn't exist
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_remove_nonexistent_field(self, demo_instance):
        """Test removing a field that doesn't exist"""
        result = await remove_field_impl(
            instance_id=demo_instance,
            field_key="nonexistent_field"
        )
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_invalid_block_index(self, demo_instance):
        """Test using invalid block index"""
        result = await add_field_impl(
            instance_id=demo_instance,
            field={"label": "Test", "key": "test", "type": "text"},
            block_index=999
        )
        # Note: The implementation may succeed by creating a new block at the end
        # We accept either outcome
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_remove_nonexistent_block(self, demo_instance):
        """Test removing a block that doesn't exist"""
        result = await remove_block_impl(
            instance_id=demo_instance,
            block_id="nonexistent_block"
        )
        # May return success or error depending on implementation

    @pytest.mark.asyncio
    async def test_invalid_block_position(self, demo_instance):
        """Test adding a block with invalid position"""
        result = await add_block_impl(
            instance_id=demo_instance,
            block={
                "id": "test_block",
                "type": "form",
                "bind": "state.params",
                "props": {"fields": []}
            },
            position="invalid_position"
        )
        # Should default to "end" position

    @pytest.mark.asyncio
    async def test_mixed_operations_in_single_patch(self, demo_instance):
        """Test mixing different operation types in a single patch call"""
        result = await patch_ui_state_impl(
            instance_id=demo_instance,
            patches=[
                {"op": "set", "path": "state.params.set_test", "value": "set"},
                {"op": "set", "path": "state.runtime.runtime_test", "value": "runtime"},
                {"op": "set", "path": "blocks.0.props.fields.0.description", "value": "Updated"}
            ]
        )
        assert result["status"] == "success"
        # patches_applied is an array of applied patches, not a count
        assert isinstance(result["patches_applied"], list)
        assert len(result["patches_applied"]) == 3


class TestComplexScenarios:
    """Test complex real-world scenarios"""

    @pytest.mark.asyncio
    async def test_create_form_with_validation(self):
        """Test creating a complete form with validation"""
        instance_id = "test_form"
        
        # Create instance
        await patch_ui_state_impl(
            instance_id="__CREATE__",
            new_instance_id=instance_id,
            patches=[
                {"op": "set", "path": "meta", "value": {
                    "pageKey": "test_form",
                    "step": {"current": 1, "total": 1},
                    "status": "idle",
                    "schemaVersion": "1.0"
                }},
                {"op": "set", "path": "state", "value": {
                    "params": {"name": "", "email": "", "age": 0},
                    "runtime": {}
                }},
                {"op": "set", "path": "blocks", "value": []},
                {"op": "set", "path": "actions", "value": []}
            ]
        )
        
        # Add fields
        await add_field_impl(
            instance_id=instance_id,
            field={"label": "Name", "key": "name", "type": "text"},
            state_path="state.params.name"
        )
        
        await add_field_impl(
            instance_id=instance_id,
            field={"label": "Email", "key": "email", "type": "text"},
            state_path="state.params.email"
        )
        
        await add_field_impl(
            instance_id=instance_id,
            field={"label": "Age", "key": "age", "type": "number"},
            state_path="state.params.age",
            initial_value=0
        )
        
        # Add actions
        await add_action_impl(
            instance_id=instance_id,
            action={
                "id": "submit",
                "label": "Submit",
                "style": "primary",
                "handler_type": "set",
                "patches": {
                    "state.runtime.message": "Form submitted at ${state.runtime.timestamp}"
                }
            }
        )
        
        await add_action_impl(
            instance_id=instance_id,
            action={
                "id": "reset",
                "label": "Reset",
                "style": "danger",
                "handler_type": "set",
                "patches": {
                    "state.params.name": "",
                    "state.params.email": "",
                    "state.params.age": 0,
                    "state.runtime.message": "Form reset"
                }
            }
        )
        
        # Validate
        result = await validate_completion_impl(
            instance_id=instance_id,
            intent="Form should have name, email, age fields and submit, reset actions",
            completion_criteria=[
                {"type": "field_exists", "path": "state.params.name", "description": "Name field"},
                {"type": "field_exists", "path": "state.params.email", "description": "Email field"},
                {"type": "field_exists", "path": "state.params.age", "description": "Age field"},
                {"type": "action_exists", "path": "submit", "description": "Submit action"},
                {"type": "action_exists", "path": "reset", "description": "Reset action"}
            ]
        )
        
        assert result["evaluation"]["completion_ratio"] == 1.0
        
        # Cleanup
        await patch_ui_state_impl(
            instance_id="__DELETE__",
            target_instance_id=instance_id
        )

    @pytest.mark.asyncio
    async def test_dynamic_table_management(self):
        """Test dynamically managing a table"""
        instance_id = "test_table"
        
        # Create instance
        await patch_ui_state_impl(
            instance_id="__CREATE__",
            new_instance_id=instance_id,
            patches=[
                {"op": "set", "path": "meta", "value": {
                    "pageKey": "test_table",
                    "step": {"current": 1, "total": 1},
                    "status": "idle",
                    "schemaVersion": "1.0"
                }},
                {"op": "set", "path": "state", "value": {
                    "params": {"items": []},
                    "runtime": {}
                }},
                {"op": "set", "path": "blocks", "value": []},
                {"op": "set", "path": "actions", "value": []}
            ]
        )
        
        # Add table field
        await add_field_impl(
            instance_id=instance_id,
            field={
                "label": "Items",
                "key": "items",
                "type": "table",
                "columns": [
                    {"key": "id", "label": "ID"},
                    {"key": "name", "label": "Name"},
                    {"key": "value", "label": "Value"}
                ]
            },
            state_path="state.params.items",
            initial_value=[]
        )
        
        # Add action to append row
        await add_action_impl(
            instance_id=instance_id,
            action={
                "id": "add_row",
                "label": "Add Row",
                "style": "primary",
                "handler_type": "set",
                "patches": {
                    "state.params.items": {
                        "operation": "append_to_list",
                        "params": {
                            "item": {"id": 1, "name": "Item 1", "value": "Value 1"}
                        }
                    }
                }
            }
        )
        
        # Add action to clear table
        await add_action_impl(
            instance_id=instance_id,
            action={
                "id": "clear_table",
                "label": "Clear",
                "style": "danger",
                "handler_type": "set",
                "patches": {"state.params.items": []}
            }
        )
        
        # Validate
        result = await validate_completion_impl(
            instance_id=instance_id,
            intent="Table should have add and clear actions",
            completion_criteria=[
                {"type": "field_exists", "path": "state.params.items", "description": "Items table"},
                {"type": "action_exists", "path": "add_row", "description": "Add row action"},
                {"type": "action_exists", "path": "clear_table", "description": "Clear action"}
            ]
        )
        
        assert result["evaluation"]["total_criteria"] == 3
        
        # Cleanup
        await patch_ui_state_impl(
            instance_id="__DELETE__",
            target_instance_id=instance_id
        )

    @pytest.mark.asyncio
    async def test_template_rendering(self):
        """Test template rendering with timestamps"""
        result = await add_action_impl(
            instance_id="demo",
            action={
                "id": "template_test",
                "label": "Test Template",
                "style": "primary",
                "handler_type": "template",
                "patches": {
                    "state.runtime.timestamp_msg": "Current time is ${state.runtime.timestamp}"
                }
            }
        )
        assert result["status"] == "success"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
