# LSP Violation Report: flask

## Summary
- **Total unique issues**: 36
- **High severity**: 2
- **Medium severity**: 22
- **Low severity**: 12
- **Found by multiple scans**: 4/36

## Issues

### LSP-022 [LOW] src/flask/sansio/app.py — App.create_jinja_environment
- **Confidence**: Found in 3 scan(s)
- **Lines**: 246–255
- **Type**: method
- **Description**: Subclass must implement create_jinja_environment to provide a Jinja environment.
- **Reasoning**: The `create_jinja_environment` method is declared in the base `App` class but raises `NotImplementedError`. Any subclass that intends to use templating must override this method. Failure to do so means the subclass is not substitutable for a class that correctly provides a Jinja environment, violating the LSP.

### LSP-024 [MEDIUM] src/flask/sansio/scaffold.py — Scaffold._check_setup_finished
- **Confidence**: Found in 3 scan(s)
- **Lines**: 71–77
- **Type**: method
- **Description**: Subclasses must implement _check_setup_finished to prevent modification after registration.
- **Reasoning**: The `_check_setup_finished` method is intended to raise an error if setup methods are called after the scaffold has been registered. The base `Scaffold` class raises `NotImplementedError`. Any subclass that overrides setup methods (like `add_url_rule`, `before_request`, etc.) must also implement `_check_setup_finished` to enforce the invariant that configuration should not change after registration. Failure to do so means the subclass is not substitutable for a scaffold that enforces this rule, violating the LSP.

### LSP-027 [MEDIUM] src/flask/sansio/blueprints.py — Blueprint.app_template_filter
- **Confidence**: Found in 3 scan(s)
- **Lines**: 450–450
- **Type**: method
- **Description**: Abstract method `app_template_filter` in base class `Blueprint` is not implemented by subclasses.
- **Reasoning**: The `Blueprint` class defines `app_template_filter` as an abstract method (`@abstract`). Any subclass of `Blueprint` must provide a concrete implementation. Failure to do so means that instances of such a subclass cannot be used where a `Blueprint` instance is expected and app-level template filters are applied, violating the LSP.

### LSP-001 [MEDIUM] src/flask/app.py — Flask.handle_http_exception
- **Confidence**: Found in 2 scan(s)
- **Lines**: 510–531
- **Type**: method
- **Description**: Subclass might override handle_http_exception and not handle RoutingException or RequestRedirect correctly.
- **Reasoning**: The `handle_http_exception` method in `Flask` has specific logic to handle `RoutingException` and `RequestRedirect`. If a subclass overrides this method, it must ensure that it correctly handles these cases or reimplements the same logic. Failure to do so could lead to unexpected behavior or errors when routing exceptions occur, violating the LSP because the subclass's behavior is not substitutable for the base class's in all scenarios.

### LSP-002 [MEDIUM] src/flask/app.py — Flask.handle_user_exception
- **Confidence**: Found in 1 scan(s)
- **Lines**: 534–557
- **Type**: method
- **Description**: Subclass might override handle_user_exception and not correctly delegate HTTP exceptions or handle error handlers.
- **Reasoning**: The `handle_user_exception` method checks for `BadRequestKeyError` and `HTTPException`. If a subclass overrides this method, it must ensure it correctly delegates `HTTPException` to `handle_http_exception` and properly finds and calls error handlers. If it fails to do so, or if it changes the behavior of how exceptions are trapped or handled, it would violate the LSP by not being substitutable for the base class's exception handling.

### LSP-003 [MEDIUM] src/flask/app.py — Flask.handle_exception
- **Confidence**: Found in 1 scan(s)
- **Lines**: 560–619
- **Type**: method
- **Description**: Subclass might override handle_exception and alter the propagation of exceptions or the finalization of requests.
- **Reasoning**: The `handle_exception` method determines whether to propagate exceptions based on `PROPAGATE_EXCEPTIONS`, `testing`, and `debug` flags. It also logs exceptions and potentially calls error handlers before finalizing the request. If a subclass overrides this method and changes this logic, especially regarding exception propagation or the finalization of the request (which includes calling `finalize_request`), it could lead to unexpected behavior where exceptions are either not handled as expected or the response is not finalized correctly, violating the LSP.

### LSP-004 [LOW] src/flask/app.py — Flask.log_exception
- **Confidence**: Found in 1 scan(s)
- **Lines**: 622–630
- **Type**: method
- **Description**: Subclass might override log_exception and not log exceptions appropriately.
- **Reasoning**: The `log_exception` method is responsible for logging exceptions. If a subclass overrides this method and changes the logging behavior (e.g., by not logging, logging to an incorrect location, or not including necessary details like the path and method), it would violate the LSP. Callers of this method expect exceptions to be logged in a standard way.

### LSP-005 [MEDIUM] src/flask/app.py — Flask.dispatch_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 633–662
- **Type**: method
- **Description**: Subclass might override dispatch_request and not handle routing exceptions, OPTIONS requests, or view function dispatching correctly.
- **Reasoning**: The `dispatch_request` method handles routing exceptions, provides automatic OPTIONS responses, and dispatches to the appropriate view function. If a subclass overrides this method and alters this behavior, for instance, by not properly handling `routing_exception`, not providing automatic OPTIONS responses when expected, or failing to dispatch to the correct view function, it would violate the LSP. Callers rely on this method to correctly route and execute the request.

### LSP-006 [MEDIUM] src/flask/app.py — Flask.full_dispatch_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 665–695
- **Type**: method
- **Description**: Subclass might override full_dispatch_request and alter the request lifecycle, including preprocessing, dispatching, exception handling, and finalization.
- **Reasoning**: The `full_dispatch_request` method orchestrates the entire request lifecycle: sending `request_started` signal, calling `preprocess_request`, handling user exceptions via `handle_user_exception`, dispatching the request via `dispatch_request`, and finalizing the response via `finalize_request`. Overriding this method without maintaining the same sequence and handling of these steps (especially exception handling and signal sending) would break the contract and violate the LSP.

### LSP-007 [MEDIUM] src/flask/app.py — Flask.finalize_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 698–729
- **Type**: method
- **Description**: Subclass might override finalize_request and not correctly process the response or send the request_finished signal.
- **Reasoning**: The `finalize_request` method is responsible for converting the return value into a response object, processing the response (e.g., calling `process_response`), sending the `request_finished` signal, and handling potential errors during finalization. If a subclass overrides this method and fails to perform these actions correctly, especially the response processing and signal sending, it would violate the LSP because the program expects these final steps to occur.

### LSP-008 [LOW] src/flask/app.py — Flask.make_default_options_response
- **Confidence**: Found in 1 scan(s)
- **Lines**: 732–741
- **Type**: method
- **Description**: Subclass might override make_default_options_response and not provide a valid OPTIONS response.
- **Reasoning**: The `make_default_options_response` method generates the default response for OPTIONS requests. If a subclass overrides this method and returns an invalid response or fails to include the allowed methods, it would violate the LSP. Callers expect a valid OPTIONS response that accurately reflects the allowed methods for the route.

### LSP-009 [LOW] src/flask/app.py — Flask.ensure_sync
- **Confidence**: Found in 1 scan(s)
- **Lines**: 744–751
- **Type**: method
- **Description**: Subclass might override ensure_sync and not correctly convert async functions to sync.
- **Reasoning**: The `ensure_sync` method is intended to ensure that functions are synchronous for WSGI workers. If a subclass overrides this method and fails to correctly convert async functions to sync (or vice-versa if the intent changes), it could lead to runtime errors when async views are called in a WSGI environment, violating the LSP.

### LSP-010 [LOW] src/flask/app.py — Flask.async_to_sync
- **Confidence**: Found in 1 scan(s)
- **Lines**: 754–775
- **Type**: method
- **Description**: Subclass might override async_to_sync and not correctly convert async code to be synchronously callable.
- **Reasoning**: The `async_to_sync` method is responsible for converting async code to be synchronously callable. If a subclass overrides this method and the conversion logic is flawed, it could lead to incorrect execution or errors when async views are called synchronously, violating the LSP. Callers expect a reliable synchronous wrapper for async functions.

### LSP-011 [MEDIUM] src/flask/app.py — Flask.url_for
- **Confidence**: Found in 1 scan(s)
- **Lines**: 896–971
- **Type**: method
- **Description**: Subclass might override url_for and not correctly generate URLs or handle URL build errors.
- **Reasoning**: The `url_for` method generates URLs based on endpoints and values. It handles context-aware URL generation and calls `handle_url_build_error` for `BuildError`. If a subclass overrides `url_for` and changes the URL generation logic, or how it handles build errors (e.g., by not calling `handle_url_build_error` or returning incorrect values), it could lead to broken links or unexpected errors, violating the LSP.

### LSP-012 [MEDIUM] src/flask/app.py — Flask.make_response
- **Confidence**: Found in 1 scan(s)
- **Lines**: 974–1079
- **Type**: method
- **Description**: Subclass might override make_response and not correctly convert view return values into response objects.
- **Reasoning**: The `make_response` method is crucial for converting various return types from view functions into a `Response` object. If a subclass overrides this method and fails to correctly handle all supported return types (strings, bytes, dicts, lists, generators, tuples, Response objects, WSGI callables) or does not properly set status and headers, it would violate the LSP. Consumers rely on this method to consistently produce valid response objects.

### LSP-013 [MEDIUM] src/flask/app.py — Flask.preprocess_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1082–1107
- **Type**: method
- **Description**: Subclass might override preprocess_request and alter the execution of URL value preprocessors or before_request functions.
- **Reasoning**: The `preprocess_request` method executes registered URL value preprocessors and `before_request` functions. If a subclass overrides this method and changes the order of execution, fails to call these functions, or incorrectly handles their return values (stopping further processing), it would violate the LSP. The contract is that these preparatory steps are executed before dispatching.

### LSP-014 [MEDIUM] src/flask/app.py — Flask.process_response
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1110–1137
- **Type**: method
- **Description**: Subclass might override process_response and alter the modification of the response or saving of the session.
- **Reasoning**: The `process_response` method modifies the response object before it's sent, by calling `after_request` functions and saving the session. If a subclass overrides this method and skips these crucial steps, or modifies the response in a way that breaks the contract (e.g., by not saving the session correctly), it would violate the LSP. Callers expect the response to be finalized and the session to be saved.

### LSP-015 [MEDIUM] src/flask/app.py — Flask.do_teardown_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1140–1173
- **Type**: method
- **Description**: Subclass might override do_teardown_request and not execute teardown functions or send the request_tearing_down signal.
- **Reasoning**: The `do_teardown_request` method is responsible for executing all registered `teardown_request` functions and sending the `request_tearing_down` signal. If a subclass overrides this method and fails to execute these functions or send the signal, it violates the LSP because cleanup actions and notifications are expected to occur.

### LSP-016 [MEDIUM] src/flask/app.py — Flask.do_teardown_appcontext
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1176–1204
- **Type**: method
- **Description**: Subclass might override do_teardown_appcontext and not execute teardown functions or send the appcontext_tearing_down signal.
- **Reasoning**: Similar to `do_teardown_request`, `do_teardown_appcontext` executes `teardown_appcontext` functions and sends the `appcontext_tearing_down` signal. Overriding this method and failing to perform these actions would violate the LSP, as resource cleanup and notification are expected.

### LSP-017 [HIGH] src/flask/app.py — Flask.wsgi_app
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1331–1368
- **Type**: method
- **Description**: Subclass might override wsgi_app and not correctly handle the WSGI application lifecycle, including context management and exception handling.
- **Reasoning**: The `wsgi_app` method is the core WSGI application interface. It manages the application and request contexts, calls `full_dispatch_request`, handles exceptions via `handle_exception`, and returns the WSGI iterable response. Overriding this method incorrectly, especially regarding context pushing/popping, exception handling, or the final WSGI response, would fundamentally break the WSGI contract and violate the LSP. Any deviation from the expected WSGI application behavior would be a severe LSP violation.

### LSP-018 [MEDIUM] src/flask/cli.py — FlaskGroup.get_command
- **Confidence**: Found in 1 scan(s)
- **Lines**: 376–398
- **Type**: method
- **Description**: Subclass might override get_command and not correctly load the app or retrieve commands from it.
- **Reasoning**: The `get_command` method in `FlaskGroup` is responsible for retrieving commands, including those provided by the Flask application itself. If a subclass overrides this method and fails to correctly load the application (e.g., by mishandling `NoAppException`) or fails to retrieve commands from the application's CLI group, it would violate the LSP. Callers expect commands defined within the Flask app's CLI to be discoverable through this method.

### LSP-019 [MEDIUM] src/flask/cli.py — FlaskGroup.list_commands
- **Confidence**: Found in 1 scan(s)
- **Lines**: 401–426
- **Type**: method
- **Description**: Subclass might override list_commands and not correctly list all available commands, including those from the app.
- **Reasoning**: The `list_commands` method in `FlaskGroup` aggregates commands from built-in, plugins, and the Flask application itself. If a subclass overrides this method and fails to correctly list all these commands (e.g., by not handling `NoAppException` or other loading errors gracefully), it violates the LSP. Users expect a comprehensive list of all available commands.

### LSP-020 [MEDIUM] src/flask/cli.py — FlaskGroup.make_context
- **Confidence**: Found in 1 scan(s)
- **Lines**: 445–468
- **Type**: method
- **Description**: Subclass might override make_context and not properly initialize ScriptInfo or set environment variables.
- **Reasoning**: The `make_context` method in `FlaskGroup` is responsible for creating the Click context, including initializing `ScriptInfo` and setting environment variables like `FLASK_RUN_FROM_CLI`. If a subclass overrides this method and fails to perform these initializations correctly, it could lead to issues with app loading or command execution, violating the LSP.

### LSP-021 [LOW] src/flask/cli.py — FlaskGroup.parse_args
- **Confidence**: Found in 1 scan(s)
- **Lines**: 471–483
- **Type**: method
- **Description**: Subclass might override parse_args and not handle eager options like --env-file and --app correctly.
- **Reasoning**: The `parse_args` method in `FlaskGroup` has special handling for eager options like `--env-file` and `--app` to ensure they are processed early. If a subclass overrides this method and bypasses or incorrectly handles this eager processing, it could lead to incorrect configuration or failure to load the app, violating the LSP.

### LSP-023 [MEDIUM] src/flask/sansio/app.py — App.add_url_rule
- **Confidence**: Found in 1 scan(s)
- **Lines**: 459–497
- **Type**: method
- **Description**: Subclass must implement add_url_rule to register URL rules.
- **Reasoning**: The `add_url_rule` method is fundamental for registering routes. The base `App` class raises `NotImplementedError`. Any subclass that needs to handle routing must implement this method. If it's not implemented, the subclass cannot be used where a routing mechanism is expected, violating the LSP.

### LSP-025 [HIGH] src/flask/views.py — View.dispatch_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 67–72
- **Type**: method
- **Description**: Subclasses must implement dispatch_request to define view logic.
- **Reasoning**: The `dispatch_request` method is the core of a class-based view, defining its behavior. The base `View` class raises `NotImplementedError`. Any subclass that intends to be used as a view must override this method. Failure to do so means the subclass cannot fulfill the contract of providing request handling logic, making it non-substitutable for a functional view, thus violating the LSP.

### LSP-026 [MEDIUM] src/flask/views.py — MethodView.dispatch_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 160–169
- **Type**: method
- **Description**: Subclass might override dispatch_request and not correctly map HTTP methods to instance methods.
- **Reasoning**: The `MethodView.dispatch_request` method maps HTTP methods (GET, POST, etc.) to corresponding instance methods (e.g., `get`, `post`). If a subclass overrides `dispatch_request` and fails to correctly implement this mapping, or if it doesn't handle the `HEAD` request fallback to `GET` properly, it would violate the LSP. Callers expect that standard HTTP methods will be routed to the appropriate handler methods.

### LSP-028 [MEDIUM] src/flask/ctx.py — _AppCtxGlobals.__enter__
- **Confidence**: Found in 1 scan(s)
- **Lines**: 662–662
- **Type**: method
- **Description**: Abstract method `__enter__` in base class `_CollectErrors` is not implemented by subclasses.
- **Reasoning**: The `_CollectErrors` class has an abstract method `__enter__`. The `_AppCtxGlobals` class inherits from `_CollectErrors` but does not provide an implementation for `__enter__`. This means that `_AppCtxGlobals` instances cannot be used in a `with` statement as intended by the `_CollectErrors` base class, violating the LSP.

### LSP-029 [LOW] src/flask/app.py — Flask.__init__
- **Confidence**: Found in 1 scan(s)
- **Lines**: 310–359
- **Type**: method
- **Description**: The Flask.__init__ method has a large number of parameters, which can make it difficult to substitute.
- **Reasoning**: The __init__ method for the Flask class has many parameters. While not a direct violation of LSP in terms of behavior, a very large number of parameters can indicate a violation of the Interface Segregation Principle or that the class is trying to do too much. This can lead to subclasses needing to provide values for many parameters they might not directly use or understand, making substitution less straightforward. It suggests a potential for refactoring into smaller initialization steps or using dependency injection.

### LSP-030 [LOW] src/flask/sansio/app.py — App.__init__
- **Confidence**: Found in 1 scan(s)
- **Lines**: 279–409
- **Type**: method
- **Description**: The App.__init__ method has a large number of parameters, which can make it difficult to substitute.
- **Reasoning**: Similar to the Flask class's __init__, the App class's __init__ method also has a significant number of parameters. This can make it cumbersome for subclasses to instantiate correctly if they do not need to configure all these options, potentially leading to issues where default values are used that may not be appropriate in all subclass contexts.

### LSP-031 [LOW] src/flask/sansio/scaffold.py — Scaffold.__init__
- **Confidence**: Found in 1 scan(s)
- **Lines**: 75–216
- **Type**: method
- **Description**: The Scaffold.__init__ method has a large number of parameters, potentially impacting substitutability.
- **Reasoning**: The Scaffold class's __init__ method also has a considerable number of parameters. This broad initialization signature can make it harder for subclasses to adhere to the base class contract if they don't need to configure all these aspects, potentially forcing them to accept or ignore parameters they don't fully understand, which is contrary to LSP's goal of seamless substitution.

### LSP-032 [LOW] src/flask/ctx.py — AppContext.__init__
- **Confidence**: Found in 1 scan(s)
- **Lines**: 300–339
- **Type**: method
- **Description**: The AppContext.__init__ method has a large number of parameters, which can make it difficult to substitute.
- **Reasoning**: The AppContext.__init__ method includes parameters for 'app', 'request', and 'session'. While these are core components, a subclass might not always need or want to override the default behavior for all of these. If a subclass were to change the expected types or behavior of these parameters without a clear contract, it could violate LSP. The `from_environ` class method also contributes to the complexity of initialization.

### LSP-033 [MEDIUM] src/flask/sessions.py — SessionInterface.__init__
- **Confidence**: Found in 1 scan(s)
- **Lines**: 100–270
- **Type**: method
- **Description**: SessionInterface defines numerous methods for cookie properties that subclasses might not need or fully implement.
- **Reasoning**: The `SessionInterface` defines a wide array of methods related to cookie properties (`get_cookie_name`, `get_cookie_domain`, `get_cookie_path`, etc.). A subclass implementing this interface might not need to override all of these, or could implement them in a way that doesn't strictly adhere to the implicit contract of the base interface. For example, a simple session implementation might not care about `get_cookie_partitioned`. If a client expects all these methods to be fully functional and customizable in a specific way, and a subclass provides a simplified or different behavior for some, it could lead to substitution issues.

### LSP-034 [MEDIUM] src/flask/sessions.py — SecureCookieSessionInterface.open_session
- **Confidence**: Found in 1 scan(s)
- **Lines**: 323–336
- **Type**: method
- **Description**: SecureCookieSessionInterface.open_session returns a specific type (SecureCookieSession) but the base interface allows a more general type (SessionMixin).
- **Reasoning**: The `SessionInterface.open_session` method is declared to return `SessionMixin | None`. However, `SecureCookieSessionInterface.open_session` returns `SecureCookieSession | None`. While `SecureCookieSession` *is* a `SessionMixin`, this specialization might be unexpected if a client was relying on the broader `SessionMixin` contract and a subclass introduced behavior specific to `SecureCookieSession` that breaks the `SessionMixin` contract. This is a form of covariant return type, which is generally safe, but the LSP concern arises if the `SecureCookieSession` itself has methods or behaviors that violate the `SessionMixin` contract (which is unlikely here as `SecureCookieSession` inherits from `SessionMixin`). The primary concern is the potential for a client to be surprised by the concrete type if it wasn't expecting `SecureCookieSession` specifically.

### LSP-035 [LOW] src/flask/testing.py — FlaskClient.open
- **Confidence**: Found in 1 scan(s)
- **Lines**: 204–248
- **Type**: method
- **Description**: FlaskClient.open has a complex signature with many optional parameters, making substitution difficult.
- **Reasoning**: The `FlaskClient.open` method has a very extensive signature with numerous optional arguments and keyword arguments. This makes it challenging for any potential subclass to correctly override or extend this method while ensuring it remains substitutable for the base `FlaskClient`. Clients using this method might rely on specific default behaviors or argument combinations that a subclass might inadvertently alter.

### LSP-036 [LOW] src/flask/wrappers.py — Request.max_content_length
- **Confidence**: Found in 1 scan(s)
- **Lines**: 60–143
- **Type**: class
- **Description**: The Request class has setters for max_content_length, max_form_memory_size, and max_form_parts, which could be misused by subclasses.
- **Reasoning**: The `Request` class provides setters for `max_content_length`, `max_form_memory_size`, and `max_form_parts`. If a subclass were to override these setters in a way that changed the expected behavior (e.g., by ignoring the new value, raising unexpected exceptions, or enforcing different constraints), it could violate the LSP. Clients relying on the ability to dynamically set these limits might find their expectations broken by a subclass implementation.
