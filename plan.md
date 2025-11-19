# Pomodoro Timer Web App - Development Plan

A phased implementation plan to build a Flask-based Pomodoro timer with frontend timer logic, session logging backend, and comprehensive tests. Each phase delivers testable, incremental functionality following the architecture in `architecture.md`.

## Implementation Steps

### 1. Setup Project Structure and Dependencies

**Objective:** Create the foundational directory structure and install required dependencies.

**Tasks:**
- Create `pomodoro_app/` directory with subdirectories:
  - `static/` (for CSS and JavaScript files)
  - `templates/` (for HTML templates)
- Install Flask using `uv pip install flask`
- Create `requirements.txt` with Flask and other dependencies
- Add basic configuration files if needed

**Testing:** Verify directory structure exists and Flask can be imported.

**Granularity:** Single atomic step - infrastructure setup should be done together to ensure consistent environment.

---

### 2. Build Minimal Flask Backend

**Objective:** Implement a basic Flask application that serves the main page.

**Tasks:**
- Create `app.py` with:
  - Flask app initialization
  - Index route (`/`) serving `index.html`
  - Basic app configuration (debug mode, host, port)
  - Optional: health check endpoint (`/health`) for testing
- Create minimal `templates/index.html` (placeholder content)

**Testing:**
- Run Flask app and verify it starts without errors
- Access index route and confirm HTML is served
- Test health check endpoint returns 200 OK

**Granularity:** 
- Function level: Separate route handlers for each endpoint
- Each route should be independently testable

---

### 3. Implement Session Logging Backend

**Objective:** Add API endpoints for logging and retrieving Pomodoro sessions.

**Tasks:**
- Implement POST `/log` endpoint:
  - Accept JSON payload: `{session_type, action, started_at, ended_at}`
  - Validate input data (required fields, valid values)
  - Append to `pomodoro_log.txt` (JSON Lines format recommended)
  - Return success/error response
- Implement GET `/history` endpoint:
  - Read `pomodoro_log.txt`
  - Parse log entries
  - Return JSON array of session events
- Create helper functions:
  - `validate_session_data(data)` - validates incoming session data
  - `append_to_log(session_data)` - handles file I/O
  - `read_log_history()` - reads and parses log file

**Testing:**
- Unit tests for `validate_session_data()` with valid/invalid inputs
- Unit tests for `append_to_log()` using temporary files
- Unit tests for `read_log_history()` with sample log data
- Integration tests for `/log` endpoint (POST valid/invalid data)
- Integration tests for `/history` endpoint (empty log, populated log)

**Granularity:**
- **Function level:** Each helper function tested independently
- **Endpoint level:** Each API route tested separately
- **Use pytest fixtures** for temporary log files to ensure test isolation

---

### 4. Create Frontend HTML Structure

**Objective:** Build the HTML user interface matching the mockup design.

**Tasks:**
- Implement `templates/index.html` with:
  - Timer display section (minutes:seconds)
  - Session type indicator (Work/Short Break/Long Break)
  - Session counter display (e.g., "Session 1 of 4")
  - Control buttons:
    - Start/Pause button
    - Skip button
    - Reset button
  - Settings panel:
    - Work duration input
    - Short break duration input
    - Long break duration input
    - Save settings button
  - Link to `static/style.css` and `static/timer.js`

**Testing:**
- Visual inspection: All elements render correctly
- Accessibility check: Proper semantic HTML, labels for inputs
- Manual test: Buttons exist and have appropriate IDs/classes

**Granularity:** Single HTML file creation - structure should be cohesive, but plan for CSS/JS to be separate concerns.

---

### 5. Implement Timer Logic in JavaScript

**Objective:** Develop the core timer functionality and state management.

**Tasks:**
- Create `static/timer.js` with modular functions:
  
  **Core Timer Functions:**
  - `initTimer()` - Initialize timer state and load settings
  - `startTimer()` - Begin countdown
  - `pauseTimer()` - Pause current session
  - `resumeTimer()` - Resume paused session
  - `skipSession()` - Skip to next session
  - `resetTimer()` - Reset to initial state
  
  **State Management:**
  - `updateTimerDisplay(minutes, seconds)` - Update UI
  - `switchSession(sessionType)` - Transition between work/break
  - `incrementSessionCount()` - Track completed work sessions
  - `determineNextSession()` - Logic for short vs long breaks
  
  **Countdown Mechanics:**
  - `tick()` - Decrement timer by one second
  - `handleSessionComplete()` - Actions when timer reaches 0:00
  
  **Settings:**
  - `loadSettings()` - Load from localStorage or defaults
  - `saveSettings(workDuration, shortBreak, longBreak)` - Persist settings
  
**Testing:**
- Unit tests for each function using Jest/QUnit:
  - Test `tick()` decrements time correctly
  - Test `switchSession()` changes state appropriately
  - Test `determineNextSession()` returns long break after 4th session
  - Test `saveSettings()` and `loadSettings()` with localStorage mocks
  - Test `handleSessionComplete()` triggers correct next session
- Mock `setInterval` for timing tests to avoid real delays

**Granularity:**
- **Function level:** Each timer function should be pure and testable in isolation
- **Group by responsibility:** Timer mechanics, state management, settings should be separate modules/concerns
- **Use dependency injection** where possible (pass DOM elements as parameters)

---

### 6. Add Frontend-Backend Integration

**Objective:** Connect JavaScript timer to Flask logging API.

**Tasks:**
- Implement API communication functions in `timer.js`:
  - `logSession(sessionData)` - POST to `/log` endpoint
  - `fetchHistory()` - GET from `/history` endpoint (optional)
  - `handleLogError(error)` - Error handling for failed requests
  
- Integrate logging into timer lifecycle:
  - Call `logSession()` when session completes
  - Call `logSession()` when session is skipped
  - Track session start/end timestamps
  
- Add user feedback:
  - Display success/error messages for logging
  - Optional: Show loading state during API calls

**Testing:**
- Mock fetch API for unit tests:
  - Test `logSession()` sends correct payload
  - Test `fetchHistory()` processes response correctly
  - Test error handling for network failures, 4xx, 5xx responses
- Integration tests with running Flask backend:
  - Start timer, complete session, verify log file updated
  - Skip session, verify skip action logged
  - Test with backend down (error handling)

**Granularity:**
- **Function level:** Each API call wrapped in testable function
- **Mock network layer** for unit tests; use real backend for integration tests

---

### 7. Apply CSS Styling

**Objective:** Implement modern, responsive UI design.

**Tasks:**
- Create `static/style.css` with:
  - Layout and positioning (flexbox/grid)
  - Typography and color scheme
  - Timer display styling (large, readable font)
  - Button styles with hover/active states
  - Settings panel styling
  - Responsive design (mobile-friendly)
  - Animations:
    - Timer state transitions
    - Button press feedback
    - Session change notifications
  - Visual indicators:
    - Different colors for work vs break sessions
    - Progress indication (optional)

**Testing:**
- Visual regression testing (manual or screenshot comparison)
- Responsive design testing (different screen sizes)
- Browser compatibility testing
- Accessibility: Color contrast, focus indicators

**Granularity:** CSS can be developed as a whole, but organize into logical sections (layout, components, animations, responsive).

---

### 8. Write Backend Tests

**Objective:** Comprehensive pytest test suite for Flask application.

**Tasks:**
- Create `tests/` directory with:
  - `test_app.py` - Flask route tests
  - `test_logging.py` - Session logging tests
  - `conftest.py` - Pytest fixtures and configuration

- Test suites:
  
  **Route Tests:**
  - Test `GET /` returns 200 and renders HTML
  - Test `POST /log` with valid data returns 200
  - Test `POST /log` with invalid data returns 400
  - Test `POST /log` with missing fields returns 400
  - Test `GET /history` returns JSON array
  - Test `GET /history` with empty log returns empty array
  
  **Logging Tests:**
  - Test `validate_session_data()` accepts valid inputs
  - Test `validate_session_data()` rejects invalid session types
  - Test `validate_session_data()` rejects invalid actions
  - Test `append_to_log()` creates file if not exists
  - Test `append_to_log()` appends to existing file
  - Test `read_log_history()` parses JSON Lines correctly
  - Test `read_log_history()` handles corrupted log entries
  
  **Fixtures:**
  - `tmp_log_file` - Temporary log file for test isolation
  - `client` - Flask test client
  - `sample_session_data` - Valid test data

**Testing:**
- Run `pytest` with coverage: `pytest --cov=pomodoro_app`
- Aim for >90% code coverage
- Test both success and failure paths

**Granularity:**
- **One test function per behavior/edge case**
- **Use parametrize for multiple similar test cases**
- **Fixtures for shared setup** (temporary files, test clients)

---

### 9. Write Frontend Tests

**Objective:** Unit tests for JavaScript timer logic.

**Tasks:**
- Set up JavaScript testing framework:
  - Option A: Jest (recommended for Node.js environments)
  - Option B: QUnit (lighter weight, browser-based)
  
- Create test files:
  - `tests/test_timer.js` - Timer logic tests
  - `tests/test_integration.js` - Frontend integration tests

- Test suites:
  
  **Timer Logic:**
  - Test initial state (25:00, session 1, work mode)
  - Test `tick()` decrements seconds correctly
  - Test `tick()` decrements minutes when seconds reach 0
  - Test timer stops at 0:00
  - Test `pauseTimer()` stops countdown
  - Test `resumeTimer()` continues from paused time
  - Test `resetTimer()` returns to initial state
  
  **Session Management:**
  - Test session switches to short break after work session
  - Test session count increments after work session
  - Test long break occurs after 4th work session
  - Test session count resets after long break
  - Test `skipSession()` moves to next session type
  
  **Settings:**
  - Test custom durations are applied
  - Test settings persist in localStorage
  - Test default settings load when no saved settings exist

**Testing:**
- Use fake timers (Jest: `jest.useFakeTimers()`) to control time
- Mock DOM elements and localStorage
- Test in isolation from backend

**Granularity:**
- **One test per function behavior**
- **Mock all external dependencies** (DOM, localStorage, fetch)
- **Group related tests** in describe blocks

---

### 10. Add Integration and End-to-End Validation

**Objective:** Test complete user workflows and system integration.

**Tasks:**
- Integration test scenarios:
  
  **Happy Path:**
  1. User starts timer → verify countdown begins
  2. Timer completes work session → verify POST to `/log`
  3. Timer automatically switches to break → verify UI updates
  4. Verify log file contains completed session
  
  **Skip Workflow:**
  1. User starts timer
  2. User clicks skip → verify POST to `/log` with skip action
  3. Verify timer switches to next session
  
  **Settings Workflow:**
  1. User changes work duration to 15 minutes
  2. User saves settings
  3. Timer reflects new duration
  4. Reload page → settings persist
  
  **Error Handling:**
  1. Backend is down
  2. Timer completes → logging fails
  3. Verify user sees error message
  4. Verify timer continues functioning

- Edge cases:
  - Rapid button clicks (debouncing)
  - Invalid input in settings
  - Browser refresh during active session
  - Multiple tabs open simultaneously

**Testing:**
- Manual end-to-end testing
- Optional: Selenium/Playwright for automated E2E tests
- Load testing: Multiple concurrent users logging sessions

**Granularity:**
- **Test complete user journeys** from start to finish
- **Each workflow as separate test case**
- **Use test database/log file** to avoid polluting production data

---

## Testing Strategy Summary

### Backend Testing (pytest)
- **Unit tests:** Individual functions with pytest fixtures for isolation
- **Integration tests:** Full request/response cycle through Flask test client
- **Fixtures:** Use `tmp_path` for temporary log files, preventing test interference
- **Coverage goal:** >90% code coverage

### Frontend Testing (Jest/QUnit)
- **Unit tests:** Pure functions tested in isolation with mocked dependencies
- **Fake timers:** Mock `setInterval`/`setTimeout` for time-based tests
- **DOM mocking:** Use jsdom or similar for DOM manipulation tests
- **Coverage goal:** Core timer logic 100%, UI interactions >80%

### Integration Testing
- **End-to-end workflows:** Complete user journeys from UI to backend
- **Manual testing:** Visual verification of UI/UX
- **Optional automation:** Selenium/Playwright for regression testing

---

## Technical Recommendations

### 1. Logging Format
**Use JSON Lines format** for `pomodoro_log.txt`:
```json
{"session_type": "work", "action": "complete", "started_at": "2025-11-19T10:00:00Z", "ended_at": "2025-11-19T10:25:00Z"}
{"session_type": "short_break", "action": "skip", "started_at": "2025-11-19T10:25:00Z", "ended_at": "2025-11-19T10:27:30Z"}
```

**Rationale:** Easy to parse line-by-line, extensible (can add fields), human-readable.

### 2. Settings Persistence
**Use localStorage** for timer duration settings:
- Store as JSON object: `{workDuration: 25, shortBreak: 5, longBreak: 15}`
- Load on page load with fallback to defaults
- Better UX: settings survive page refreshes

### 3. Test Data Isolation
**Backend:** Use pytest's `tmp_path` fixture to create unique log files per test:
```python
def test_log_session(tmp_path):
    log_file = tmp_path / "test_log.txt"
    # test with isolated log file
```

**Frontend:** Mock localStorage and reset state before each test:
```javascript
beforeEach(() => {
    localStorage.clear();
    // reset timer state
});
```

### 4. Error Handling
- **Backend:** Return appropriate HTTP status codes (400 for validation errors, 500 for server errors)
- **Frontend:** Display user-friendly error messages, gracefully degrade if logging fails
- **Logging failures should not break timer functionality**

### 5. Development Workflow
1. Start with backend (easier to test in isolation)
2. Build frontend HTML structure
3. Implement timer logic (testable without backend)
4. Wire up frontend-backend integration
5. Add styling last (visual, subjective)
6. Write tests alongside implementation (TDD preferred)

---

## Dependencies

### Backend
- Flask (web framework)
- pytest (testing)
- pytest-cov (coverage reporting)

### Frontend
- Vanilla JavaScript (no framework needed)
- Optional: Jest (if using Node.js-based testing)
- Optional: QUnit (for browser-based testing)

### Development Tools
- `uv` (package management within `.venv`)
- Coverage.py (Python code coverage)
- ESLint/Prettier (optional, for code quality)

---

## Success Criteria

- [ ] Flask backend serves static assets and API endpoints
- [ ] POST `/log` validates and persists session data
- [ ] GET `/history` retrieves logged sessions
- [ ] Timer counts down accurately
- [ ] Sessions transition correctly (work → short break → work → long break)
- [ ] Settings can be customized and persist
- [ ] Failed logging doesn't break timer functionality
- [ ] Backend tests achieve >90% coverage
- [ ] Frontend core logic has comprehensive unit tests
- [ ] End-to-end workflows validated (manual or automated)
- [ ] UI matches mockup design
- [ ] Application is responsive and accessible

---

## Future Enhancements (Out of Scope)

- User authentication and per-user session tracking
- Analytics dashboard (sessions completed per day/week)
- Sound notifications when sessions complete
- Browser notifications API integration
- Export session history to CSV/JSON
- Multiple timer presets (different Pomodoro configurations)
- Sync sessions across devices (requires backend database)
