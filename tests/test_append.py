from backend.core.defaults import get_default_instances
from backend.fastapi.services.event_handler import EventHandler
import asyncio

async def test():
    schemas = get_default_instances()
    demo = schemas['demo']
    handler = EventHandler()

    print('Initial users count:', len(demo.state.params.get('users', [])))

    # 测试添加用户
    patch = await handler.handle_event(
        'action_click',
        'add_user',
        'demo',
        {},
        demo
    )

    print('Patch keys:', list(patch.keys()))
    if 'state.params.users' in patch:
        print('New users:', patch['state.params.users'])
        print('New users count:', len(patch['state.params.users']))
    else:
        print('No patch for state.params.users')

    # 测试 _apply_patches
    patches = {
        'state.params.users': {
            'mode': 'operation',
            'operation': 'append_to_list',
            'params': {
                'items': {
                    'id': 6,
                    'name': '赵六',
                    'email': 'zhaoliu@example.com',
                    'status': 'pending',
                    'avatar': 'https://picsum.photos/seed/zhaoliu/100/100.jpg'
                }
            }
        }
    }

    result = await handler._apply_patches(patches, demo)
    print('_apply_patches result keys:', list(result.keys()))
    if 'state.params.users' in result:
        print('New users count:', len(result['state.params.users']))

asyncio.run(test())
