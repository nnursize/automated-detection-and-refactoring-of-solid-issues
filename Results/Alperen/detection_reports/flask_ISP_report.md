# ISP Violation Report: flask

## Summary
- **Total unique issues**: 85
- **High severity**: 1
- **Medium severity**: 37
- **Low severity**: 47
- **Found by multiple scans**: 6/85

## Issues

### ISP-074 [MEDIUM] src/flask/sessions.py — SessionInterface
- **Confidence**: Found in 4 scan(s)
- **Lines**: 72–250
- **Type**: class
- **Description**: The SessionInterface defines many configuration getters and core methods, potentially forcing implementers to provide unused functionality.
- **Reasoning**: The `SessionInterface` defines a comprehensive set of methods for managing sessions, including getters for cookie parameters (name, domain, path, httponly, secure, samesite, partitioned), expiration time, and the core `open_session`/`save_session`. Implementers who only need a simple session storage might be forced to provide implementations for all these cookie-related getters, even if they don't use cookies or have their own storage mechanism. This violates ISP by having a large interface.

### ISP-001 [MEDIUM] src/flask/app.py — Flask.handle_http_exception
- **Confidence**: Found in 3 scan(s)
- **Lines**: 488–503
- **Type**: method
- **Description**: The handle_http_exception method handles both routing exceptions and other HTTP exceptions, violating ISP.
- **Reasoning**: The `handle_http_exception` method is responsible for handling all `HTTPException` subclasses, including routing-specific exceptions like `RequestRedirect` and general HTTP exceptions. This broad responsibility forces clients (or subclasses) to be aware of and potentially handle routing-specific logic when they only intend to deal with general HTTP exceptions. A more segregated approach would separate the handling of routing exceptions from other HTTP exceptions.

### ISP-044 [MEDIUM] src/flask/sansio/scaffold.py — Scaffold.add_url_rule
- **Confidence**: Found in 3 scan(s)
- **Lines**: 328–379
- **Type**: method
- **Description**: The add_url_rule method handles methods, endpoint naming, automatic OPTIONS, defaults, and rule object creation, violating ISP.
- **Reasoning**: The `add_url_rule` method in `Scaffold` (which `Flask` and `Blueprint` inherit from) handles methods, endpoint naming, automatic OPTIONS, defaults, and the creation of the `Rule` object. This broad interface means that clients customizing one aspect might be coupled to others. For instance, a client only interested in endpoint naming must still be aware of method handling and default values.

### ISP-079 [MEDIUM] src/flask/json/provider.py — JSONProvider
- **Confidence**: Found in 3 scan(s)
- **Lines**: 24–97
- **Type**: class
- **Description**: Fat interface mixing JSON serialization with Flask-specific HTTP response logic.
- **Reasoning**: The JSONProvider interface combines two distinct responsibilities: raw JSON serialization/deserialization (dumps/loads) and the construction of Flask-specific HTTP responses (the response method). This forces a provider implementation to depend on the Flask Response class and HTTP-level concerns, even if its primary purpose is simply to interface with a specific JSON library for serialization.

### ISP-083 [MEDIUM] src/flask/ctx.py — AppContext
- **Confidence**: Found in 3 scan(s)
- **Lines**: 260–525
- **Type**: class
- **Description**: AppContext violates ISP by merging request-specific functionality into a general application context.
- **Reasoning**: After merging RequestContext into AppContext (as noted in the class docstring for version 3.2), the class now contains methods and properties such as 'request', 'session', and 'match_request' that are only valid when a request is present. Clients using the context in a non-request environment (such as CLI commands or background tasks) are forced to depend on a 'fat' interface where these members are non-functional and raise RuntimeError if accessed. This violates the principle that clients should not be forced to depend on interfaces they do not use, and that interfaces should be split into smaller, more focused ones.

### ISP-027 [MEDIUM] src/flask/sansio/app.py — App.create_jinja_environment
- **Confidence**: Found in 2 scan(s)
- **Lines**: 336–359
- **Type**: method
- **Description**: The create_jinja_environment method configures Jinja with autoescape and auto_reload based on app debug status, potentially forcing unwanted configurations.
- **Reasoning**: The `create_jinja_environment` method decides whether to enable `autoescape` and `auto_reload` based on the application's debug status and configuration. A subclass that wants to customize the Jinja environment but doesn't want Flask's default autoescape or auto-reload behavior might find it difficult to override these settings without overriding the entire method. This forces clients to depend on the logic for these specific Jinja features.

### ISP-002 [MEDIUM] src/flask/app.py — Flask.handle_user_exception
- **Confidence**: Found in 1 scan(s)
- **Lines**: 505–528
- **Type**: method
- **Description**: The handle_user_exception method handles general exceptions and HTTP exceptions, violating ISP.
- **Reasoning**: The `handle_user_exception` method is designed to handle both general `Exception` types and `HTTPException` types. It first checks if the exception is an `HTTPException` and, if so, forwards it to `handle_http_exception`. This creates a dependency on `handle_http_exception` for a subset of exceptions, rather than having a dedicated handler for user-defined exceptions that are not HTTP exceptions. This can lead to classes needing to be aware of the `handle_http_exception` method even if they only intend to handle general exceptions.

### ISP-003 [MEDIUM] src/flask/app.py — Flask.handle_exception
- **Confidence**: Found in 1 scan(s)
- **Lines**: 530–571
- **Type**: method
- **Description**: The handle_exception method handles unhandled exceptions and propagates them, potentially involving other handlers, violating ISP.
- **Reasoning**: The `handle_exception` method is a catch-all for exceptions that don't have specific handlers. It also includes logic for propagating exceptions based on `PROPAGATE_EXCEPTIONS` and potentially calls `log_exception` and `finalize_request`. This broad scope makes it difficult for subclasses or clients to override specific aspects of exception handling without affecting the entire flow. A more segregated approach would break down these responsibilities into smaller, more focused methods.

### ISP-004 [LOW] src/flask/app.py — Flask.log_exception
- **Confidence**: Found in 1 scan(s)
- **Lines**: 573–578
- **Type**: method
- **Description**: The log_exception method is part of the broader exception handling mechanism, potentially violating ISP by being coupled to it.
- **Reasoning**: While `log_exception` itself is focused, it's called by `handle_exception`. This tight coupling means that any subclass wanting to customize logging might need to be aware of the entire exception handling chain, rather than just logging. A more segregated design might allow logging to be injected or replaced more independently.

### ISP-005 [MEDIUM] src/flask/app.py — Flask.dispatch_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 580–595
- **Type**: method
- **Description**: The dispatch_request method handles routing exceptions, OPTIONS responses, and view function calls, violating ISP.
- **Reasoning**: The `dispatch_request` method is responsible for multiple distinct tasks: handling routing exceptions (`raise_routing_exception`), generating default OPTIONS responses (`make_default_options_response`), and dispatching to the actual view function. This violates ISP because a client might only be interested in customizing the view function dispatch and should not be forced to depend on or be aware of the logic for handling routing exceptions or OPTIONS requests.

### ISP-006 [MEDIUM] src/flask/app.py — Flask.full_dispatch_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 597–619
- **Type**: method
- **Description**: The full_dispatch_request method orchestrates request processing, including preprocessing, dispatching, and exception handling, violating ISP.
- **Reasoning**: The `full_dispatch_request` method acts as a central orchestrator for the entire request lifecycle. It calls `preprocess_request`, `dispatch_request`, `handle_user_exception`, and `finalize_request`. This means any customization of request processing, even if only for preprocessing, requires interacting with or being aware of the broader dispatch, exception, and finalization logic. Separating these concerns would allow for more focused overrides.

### ISP-007 [MEDIUM] src/flask/app.py — Flask.finalize_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 621–637
- **Type**: method
- **Description**: The finalize_request method handles response creation, postprocessing, and signal sending, violating ISP.
- **Reasoning**: The `finalize_request` method is responsible for converting a return value into a response (`make_response`), processing the response (`process_response`), sending signals (`request_finished`), and handling potential errors during finalization. This bundles several distinct responsibilities. A client interested only in modifying the response object might be coupled to the signal-sending mechanism or the error handling during finalization.

### ISP-008 [LOW] src/flask/app.py — Flask.make_default_options_response
- **Confidence**: Found in 1 scan(s)
- **Lines**: 639–644
- **Type**: method
- **Description**: The make_default_options_response method is specific to OPTIONS requests, but its dependency on URL adapter might be considered a minor ISP violation if not used broadly.
- **Reasoning**: This method is specifically for generating an OPTIONS response. While focused, its reliance on `ctx.url_adapter.allowed_methods()` ties it directly to the routing mechanism. If a client only wanted to customize response generation in general and not specifically for OPTIONS or routing, this method's implementation details could be seen as a minor violation of ISP.

### ISP-009 [LOW] src/flask/app.py — Flask.ensure_sync
- **Confidence**: Found in 1 scan(s)
- **Lines**: 646–650
- **Type**: method
- **Description**: The ensure_sync method bridges async and sync, but its direct coupling might be seen as a minor ISP violation.
- **Reasoning**: The `ensure_sync` method is a utility to ensure synchronous execution for WSGI workers. While useful, it tightly couples the synchronous execution path with asynchronous capabilities. A client that exclusively uses synchronous code might still inherit this method, and a client that wants to manage async execution differently might find this method's presence intrusive.

### ISP-010 [LOW] src/flask/app.py — Flask.async_to_sync
- **Confidence**: Found in 1 scan(s)
- **Lines**: 652–671
- **Type**: method
- **Description**: The async_to_sync method is specifically for async to sync conversion, potentially forcing sync-only clients to depend on async logic.
- **Reasoning**: This method is specifically designed for converting asynchronous functions to synchronous ones. While necessary for WSGI compatibility, it introduces a dependency on async concepts and external libraries (like `asgiref`) even for applications that might not use asynchronous features at all. This can be seen as a minor ISP violation if the interface forces knowledge of async implementation details onto synchronous-only clients.

### ISP-011 [MEDIUM] src/flask/app.py — Flask.url_for
- **Confidence**: Found in 1 scan(s)
- **Lines**: 673–823
- **Type**: method
- **Description**: The url_for method handles URL generation with numerous parameters, potentially forcing clients to depend on unused parameters.
- **Reasoning**: The `url_for` method has a large number of parameters, including `_anchor`, `_method`, `_scheme`, `_external`, and variable parts of the URL. While many are optional, the sheer number and variety of options means a client calling `url_for` might be aware of or even need to provide values for parameters they do not intend to use, violating ISP. Smaller, more focused URL generation methods could be beneficial.

### ISP-012 [MEDIUM] src/flask/app.py — Flask.make_response
- **Confidence**: Found in 1 scan(s)
- **Lines**: 825–923
- **Type**: method
- **Description**: The make_response method handles conversion of various return types to Response objects, violating ISP by having a large, multifaceted interface.
- **Reasoning**: The `make_response` method is responsible for converting a wide range of return types (strings, bytes, dicts, lists, generators, tuples, Response objects, WSGI callables) into a `Response` object. This large and varied interface means clients or subclasses that only need to handle a subset of these return types are still exposed to the entire API. A violation occurs because clients creating responses from simple strings are forced to be aware of the complex tuple unpacking and other type coercions.

### ISP-013 [MEDIUM] src/flask/app.py — Flask.preprocess_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 925–947
- **Type**: method
- **Description**: The preprocess_request method handles URL value preprocessors and before_request functions, violating ISP by combining distinct concerns.
- **Reasoning**: The `preprocess_request` method combines two distinct functionalities: executing URL value preprocessors and executing `before_request` functions. A client that only wants to modify URL values or only wants to perform actions before a request would still be exposed to the other functionality. Separating these into two methods would adhere better to ISP.

### ISP-014 [MEDIUM] src/flask/app.py — Flask.process_response
- **Confidence**: Found in 1 scan(s)
- **Lines**: 949–964
- **Type**: method
- **Description**: The process_response method handles after_request functions, session saving, and signal sending, violating ISP.
- **Reasoning**: The `process_response` method encompasses several responsibilities: running `after_request` functions, saving the session, and sending the `request_finished` signal. A client that only needs to modify the response or save the session might be unnecessarily coupled to the signal-sending mechanism. Breaking this down would allow for more granular control and adherence to ISP.

### ISP-015 [MEDIUM] src/flask/app.py — Flask.do_teardown_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 966–984
- **Type**: method
- **Description**: The do_teardown_request method handles teardown_request functions and sends a signal, violating ISP by combining concerns.
- **Reasoning**: The `do_teardown_request` method executes registered `teardown_request` functions and then sends the `request_tearing_down` signal. This couples the execution of teardown logic with signal emission. A client that only wants to customize teardown logic might be unnecessarily aware of the signal mechanism, violating ISP.

### ISP-016 [MEDIUM] src/flask/app.py — Flask.do_teardown_appcontext
- **Confidence**: Found in 1 scan(s)
- **Lines**: 986–1001
- **Type**: method
- **Description**: The do_teardown_appcontext method handles teardown_appcontext functions and sends a signal, violating ISP by combining concerns.
- **Reasoning**: Similar to `do_teardown_request`, `do_teardown_appcontext` executes `teardown_appcontext` functions and then sends the `appcontext_tearing_down` signal. This coupling of teardown logic with signal emission violates ISP. A client needing only to adjust teardown behavior might be forced to interact with or understand the signal system.

### ISP-017 [LOW] src/flask/app.py — Flask.app_context
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1003–1017
- **Type**: method
- **Description**: The app_context method creates an AppContext, which might be seen as a broad interface.
- **Reasoning**: The `app_context` method is responsible for creating and managing the application context. While necessary, the resulting `AppContext` object itself might be considered a large interface if clients only need a small part of its functionality (e.g., just accessing `current_app`). However, this is a fundamental part of Flask's architecture.

### ISP-018 [LOW] src/flask/app.py — Flask.request_context
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1019–1035
- **Type**: method
- **Description**: The request_context method creates a RequestContext, which might be seen as a broad interface.
- **Reasoning**: Similar to `app_context`, `request_context` creates a `RequestContext`. The complexity of `RequestContext` (which includes request, session, URL adapter, etc.) might be more than a client needs if it only requires, for example, the `request` object. This could be seen as a minor ISP violation due to the broadness of the interface.

### ISP-019 [LOW] src/flask/app.py — Flask.test_request_context
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1037–1088
- **Type**: method
- **Description**: The test_request_context method exposes many parameters from EnvironBuilder, potentially violating ISP.
- **Reasoning**: The `test_request_context` method accepts arguments that are directly passed to Werkzeug's `EnvironBuilder`. This exposes a large API surface related to building WSGI environments. Clients that only need to set a path or method might be forced to be aware of other `EnvironBuilder` parameters, which could be considered a minor ISP violation.

### ISP-020 [MEDIUM] src/flask/app.py — Flask.wsgi_app
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1090–1116
- **Type**: method
- **Description**: The wsgi_app method handles context pushing/popping, request dispatching, exception handling, and WSGI response generation, violating ISP.
- **Reasoning**: The `wsgi_app` method is the core WSGI entry point. It handles pushing/popping contexts, calling `full_dispatch_request` (which includes preprocessing, dispatching, exception handling, and finalization), and finally returning the WSGI response. This method combines a significant number of responsibilities, making it difficult for a client (e.g., a WSGI middleware) to interact with only a subset of its functionality without being aware of the entire flow.

### ISP-021 [LOW] src/flask/cli.py — AppGroup.command
- **Confidence**: Found in 1 scan(s)
- **Lines**: 219–230
- **Type**: method
- **Description**: The command method wraps commands with with_appcontext by default, potentially forcing sync-only users to depend on context logic.
- **Reasoning**: The `command` method in `AppGroup` defaults to wrapping commands with `with_appcontext`. While useful for Flask CLI commands, this means even simple commands that don't require an app context might inherit this behavior. A client that only wants to define a command without app context awareness could be seen as depending on functionality they don't use.

### ISP-022 [LOW] src/flask/cli.py — AppGroup.group
- **Confidence**: Found in 1 scan(s)
- **Lines**: 232–237
- **Type**: method
- **Description**: The group method defaults the group class to AppGroup, potentially forcing non-Flask CLI groups to depend on Flask-specific context logic.
- **Reasoning**: The `group` method in `AppGroup` defaults the group class to `AppGroup`. This means that any nested groups created via this method will also inherit the `with_appcontext` behavior from `AppGroup.command` (due to `AppGroup`'s inheritance). This can force clients creating purely non-Flask CLI groups to depend on Flask's context management.

### ISP-023 [MEDIUM] src/flask/cli.py — FlaskGroup.get_command
- **Confidence**: Found in 1 scan(s)
- **Lines**: 345–367
- **Type**: method
- **Description**: The get_command method loads the app and pushes context even for commands that might not need it, violating ISP.
- **Reasoning**: The `get_command` method in `FlaskGroup` first loads the Flask application and then pushes an application context (`ctx.with_resource(app.app_context())`) for all commands retrieved from the app's CLI, regardless of whether the command actually needs an app context. This forces all commands to depend on the application context infrastructure, even if they are simple built-in commands or plugin commands that do not interact with the Flask app.

### ISP-024 [MEDIUM] src/flask/cli.py — FlaskGroup.list_commands
- **Confidence**: Found in 1 scan(s)
- **Lines**: 369–388
- **Type**: method
- **Description**: The list_commands method attempts to load the app and its commands, potentially failing for commands that don't need the app context, violating ISP.
- **Reasoning**: The `list_commands` method in `FlaskGroup` attempts to load the Flask application (`info.load_app()`) to list commands provided by the app's CLI. This means that even if a user is only interested in listing built-in Flask commands (like `run`, `shell`), they might encounter errors if the app itself fails to load, due to dependencies on the app context or other setup logic. This violates ISP by forcing a dependency on app loading for listing all commands.

### ISP-025 [MEDIUM] src/flask/cli.py — FlaskGroup.make_context
- **Confidence**: Found in 1 scan(s)
- **Lines**: 404–418
- **Type**: method
- **Description**: The make_context method initializes ScriptInfo, setting debug flag and loading dotenv, which might be unwanted by clients.
- **Reasoning**: The `make_context` method in `FlaskGroup` automatically initializes `ScriptInfo`, setting the debug flag and handling dotenv loading. This behavior is tied to the `flask` command's internal workings. If a client were to subclass `FlaskGroup` or manually create a context, they might be forced to accept this default behavior, even if they have their own mechanisms for managing debug flags or environment variables, thus violating ISP.

### ISP-026 [LOW] src/flask/cli.py — FlaskGroup.parse_args
- **Confidence**: Found in 1 scan(s)
- **Lines**: 420–431
- **Type**: method
- **Description**: The parse_args method eagerly handles env-file and app options, potentially affecting clients that don't use them.
- **Reasoning**: The `parse_args` method in `FlaskGroup` eagerly handles the `--env-file` and `--app` options. This is done to ensure that `no_args_is_help` can correctly discover commands from `app.cli`. However, this means that any client subclassing `FlaskGroup` or overriding `parse_args` might need to account for this eager parsing, even if they don't intend to use these specific options, which could be a minor ISP violation.

### ISP-028 [LOW] src/flask/sansio/app.py — App.select_jinja_autoescape
- **Confidence**: Found in 1 scan(s)
- **Lines**: 469–475
- **Type**: method
- **Description**: The select_jinja_autoescape method's logic is tied to specific file extensions.
- **Reasoning**: The `select_jinja_autoescape` method determines whether autoescaping should be enabled based on file extensions. While this is a reasonable default, a client that wants to control autoescaping based on different criteria (e.g., template content, or a specific configuration option) might need to override this method, thus depending on the file extension logic.

### ISP-029 [MEDIUM] src/flask/sansio/app.py — App.register_blueprint
- **Confidence**: Found in 1 scan(s)
- **Lines**: 609–645
- **Type**: method
- **Description**: The register_blueprint method handles blueprint registration, URL rules, and nested blueprint registration, violating ISP.
- **Reasoning**: The `register_blueprint` method handles multiple aspects of blueprint integration: adding URL rules, processing deferred setup functions, managing static file rules, and recursively registering nested blueprints. This large interface means that a client wanting to customize only one aspect (e.g., how static rules are added) must override or be aware of the entire method's logic, violating ISP.

### ISP-030 [MEDIUM] src/flask/sansio/app.py — App.add_url_rule
- **Confidence**: Found in 1 scan(s)
- **Lines**: 647–699
- **Type**: method
- **Description**: The add_url_rule method handles methods, endpoint naming, automatic OPTIONS, defaults, and rule object creation, violating ISP.
- **Reasoning**: The `add_url_rule` method is responsible for adding URL rules. It handles method negotiation (including automatic OPTIONS), endpoint naming, default values, and the creation of the `Rule` object itself. This broad scope means a client might need to interact with logic related to methods or defaults even if they only care about endpoint naming or the rule object. Separating these concerns would lead to a more ISP-compliant design.

### ISP-031 [LOW] src/flask/sansio/app.py — App.template_filter
- **Confidence**: Found in 1 scan(s)
- **Lines**: 701–716
- **Type**: method
- **Description**: The template_filter decorator registers filters, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: The `template_filter` decorator, while convenient, mixes the act of registering a filter with the definition of the filter function itself. A client that only wants to register an existing function as a filter might find this pattern overly coupled. The existence of `add_template_filter` mitigates this, but the decorator pattern itself can be seen as a minor ISP violation.

### ISP-032 [LOW] src/flask/sansio/app.py — App.add_template_filter
- **Confidence**: Found in 1 scan(s)
- **Lines**: 718–730
- **Type**: method
- **Description**: The add_template_filter method directly modifies the Jinja environment's filters.
- **Reasoning**: The `add_template_filter` method directly modifies the `jinja_env.filters` dictionary. While focused on adding filters, it implies a dependency on the internal structure of the Jinja environment. A more ISP-compliant approach might abstract this interaction further.

### ISP-033 [LOW] src/flask/sansio/app.py — App.template_test
- **Confidence**: Found in 1 scan(s)
- **Lines**: 732–747
- **Type**: method
- **Description**: The template_test decorator registers tests, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: Similar to `template_filter`, the `template_test` decorator couples the definition of a test function with its registration. While `add_template_test` exists, the decorator pattern itself can be viewed as a minor ISP violation by mixing concerns.

### ISP-034 [LOW] src/flask/sansio/app.py — App.add_template_test
- **Confidence**: Found in 1 scan(s)
- **Lines**: 749–761
- **Type**: method
- **Description**: The add_template_test method directly modifies the Jinja environment's tests.
- **Reasoning**: The `add_template_test` method directly modifies the `jinja_env.tests` dictionary. This implies a dependency on the internal structure of the Jinja environment, which could be a minor ISP violation.

### ISP-035 [LOW] src/flask/sansio/app.py — App.template_global
- **Confidence**: Found in 1 scan(s)
- **Lines**: 763–778
- **Type**: method
- **Description**: The template_global decorator registers globals, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: Similar to `template_filter` and `template_test`, the `template_global` decorator couples the definition of a global function with its registration. The existence of `add_template_global` mitigates this, but the decorator pattern itself might be considered a minor ISP violation.

### ISP-036 [LOW] src/flask/sansio/app.py — App.add_template_global
- **Confidence**: Found in 1 scan(s)
- **Lines**: 780–792
- **Type**: method
- **Description**: The add_template_global method directly modifies the Jinja environment's globals.
- **Reasoning**: The `add_template_global` method directly modifies the `jinja_env.globals` dictionary. This implies a dependency on the internal structure of the Jinja environment, which could be a minor ISP violation.

### ISP-037 [LOW] src/flask/sansio/app.py — App.teardown_appcontext
- **Confidence**: Found in 1 scan(s)
- **Lines**: 794–822
- **Type**: method
- **Description**: The teardown_appcontext decorator registers functions, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: The `teardown_appcontext` decorator couples the definition of a teardown function with its registration. While this is a common pattern, it implies a dependency on the decorator mechanism for registration, which could be a minor ISP violation.

### ISP-038 [LOW] src/flask/sansio/app.py — App.shell_context_processor
- **Confidence**: Found in 1 scan(s)
- **Lines**: 824–833
- **Type**: method
- **Description**: The shell_context_processor decorator registers context processors, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: Similar to other registration decorators, `shell_context_processor` couples the definition of a context processor function with its registration. This implies a dependency on the decorator mechanism for registration, which could be a minor ISP violation.

### ISP-039 [MEDIUM] src/flask/sansio/app.py — App._find_error_handler
- **Confidence**: Found in 1 scan(s)
- **Lines**: 844–862
- **Type**: method
- **Description**: The _find_error_handler method searches through multiple scopes and exception types, potentially forcing clients to be aware of this complex lookup.
- **Reasoning**: The `_find_error_handler` method has a complex lookup logic that iterates through blueprints, error codes, and exception class hierarchies. Clients interacting with error handling might need to understand this entire search mechanism, even if they only want to register a simple handler for a specific exception type at the application level. This violates ISP by exposing a broad and interconnected interface.

### ISP-040 [LOW] src/flask/sansio/app.py — App.trap_http_exception
- **Confidence**: Found in 1 scan(s)
- **Lines**: 864–881
- **Type**: method
- **Description**: The trap_http_exception method's logic depends on multiple configuration options and exception types.
- **Reasoning**: The `trap_http_exception` method's logic depends on `TRAP_HTTP_EXCEPTIONS`, `TRAP_BAD_REQUEST_ERRORS`, `debug`, and the type of exception (`BadRequestKeyError`, `BadRequest`). This intertwining of concerns means that customizing this behavior requires understanding all these dependencies, which could be seen as a minor ISP violation.

### ISP-041 [LOW] src/flask/sansio/app.py — App.redirect
- **Confidence**: Found in 1 scan(s)
- **Lines**: 918–932
- **Type**: method
- **Description**: The redirect method's behavior depends on the application's response_class and the context.
- **Reasoning**: The `redirect` method relies on `current_app.redirect` if an app context is available, otherwise it uses Werkzeug's default. This means clients calling `redirect` are implicitly dependent on the application context being available or the default Werkzeug behavior. While functional, it couples the redirect functionality to the application context's presence.

### ISP-042 [MEDIUM] src/flask/sansio/app.py — App.inject_url_defaults
- **Confidence**: Found in 1 scan(s)
- **Lines**: 934–955
- **Type**: method
- **Description**: The inject_url_defaults method handles blueprint-specific defaults and application-wide defaults, violating ISP by combining concerns.
- **Reasoning**: The `inject_url_defaults` method handles injecting URL defaults. It considers both blueprint-specific defaults (by parsing the endpoint) and application-wide defaults. This combination of logic means that customizing default URL injection might require understanding how blueprint endpoints are parsed, even if the client is only interested in application-wide defaults. Separating these concerns would be more ISP-compliant.

### ISP-043 [MEDIUM] src/flask/sansio/app.py — App.handle_url_build_error
- **Confidence**: Found in 1 scan(s)
- **Lines**: 957–974
- **Type**: method
- **Description**: The handle_url_build_error method iterates through error handlers and handles BuildErrors, violating ISP.
- **Reasoning**: The `handle_url_build_error` method iterates through `url_build_error_handlers` and also handles `BuildError` directly. This means clients overriding this method must be aware of both the handler list mechanism and the specific `BuildError` exception handling. Separating the iteration of handlers from the direct handling of `BuildError` would improve adherence to ISP.

### ISP-045 [LOW] src/flask/sansio/scaffold.py — Scaffold.errorhandler
- **Confidence**: Found in 1 scan(s)
- **Lines**: 446–466
- **Type**: method
- **Description**: The errorhandler decorator registers handlers, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: The `errorhandler` decorator couples the definition of an error handler function with its registration. While `register_error_handler` exists, the decorator pattern itself implies a dependency on the registration mechanism, which could be a minor ISP violation.

### ISP-046 [LOW] src/flask/sansio/scaffold.py — Scaffold.register_error_handler
- **Confidence**: Found in 1 scan(s)
- **Lines**: 468–476
- **Type**: method
- **Description**: The register_error_handler method directly modifies the error_handler_spec.
- **Reasoning**: The `register_error_handler` method directly modifies the `error_handler_spec` dictionary. This implies a dependency on the internal structure of how error handlers are stored, which could be a minor ISP violation.

### ISP-047 [LOW] src/flask/sansio/scaffold.py — Scaffold.before_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 546–561
- **Type**: method
- **Description**: The before_request decorator registers functions, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: The `before_request` decorator couples the definition of a request hook function with its registration. This implies a dependency on the decorator mechanism for registration, which could be a minor ISP violation.

### ISP-048 [LOW] src/flask/sansio/scaffold.py — Scaffold.after_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 563–584
- **Type**: method
- **Description**: The after_request decorator registers functions, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: Similar to `before_request`, the `after_request` decorator couples the definition of a request hook function with its registration. This implies a dependency on the decorator mechanism for registration, which could be a minor ISP violation.

### ISP-049 [LOW] src/flask/sansio/scaffold.py — Scaffold.teardown_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 586–618
- **Type**: method
- **Description**: The teardown_request decorator registers functions, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: Similar to `before_request` and `after_request`, the `teardown_request` decorator couples the definition of a teardown function with its registration. This implies a dependency on the decorator mechanism for registration, which could be a minor ISP violation.

### ISP-050 [LOW] src/flask/sansio/scaffold.py — Scaffold.context_processor
- **Confidence**: Found in 1 scan(s)
- **Lines**: 620–634
- **Type**: method
- **Description**: The context_processor decorator registers context processors, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: The `context_processor` decorator couples the definition of a context processor function with its registration. This implies a dependency on the decorator mechanism for registration, which could be a minor ISP violation.

### ISP-051 [LOW] src/flask/sansio/scaffold.py — Scaffold.url_value_preprocessor
- **Confidence**: Found in 1 scan(s)
- **Lines**: 636–658
- **Type**: method
- **Description**: The url_value_preprocessor decorator registers preprocessors, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: The `url_value_preprocessor` decorator couples the definition of a preprocessor function with its registration. This implies a dependency on the decorator mechanism for registration, which could be a minor ISP violation.

### ISP-052 [LOW] src/flask/sansio/scaffold.py — Scaffold.url_defaults
- **Confidence**: Found in 1 scan(s)
- **Lines**: 660–674
- **Type**: method
- **Description**: The url_defaults decorator registers default functions, but the decorator pattern itself can be seen as a minor ISP violation.
- **Reasoning**: The `url_defaults` decorator couples the definition of a default function with its registration. This implies a dependency on the decorator mechanism for registration, which could be a minor ISP violation.

### ISP-053 [MEDIUM] src/flask/blueprints.py — Blueprint.register_blueprint
- **Confidence**: Found in 1 scan(s)
- **Lines**: 241–252
- **Type**: method
- **Description**: The register_blueprint method handles nested blueprint registration, potentially forcing clients to depend on nested registration logic.
- **Reasoning**: The `register_blueprint` method in `Blueprint` handles the registration of nested blueprints. This means that even if a client is only registering a blueprint directly with an application and not nesting it, the method's implementation might still be coupled to the logic for handling nested registrations and their options (like `url_prefix`, `subdomain`). This violates ISP by exposing functionality that might not be used by all clients.

### ISP-054 [MEDIUM] src/flask/blueprints.py — Blueprint.register
- **Confidence**: Found in 1 scan(s)
- **Lines**: 254–340
- **Type**: method
- **Description**: The register method handles multiple aspects of blueprint registration, including static files, deferred functions, CLI groups, and nested blueprints, violating ISP.
- **Reasoning**: The `register` method in `Blueprint` is highly multifaceted. It handles registering static routes, executing deferred setup functions, integrating CLI commands, and recursively registering nested blueprints. This large interface means that a client wanting to customize only one aspect (e.g., only CLI integration) is still exposed to the entire method's logic, violating ISP by forcing awareness of unrelated functionalities.

### ISP-055 [LOW] src/flask/blueprints.py — Blueprint.app_template_filter
- **Confidence**: Found in 1 scan(s)
- **Lines**: 470–485
- **Type**: method
- **Description**: The app_template_filter decorator registers filters globally, potentially forcing clients to depend on global scope.
- **Reasoning**: The `app_template_filter` decorator registers a filter globally for the application. This means that even if a blueprint is only concerned with its own templates, it inherits the mechanism for global filter registration. The decorator pattern itself, as noted before, can be a minor ISP violation.

### ISP-056 [LOW] src/flask/blueprints.py — Blueprint.add_app_template_filter
- **Confidence**: Found in 1 scan(s)
- **Lines**: 487–500
- **Type**: method
- **Description**: The add_app_template_filter method registers filters globally, potentially forcing clients to depend on global scope.
- **Reasoning**: Similar to `app_template_filter`, `add_app_template_filter` registers filters globally. This implies a dependency on the application's global filter management, which might be more than a blueprint client needs if it's only concerned with its own template filters.

### ISP-057 [LOW] src/flask/blueprints.py — Blueprint.app_template_test
- **Confidence**: Found in 1 scan(s)
- **Lines**: 502–517
- **Type**: method
- **Description**: The app_template_test decorator registers tests globally, potentially forcing clients to depend on global scope.
- **Reasoning**: The `app_template_test` decorator registers tests globally for the application. This forces a dependency on global test registration, even if the blueprint client is only interested in its own template tests. The decorator pattern itself can be a minor ISP violation.

### ISP-058 [LOW] src/flask/blueprints.py — Blueprint.add_app_template_test
- **Confidence**: Found in 1 scan(s)
- **Lines**: 519–532
- **Type**: method
- **Description**: The add_app_template_test method registers tests globally, potentially forcing clients to depend on global scope.
- **Reasoning**: Similar to `app_template_test`, `add_app_template_test` registers tests globally. This implies a dependency on the application's global test management, which might be more than a blueprint client needs if it's only concerned with its own template tests.

### ISP-059 [LOW] src/flask/blueprints.py — Blueprint.app_template_global
- **Confidence**: Found in 1 scan(s)
- **Lines**: 534–549
- **Type**: method
- **Description**: The app_template_global decorator registers globals globally, potentially forcing clients to depend on global scope.
- **Reasoning**: The `app_template_global` decorator registers globals globally for the application. This implies a dependency on global global registration, even if the blueprint client is only interested in its own template globals. The decorator pattern itself can be a minor ISP violation.

### ISP-060 [LOW] src/flask/blueprints.py — Blueprint.add_app_template_global
- **Confidence**: Found in 1 scan(s)
- **Lines**: 551–564
- **Type**: method
- **Description**: The add_app_template_global method registers globals globally, potentially forcing clients to depend on global scope.
- **Reasoning**: Similar to `app_template_global`, `add_app_template_global` registers globals globally. This implies a dependency on the application's global management, which might be more than a blueprint client needs if it's only concerned with its own template globals.

### ISP-061 [LOW] src/flask/blueprints.py — Blueprint.before_app_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 566–577
- **Type**: method
- **Description**: The before_app_request decorator registers hooks globally, potentially forcing clients to depend on global scope.
- **Reasoning**: The `before_app_request` decorator registers request hooks globally. This forces a dependency on global hook registration, even if the blueprint client is only interested in its own request hooks. The decorator pattern itself can be a minor ISP violation.

### ISP-062 [LOW] src/flask/blueprints.py — Blueprint.after_app_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 579–590
- **Type**: method
- **Description**: The after_app_request decorator registers hooks globally, potentially forcing clients to depend on global scope.
- **Reasoning**: Similar to `before_app_request`, the `after_app_request` decorator registers request hooks globally. This forces a dependency on global hook registration, even if the blueprint client is only interested in its own request hooks. The decorator pattern itself can be a minor ISP violation.

### ISP-063 [LOW] src/flask/blueprints.py — Blueprint.teardown_app_request
- **Confidence**: Found in 1 scan(s)
- **Lines**: 592–603
- **Type**: method
- **Description**: The teardown_app_request decorator registers teardown hooks globally, potentially forcing clients to depend on global scope.
- **Reasoning**: Similar to `before_app_request` and `after_app_request`, the `teardown_app_request` decorator registers teardown hooks globally. This forces a dependency on global hook registration, even if the blueprint client is only interested in its own teardown hooks. The decorator pattern itself can be a minor ISP violation.

### ISP-064 [LOW] src/flask/blueprints.py — Blueprint.app_context_processor
- **Confidence**: Found in 1 scan(s)
- **Lines**: 605–616
- **Type**: method
- **Description**: The app_context_processor decorator registers context processors globally, potentially forcing clients to depend on global scope.
- **Reasoning**: The `app_context_processor` decorator registers context processors globally. This forces a dependency on global context processor registration, even if the blueprint client is only interested in its own context processors. The decorator pattern itself can be a minor ISP violation.

### ISP-065 [LOW] src/flask/blueprints.py — Blueprint.app_errorhandler
- **Confidence**: Found in 1 scan(s)
- **Lines**: 618–630
- **Type**: method
- **Description**: The app_errorhandler decorator registers handlers globally, potentially forcing clients to depend on global scope.
- **Reasoning**: The `app_errorhandler` decorator registers error handlers globally. This forces a dependency on global error handler registration, even if the blueprint client is only interested in its own error handlers. The decorator pattern itself can be a minor ISP violation.

### ISP-066 [LOW] src/flask/blueprints.py — Blueprint.app_url_value_preprocessor
- **Confidence**: Found in 1 scan(s)
- **Lines**: 632–643
- **Type**: method
- **Description**: The app_url_value_preprocessor decorator registers preprocessors globally, potentially forcing clients to depend on global scope.
- **Reasoning**: The `app_url_value_preprocessor` decorator registers URL value preprocessors globally. This forces a dependency on global preprocessor registration, even if the blueprint client is only interested in its own preprocessors. The decorator pattern itself can be a minor ISP violation.

### ISP-067 [LOW] src/flask/blueprints.py — Blueprint.app_url_defaults
- **Confidence**: Found in 1 scan(s)
- **Lines**: 645–656
- **Type**: method
- **Description**: The app_url_defaults decorator registers default functions globally, potentially forcing clients to depend on global scope.
- **Reasoning**: The `app_url_defaults` decorator registers URL default functions globally. This forces a dependency on global default registration, even if the blueprint client is only interested in its own URL defaults. The decorator pattern itself can be a minor ISP violation.

### ISP-068 [MEDIUM] src/flask/helpers.py — stream_with_context
- **Confidence**: Found in 1 scan(s)
- **Lines**: 60–109
- **Type**: class
- **Description**: The stream_with_context function couples generator logic with context management, potentially forcing clients to depend on context details.
- **Reasoning**: The `stream_with_context` function wraps a generator to ensure it runs within the request context. While useful, it tightly couples the generator's execution with the context management details (like `_cv_app.get(None)` and `ctx.push()`). Clients who only want to stream data might be forced to understand and depend on Flask's context management mechanisms, violating ISP.

### ISP-069 [MEDIUM] src/flask/helpers.py — send_file
- **Confidence**: Found in 1 scan(s)
- **Lines**: 376–436
- **Type**: class
- **Description**: The send_file function has a large number of parameters and depends on context-specific configurations, violating ISP.
- **Reasoning**: The `send_file` function accepts a wide array of parameters for controlling file sending behavior (mimetype, as_attachment, download_name, conditional, etag, last_modified, max_age). It also implicitly relies on application context for `max_age`, `environ`, `use_x_sendfile`, and `response_class`. This broad interface means clients might be exposed to many options they don't need, and the implicit dependency on context violates ISP.

### ISP-070 [MEDIUM] src/flask/helpers.py — send_from_directory
- **Confidence**: Found in 1 scan(s)
- **Lines**: 438–460
- **Type**: class
- **Description**: The send_from_directory function wraps send_file and inherits its ISP violations, plus adds directory parameter.
- **Reasoning**: The `send_from_directory` function is a wrapper around `send_file`. It inherits all the ISP violations of `send_file` (large parameter list, context dependencies) and adds its own parameter (`directory`). This further broadens the interface and increases the potential for clients to depend on functionality they do not use.

### ISP-071 [LOW] src/flask/helpers.py — get_root_path
- **Confidence**: Found in 1 scan(s)
- **Lines**: 462–517
- **Type**: class
- **Description**: The get_root_path function's logic for finding the path depends on import machinery and file system checks.
- **Reasoning**: The `get_root_path` function attempts to find the root path using various methods involving `sys.modules`, `importlib.util.find_spec`, and file system checks. While necessary for resource loading, this complex logic means clients depending on it are coupled to these underlying mechanisms. A simpler interface for obtaining the root path might be preferred.

### ISP-072 [LOW] src/flask/helpers.py — _CollectErrors
- **Confidence**: Found in 1 scan(s)
- **Lines**: 519–541
- **Type**: class
- **Description**: The _CollectErrors class manages errors and provides a raise_any method, potentially coupling error collection with specific raising mechanisms.
- **Reasoning**: The `_CollectErrors` class acts as a context manager to collect and optionally raise errors. While its purpose is clear, the `raise_any` method tightly couples the error collection mechanism with a specific way of raising errors (either `BaseExceptionGroup` or the first collected exception). Clients using this class might be forced to depend on this particular error-raising strategy.

### ISP-073 [MEDIUM] src/flask/ctx.py — AppContext
- **Confidence**: Found in 1 scan(s)
- **Lines**: 108–373
- **Type**: class
- **Description**: The AppContext class combines application and request context features, potentially forcing clients to depend on unused features.
- **Reasoning**: The `AppContext` class now serves as both an application context and a request context (since version 3.2). It holds references to the app, request, session, URL adapter, and manages teardown functions. Clients that only need the application object might still be exposed to the full complexity of request-specific features (like session or URL adapter), violating ISP. The `has_request` property indicates this combined nature.

### ISP-075 [MEDIUM] src/flask/sessions.py — SecureCookieSessionInterface.open_session
- **Confidence**: Found in 1 scan(s)
- **Lines**: 377–389
- **Type**: method
- **Description**: The open_session method depends on getting the signing serializer, which itself depends on secret_key, creating a chain of dependencies.
- **Reasoning**: The `open_session` method in `SecureCookieSessionInterface` first calls `get_signing_serializer(app)`, which in turn depends on `app.secret_key`. This creates a chain of dependencies related to secret key management and serialization. A client implementing a different session storage mechanism might not need signing or secret keys, but the interface still exposes this part of the logic.

### ISP-076 [MEDIUM] src/flask/sessions.py — SecureCookieSessionInterface.save_session
- **Confidence**: Found in 1 scan(s)
- **Lines**: 391–455
- **Type**: method
- **Description**: The save_session method handles cookie parameters and serialization, depending on multiple configuration values and the session object.
- **Reasoning**: The `save_session` method in `SecureCookieSessionInterface` handles setting various cookie parameters (name, domain, path, secure, partitioned, samesite, httponly), serializing the session data, and then calling `response.set_cookie`. This single method combines cookie configuration retrieval, data serialization, and response modification. Clients wanting to customize only one aspect (e.g., cookie domain) are exposed to the entire logic.

### ISP-077 [MEDIUM] src/flask/json/provider.py — JSONProvider.response
- **Confidence**: Found in 1 scan(s)
- **Lines**: 104–120
- **Type**: method
- **Description**: The response method handles serialization and response object creation, potentially coupling these concerns.
- **Reasoning**: The `response` method in `JSONProvider` handles both serializing data using `dumps` and creating a `Response` object with the correct mimetype. Clients that might want to serialize JSON data but use a different response mechanism (or vice-versa) are coupled to both functionalities within this single method. This violates ISP by combining distinct concerns.

### ISP-078 [LOW] src/flask/json/provider.py — DefaultJSONProvider.dumps
- **Confidence**: Found in 1 scan(s)
- **Lines**: 179–190
- **Type**: method
- **Description**: The dumps method sets defaults for ensure_ascii and sort_keys, potentially forcing clients to depend on these defaults.
- **Reasoning**: The `dumps` method in `DefaultJSONProvider` sets default values for `ensure_ascii` and `sort_keys` using `kwargs.setdefault`. While these are common JSON serialization options, clients that do not wish to use these specific defaults might still have them applied implicitly or need to explicitly override them. This can be seen as a minor ISP violation by forcing awareness of these specific defaults.

### ISP-080 [LOW] src/flask/json/tag.py — PassDict
- **Confidence**: Found in 1 scan(s)
- **Lines**: 135–144
- **Type**: class
- **Description**: Class implements a fat interface (JSONTag) but refuses to implement the to_python method.
- **Reasoning**: PassDict inherits from the JSONTag interface but does not provide an implementation for the to_python method. While the TaggedJSONSerializer is designed to avoid calling this method on tags without a key, the class still inherits a method that is irrelevant to its pass-through purpose, which would raise a NotImplementedError if invoked. This is a Refused Bequest smell indicating that the JSONTag interface is not sufficiently segregated for internal utility tags.

### ISP-081 [MEDIUM] src/flask/sessions.py — SessionInterface
- **Confidence**: Found in 1 scan(s)
- **Lines**: 341–494
- **Type**: class
- **Description**: Fat interface coupling session management to cookie-specific implementation details
- **Reasoning**: SessionInterface violates ISP by forcing all session implementations to depend on cookie-specific logic. It contains numerous concrete methods for cookie configuration such as 'get_cookie_name', 'get_cookie_path', and 'get_cookie_secure' (lines 405-460). An implementation that uses a different mechanism (e.g., a custom HTTP header or a purely server-side token) is forced to inherit these cookie-related methods, indicating the interface is not sufficiently segregated from the default cookie-based implementation.

### ISP-082 [LOW] src/flask/json/tag.py — JSONTag
- **Confidence**: Found in 1 scan(s)
- **Lines**: 74–103
- **Type**: class
- **Description**: Subclasses forced to inherit unused deserialization methods
- **Reasoning**: The JSONTag base class defines a two-way interface for both serialization (to_json) and deserialization (to_python). Subclasses like 'PassDict' (line 118) and 'PassList' (line 142) only participate in the serialization/tagging phase and do not provide an implementation for 'to_python'. This forces these subclasses to depend on a method they do not use, which would raise a NotImplementedError from the base class if invoked, representing a Refused Bequest smell that violates ISP.

### ISP-084 [HIGH] src/flask/sessions.py — NullSession
- **Confidence**: Found in 1 scan(s)
- **Lines**: 83–97
- **Type**: class
- **Description**: NullSession implements a mutable session interface only to disable it by raising errors.
- **Reasoning**: NullSession is forced to implement mutation methods like __setitem__, pop, and clear from the session interface (inherited via SecureCookieSession), but it overrides them to call _fail. This forces the class to adhere to a broad interface it cannot support, which is a direct violation of ISP.

### ISP-085 [MEDIUM] src/flask/sansio/blueprints.py — Blueprint
- **Confidence**: Found in 1 scan(s)
- **Lines**: 119–692
- **Type**: class
- **Description**: The Blueprint class interface is bloated with redundant 'app-level' registration methods.
- **Reasoning**: Blueprint duplicates almost all registration methods from Scaffold with an 'app_' prefix (e.g., app_template_filter, app_template_test, app_template_global, before_app_request, app_errorhandler). This creates a bloated interface where the Blueprint is forced to manage both its own local scope and the global application scope, rather than segregating these roles into distinct interfaces (e.g., a LocalRegistry and a GlobalRegistry).
