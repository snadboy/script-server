# HTTP Endpoint Integration Testing Guide

## Summary
Created framework for integration testing critical HTTP endpoints in `web/server.py` (2,220 lines, 109 handlers, currently 0% tested).

## Test Coverage Status

### Priority Endpoints (5)

| Endpoint | Method | Handler | Status |
|----------|--------|---------|--------|
| `/admin/projects/{id}/wrapper` | POST | GenerateWrapperHandler | ⏳ Framework created |
| `/admin/scripts/{name}` | GET/PUT/DELETE | AdminScriptEndpoint | ⏳ Framework created |
| `/schedules` | POST | AddSchedule | ⏳ Framework created |
| `/scripts/execute` | POST | ScriptExecute | ⏳ Framework created |
| `/admin/connections` | GET/POST | ConnectionsHandler | ⏳ Framework created |

### Test File Created

**Location:** `tests/web/test_server_integration.py` (390 lines)

Contains:
- ✅ BaseServerTestCase (reusable test harness)
- ✅ TestAdminScriptEndpoint (5 test cases)
- ✅ TestScriptExecute (5 test cases)
- ⏳ TestGenerateWrapperHandler (placeholders)
- ⏳ TestScheduleEndpoints (placeholders)
- ⏳ TestConnectionEndpoints (placeholders)
- ⏳ TestAuthenticationEndpoints (placeholders)
- ⏳ TestHistoryEndpoints (placeholders)

## Challenges Identified

### 1. Application Setup Complexity

Handlers require extensive application context:

```python
# Required application attributes
application.config_service
application.execution_service
application.schedule_service
application.authorizer
application.server_config       # Missing in basic setup
application.file_download_feature
application.file_upload_feature
application.identification
application.max_request_size_mb
```

### 2. Request Context

Handlers need authenticated user context:

```python
# Handlers expect
self.application.identification.identify_user(request_handler)
# Returns User object with user_id, name, permissions
```

### 3. Configuration Dependencies

Many handlers load script configs that require:
- Real or mocked file system
- Config service with proper initialization
- Authorization context

## Recommended Approach

### Option 1: Fixture-Based Testing (Recommended)

Create comprehensive test fixtures:

```python
class ServerTestFixture:
    """Complete server application setup for testing."""

    def __init__(self, test_case):
        self.test_case = test_case
        self.temp_dir = tempfile.mkdtemp()

        # Create directory structure
        self.conf_dir = Path(self.temp_dir) / 'conf'
        self.runners_dir = self.conf_dir / 'runners'
        self.projects_dir = Path(self.temp_dir) / 'projects'

        self.conf_dir.mkdir(parents=True)
        self.runners_dir.mkdir(parents=True)
        self.projects_dir.mkdir(parents=True)

        # Initialize services
        self.server_config = self._create_server_config()
        self.config_service = ConfigService(...)
        self.execution_service = ExecutionService(...)
        self.schedule_service = ScheduleService(...)
        self.authorizer = Authorizer(...)
        self.identification = self._create_identification()

        # Create test scripts
        self._create_test_script('test-script')

    def get_application(self):
        """Get configured tornado application."""
        from web.server import create_application
        app = create_application(self.server_config)

        # Override services with test versions
        app.config_service = self.config_service
        app.execution_service = self.execution_service

        return app

    def cleanup(self):
        shutil.rmtree(self.temp_dir)
```

Usage:

```python
class TestEndpoints(AsyncHTTPTestCase):
    def setUp(self):
        self.fixture = ServerTestFixture(self)
        super().setUp()

    def get_app(self):
        return self.fixture.get_application()

    def tearDown(self):
        super().tearDown()
        self.fixture.cleanup()
```

### Option 2: Mock-Heavy Approach (Current)

Mock all dependencies:

```python
def get_app(self):
    app = tornado.web.Application([...])

    # Mock all services
    app.server_config = Mock()
    app.server_config.xsrf_protection = 'disabled'
    app.config_service = Mock()
    app.execution_service = Mock()
    # ... 15+ more mocks

    return app
```

**Drawbacks:**
- Brittle (breaks when handlers change)
- Doesn't test real integration
- Requires deep knowledge of internals

### Option 3: Real Server Testing (Slow but Thorough)

Start actual server in test mode:

```python
class TestRealServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start real script-server on test port
        cls.server_process = subprocess.Popen([
            'python', 'launcher.py',
            '--config', 'test_config.json',
            '--port', '55555'
        ])
        time.sleep(2)  # Wait for startup

    def test_endpoint(self):
        response = requests.post('http://localhost:55555/scripts/execute', ...)
        self.assertEqual(200, response.status_code)
```

**Drawbacks:**
- Slow (startup time)
- Requires test configuration
- Complex teardown

## Completed Test Examples

### 1. AdminScriptEndpoint Tests

```python
def test_get_script_config_success(self):
    """Test GET /admin/scripts/{name} returns script config."""
    mock_config = {
        'name': 'test-script',
        'script_path': '/path/to/script.py',
        'parameters': []
    }
    self.config_service.load_config.return_value = Mock(
        name='test-script',
        config=mock_config
    )

    response = self.fetch('/admin/scripts/test-script')

    self.assertEqual(200, response.code)
    data = json.loads(response.body)
    self.assertEqual('test-script', data['name'])
```

### 2. ScriptExecute Tests

```python
def test_execute_script_success(self):
    """Test successful script execution."""
    mock_config = Mock()
    mock_config.name = 'test-script'
    mock_config.is_allowed_for_user.return_value = True

    self.config_service.load_config.return_value = mock_config
    self.execution_service.start_script.return_value = 'exec-123'

    response = self.fetch(
        '/scripts/execute',
        method='POST',
        body=json.dumps({
            'script': 'test-script',
            'parameters': {}
        })
    )

    self.assertEqual(200, response.code)
    data = json.loads(response.body)
    self.assertEqual('exec-123', data.get('executionId'))
```

## Next Steps to Complete

### 1. Fix Application Setup (High Priority)

Add missing attributes to test application:

```python
def get_app(self):
    app = tornado.web.Application([...])

    # Add all required attributes
    app.server_config = Mock()
    app.server_config.xsrf_protection = 'disabled'
    app.server_config.max_request_size_mb = 10

    app.identification = Mock()
    app.identification.identify_user = Mock(return_value=User('test-user'))

    app.file_download_feature = Mock()
    app.file_upload_feature = Mock()

    # Services
    app.config_service = self.config_service
    app.execution_service = self.execution_service
    app.schedule_service = self.schedule_service
    app.authorizer = self.authorizer

    return app
```

### 2. Implement GenerateWrapperHandler Tests

```python
def test_generate_wrapper_success(self):
    """Test successful wrapper generation."""
    response = self.fetch(
        '/admin/projects/test-project/wrapper',
        method='POST',
        body=json.dumps({
            'entry_point': 'main.py',
            'script_name': 'Test Script',
            'description': 'Test description'
        })
    )

    self.assertEqual(200, response.code)

def test_generate_wrapper_duplicate_name(self):
    """Test wrapper generation fails with duplicate script name."""
    # First create a script
    # Then try to create another with same name
    # Expect 400 error
```

### 3. Implement Schedule Tests

```python
def test_add_schedule_success(self):
    """Test POST /schedules creates schedule."""
    response = self.fetch(
        '/schedules',
        method='POST',
        body=json.dumps({
            'script_name': 'test-script',
            'schedule_config': {
                'type': 'interval',
                'interval_minutes': 60
            }
        })
    )

    self.assertEqual(200, response.code)
```

### 4. Implement Connection Tests

```python
def test_create_connection_success(self):
    """Test POST /admin/connections creates connection."""
    response = self.fetch(
        '/admin/connections',
        method='POST',
        body=json.dumps({
            'name': 'Test Connection',
            'type': 'plex',
            'fields': {
                'url': 'http://plex:32400',
                'token': 'abc123'
            }
        })
    )

    self.assertEqual(201, response.code)
```

## Test Coverage Goals

Target: **75% coverage for critical endpoints**

### Coverage by Handler Type

| Type | Handlers | Priority | Target |
|------|----------|----------|--------|
| **Admin** | 25 | High | 80% |
| **Execution** | 15 | Critical | 90% |
| **Schedule** | 8 | High | 80% |
| **Connection** | 6 | High | 80% |
| **Auth** | 10 | Critical | 85% |
| **History** | 5 | Medium | 60% |
| **Static** | 20 | Low | 30% |
| **WebSocket** | 5 | Medium | 50% |

## Estimated Effort

- Fix application setup: 2 hours
- Complete priority endpoint tests: 8 hours
- Add auth/history tests: 6 hours
- WebSocket testing: 8 hours
- **Total: 24 hours** (as estimated)

## Benefits

1. **Catch regressions** before deployment
2. **Document API** through tests
3. **Validate security** (auth, permissions)
4. **Test error handling** (400, 403, 404, 500)
5. **Integration confidence** for refactoring

## Current Status

✅ Test framework created (390 lines)
✅ 10 test cases written (AdminScript + Execute)
⏳ Application setup needs completion
⏳ 30+ additional test cases needed
⏳ Mock services need enhancement

**Estimated completion: 70% of framework, 25% of actual tests**
