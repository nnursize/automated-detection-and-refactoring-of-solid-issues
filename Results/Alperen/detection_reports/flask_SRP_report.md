# SRP Violation Report: flask

## Summary
- **Total unique issues**: 64
- **High severity**: 9
- **Medium severity**: 44
- **Low severity**: 11
- **Found by multiple scans**: 22/64

## Issues

### SRP-001 [MEDIUM] src/flask/app.py — Flask.send_static_file
- **Confidence**: Found in 11 scan(s)
- **Lines**: 306–316
- **Type**: method
- **Description**: The Flask application directly implements static file serving logic.
- **Reasoning**: The primary responsibility of the Flask application is to manage the web application's lifecycle, routing, and configuration. Directly implementing static file serving (I/O and HTTP serving logic) is a separate concern that could be delegated to a dedicated static file handler or utility.

### SRP-040 [HIGH] src/flask/sansio/blueprints.py — Blueprint.register
- **Confidence**: Found in 7 scan(s)
- **Lines**: 160–230
- **Type**: method
- **Description**: The 'register' method is responsible for both defining the blueprint's components and orchestrating their integration into the main 'App' object, including merging various types of functions and static files.
- **Reasoning**: This method goes beyond simply registering a blueprint; it acts as a complex 'registrar' that merges the blueprint's URL rules, error handlers, request hooks, template context processors, URL value preprocessors, URL defaults, and CLI commands into the main `App`. This orchestration of integration logic is a distinct responsibility from merely defining the blueprint's own components, leading to a God Class smell and tight coupling (Inappropriate Intimacy) with the `App`'s internal structure.

### SRP-025 [MEDIUM] src/flask/sansio/app.py — App.auto_find_instance_path
- **Confidence**: Found in 6 scan(s)
- **Lines**: 401–408
- **Type**: method
- **Description**: Automatically locates the application's instance path, mixing file system path resolution with core app logic.
- **Reasoning**: This method deals with file system path discovery logic, which is a concern separate from the core responsibilities of a web application (like request processing or routing). This logic could be externalized to a path utility helper.

### SRP-004 [MEDIUM] src/flask/app.py — Flask.run
- **Confidence**: Found in 5 scan(s)
- **Lines**: 409–486
- **Type**: method
- **Description**: The Flask application directly implements the logic for running a development server.
- **Reasoning**: Starting and managing a development server is an operational concern, distinct from the application's core responsibilities of routing, request handling, and configuration. This method mixes application definition with server management, which could be delegated to a separate server runner utility.

### SRP-030 [LOW] src/flask/sansio/scaffold.py — Scaffold.static_folder
- **Confidence**: Found in 5 scan(s)
- **Lines**: 169–175
- **Type**: class
- **Description**: Property for resolving the absolute path of the static folder, mixing path resolution with component registration.
- **Reasoning**: While `Scaffold` needs to know about a static folder path, the logic for resolving it (joining `root_path`) is a path manipulation concern. This could be handled by a dedicated path utility rather than being a property of a class primarily focused on registering application components.

### SRP-014 [MEDIUM] src/flask/blueprints.py — Blueprint.get_send_file_max_age
- **Confidence**: Found in 4 scan(s)
- **Lines**: 105–120
- **Type**: method
- **Description**: The 'get_send_file_max_age' method handles specific logic for determining cache control for static files within a blueprint.
- **Reasoning**: The primary responsibility of a Blueprint is to modularize application components and their registration. This method, however, implements specific logic for static file caching. This is a duplication of concerns already present in the `Flask` class and represents a distinct 'static file serving' responsibility. Changes to static file caching would affect this method, independent of the blueprint's core registration logic.

### SRP-036 [LOW] src/flask/json/provider.py — JSONProvider.response
- **Confidence**: Found in 4 scan(s)
- **Lines**: 98–105
- **Type**: method
- **Description**: Combines JSON serialization with HTTP response object creation.
- **Reasoning**: This method takes serialized JSON data and wraps it into an HTTP response object with the appropriate mimetype. While convenient for JSON APIs, it technically mixes the responsibility of 'data serialization' with 'HTTP response construction'. This is a common pattern in web frameworks for convenience, but it's a slight blend of concerns.

### SRP-005 [MEDIUM] src/flask/app.py — Flask.test_client
- **Confidence**: Found in 3 scan(s)
- **Lines**: 488–536
- **Type**: method
- **Description**: The Flask application provides methods for creating a test client.
- **Reasoning**: Testing utilities are a separate concern from the core application's runtime responsibilities. While convenient, the application object should ideally focus on its primary role, and testing client creation could be handled by a dedicated testing factory or module.

### SRP-041 [MEDIUM] src/flask/sansio/blueprints.py — Blueprint.app_template_filter
- **Confidence**: Found in 3 scan(s)
- **Lines**: 278–298
- **Type**: method
- **Description**: The 'Blueprint' class provides methods like 'app_template_filter' to register global application-wide hooks, blurring its responsibility for modular components with global application configuration.
- **Reasoning**: A blueprint's primary responsibility should be to define and manage its own modular components. However, methods like `app_template_filter` (and similar `app_*` methods) allow a blueprint to register *global* application hooks. This means the blueprint has a reason to change if the global application's templating behavior changes, which is outside its core responsibility of defining a modular section of the app. This is an Inappropriate Intimacy smell.

### SRP-043 [HIGH] src/flask/ctx.py — AppContext
- **Confidence**: Found in 3 scan(s)
- **Lines**: 98–280
- **Type**: class
- **Description**: The 'AppContext' class manages the entire lifecycle of application and request contexts, including state, session initialization, routing, and teardown orchestration.
- **Reasoning**: The `AppContext` class is responsible for managing the state of the application and request contexts, initializing the session (`_get_session`), performing URL routing (`match_request`), and orchestrating the execution of multiple teardown functions (`pop`). These are distinct responsibilities that contribute to a God Class smell. Changes to session management, routing, or teardown logic would all require modifications to this class.

### SRP-044 [HIGH] src/flask/sessions.py — SessionInterface
- **Confidence**: Found in 3 scan(s)
- **Lines**: 78–166
- **Type**: class
- **Description**: The 'SessionInterface' class defines the core contract for session storage and also provides a comprehensive set of methods for configuring all aspects of the session cookie.
- **Reasoning**: This class has two primary reasons to change: if the abstract contract for session storage (opening/saving sessions) needs to evolve, or if any aspect of session cookie configuration (name, domain, path, security flags, expiration logic, when to set the cookie) needs to change. These are distinct responsibilities, violating SRP. The cookie configuration could be extracted into a dedicated `SessionCookieConfigurator`.

### SRP-046 [HIGH] src/flask/config.py — Config
- **Confidence**: Found in 3 scan(s)
- **Lines**: 35–241
- **Type**: class
- **Description**: The 'Config' class acts as a dictionary for configuration storage but also implements numerous strategies for loading configuration from environment variables, Python files, generic files, and objects.
- **Reasoning**: The `Config` class has multiple reasons to change. It's a data structure for storing configuration, but it also knows how to load itself from various external sources (environment variables, Python files, generic files, Python objects). Each loading strategy (e.g., `from_envvar`, `from_pyfile`, `from_object`, `from_file`, `from_prefixed_env`) represents a distinct responsibility. Changes to any of these loading mechanisms would require modifying this class, violating SRP and exhibiting a God Class smell.

### SRP-052 [MEDIUM] src/flask/wrappers.py — Request
- **Confidence**: Found in 3 scan(s)
- **Lines**: 20–150
- **Type**: class
- **Description**: The 'Request' class extends Werkzeug's request object but also directly accesses application-level configuration for request limits and includes debug-specific behavior for form data handling.
- **Reasoning**: This class has multiple reasons to change. It provides request-specific data and functionality, but also fetches and interprets application-wide configuration settings for request limits (`max_content_length`, `max_form_memory_size`, `max_form_parts`) from `current_app.config`. Furthermore, its `_load_form_data` method includes debug-specific logic to patch `request.files` for better error reporting. These are distinct responsibilities: core request data, application configuration access, and debug-specific behavior.

### SRP-061 [MEDIUM] src/flask/cli.py — FlaskGroup.get_command
- **Confidence**: Found in 3 scan(s)
- **Lines**: 590–614
- **Type**: method
- **Description**: The 'get_command' method combines responsibilities for loading plugin commands, loading the Flask application, and pushing an application context, in addition to its primary role of retrieving a CLI command.
- **Reasoning**: This method is responsible for multiple distinct operations: first, it ensures plugin commands are loaded; then, it attempts to load the Flask application (which involves complex logic delegated to 'ScriptInfo'); and finally, it pushes an application context. Each of these is a separate 'reason to change'. If the plugin loading mechanism changes, or the app loading strategy changes, or the context management for CLI changes, this method would need modification. This violates SRP by coupling command retrieval with application and context lifecycle management.

### SRP-002 [MEDIUM] src/flask/app.py — Flask.open_resource
- **Confidence**: Found in 2 scan(s)
- **Lines**: 318–337
- **Type**: method
- **Description**: The Flask application directly handles opening resource files from the filesystem.
- **Reasoning**: File system I/O for reading arbitrary resources is a distinct responsibility from the core application logic. This could be delegated to a resource manager utility.

### SRP-003 [MEDIUM] src/flask/app.py — Flask.open_instance_resource
- **Confidence**: Found in 2 scan(s)
- **Lines**: 339–349
- **Type**: method
- **Description**: The Flask application directly handles opening instance resource files from the filesystem.
- **Reasoning**: Similar to 'open_resource', file system I/O for reading/writing instance resources is a distinct responsibility from the core application logic. This could be delegated to a resource manager utility.

### SRP-007 [MEDIUM] src/flask/cli.py — ScriptInfo.load_app
- **Confidence**: Found in 2 scan(s)
- **Lines**: 210–248
- **Type**: method
- **Description**: The method mixes application loading/discovery with application configuration.
- **Reasoning**: This method is responsible for locating and instantiating the Flask application, but it also applies configuration by setting the `app.debug` flag. The responsibility of loading/providing the app should be separate from configuring it based on CLI flags or environment variables.

### SRP-008 [HIGH] src/flask/cli.py — FlaskGroup
- **Confidence**: Found in 2 scan(s)
- **Lines**: 318–435
- **Type**: class
- **Description**: The FlaskGroup class acts as a 'God object' for Flask CLI, handling multiple unrelated responsibilities.
- **Reasoning**: This class is responsible for defining Flask-specific CLI options, adding default Flask commands, loading plugin commands, loading the Flask application itself (via ScriptInfo), setting up the application context for commands, and handling environment variable loading. This broad set of responsibilities makes it a central orchestrator for the Flask CLI, violating SRP by mixing command definition, environment setup, and application lifecycle management.

### SRP-051 [MEDIUM] src/flask/templating.py — DispatchingJinjaLoader
- **Confidence**: Found in 2 scan(s)
- **Lines**: 49–106
- **Type**: class
- **Description**: The 'DispatchingJinjaLoader' class is responsible for loading templates from various sources (app, blueprints) and for integrating with debug-specific template loading explanation logic.
- **Reasoning**: This class combines the core responsibility of locating and loading templates from different parts of the application (app and blueprints) with the distinct responsibility of providing detailed debugging information about template loading attempts (`_get_source_explained` calls `explain_template_loading_attempts`). Changes to template loading mechanisms or to debugging output would both require changes to this class, violating SRP.

### SRP-059 [LOW] src/flask/ctx.py — AppContext.match_request
- **Confidence**: Found in 2 scan(s)
- **Lines**: 409–415
- **Type**: method
- **Description**: The 'match_request' method performs URL routing, which is a distinct responsibility from managing the application context's lifecycle.
- **Reasoning**: While URL routing is an essential part of request processing, the specific logic of matching a request to a URL rule (delegating to 'url_adapter.match') is a routing concern. Placing this directly within the 'AppContext' class means that changes to the routing mechanism would impact the context management class, violating SRP. The context should manage its state and lifecycle, not perform routing itself.

### SRP-062 [MEDIUM] src/flask/cli.py — ScriptInfo
- **Confidence**: Found in 2 scan(s)
- **Lines**: 293–372
- **Type**: class
- **Description**: The ScriptInfo class is responsible for both finding/loading a Flask application and applying configuration during the loading process.
- **Reasoning**: The `load_app` method combines several responsibilities: locating the application (via import path, create_app callable, or default filenames), instantiating it, and then applying configuration (setting the debug flag). Changes to how applications are located should not necessarily impact how they are configured after loading, and vice-versa. This method also indirectly references environment loading via `load_dotenv_defaults`.

### SRP-063 [LOW] src/flask/cli.py — CertParamType
- **Confidence**: Found in 2 scan(s)
- **Lines**: 780–825
- **Type**: class
- **Description**: The CertParamType class handles multiple distinct conversion strategies for certificate options within a single 'convert' method.
- **Reasoning**: The `convert` method is responsible for three different types of conversions: file path validation, recognizing the 'adhoc' string (with associated dependency checks for `cryptography`), and importing an `ssl.SSLContext` object (with associated dependency checks for `ssl`). Each of these conversion strategies and their specific validation/dependency logic represents a distinct reason for the method to change. A more granular design could separate these concerns into individual type converters or a strategy pattern.

### SRP-006 [MEDIUM] src/flask/app.py — Flask.test_cli_runner
- **Confidence**: Found in 1 scan(s)
- **Lines**: 538–548
- **Type**: method
- **Description**: The Flask application provides methods for creating a CLI runner for testing.
- **Reasoning**: Similar to 'test_client', CLI testing utilities are a separate concern from the core application's runtime responsibilities.

### SRP-009 [MEDIUM] src/flask/cli.py — load_dotenv
- **Confidence**: Found in 1 scan(s)
- **Lines**: 438–487
- **Type**: class
- **Description**: The function performs file I/O and environment variable manipulation, which is distinct from core CLI command definition.
- **Reasoning**: Loading environment variables from files involves file system I/O and direct manipulation of `os.environ`. While essential for CLI setup, this is a utility function that could reside in a dedicated configuration or environment helper module, rather than being embedded within the CLI module.

### SRP-010 [MEDIUM] src/flask/cli.py — run_command
- **Confidence**: Found in 1 scan(s)
- **Lines**: 530–586
- **Type**: class
- **Description**: The CLI command directly implements the logic for starting the Werkzeug development server.
- **Reasoning**: This function mixes the definition of a CLI command with the detailed runtime logic for starting a web server. The server startup implementation could be encapsulated in a separate `ServerRunner` class or module, which the `run_command` would then invoke.

### SRP-011 [MEDIUM] src/flask/app.py — Flask.send_static_file
- **Confidence**: Found in 1 scan(s)
- **Lines**: 348–366
- **Type**: method
- **Description**: The 'send_static_file' method is responsible for serving static files from the filesystem.
- **Reasoning**: This method directly implements the logic for serving static files, including path validation and delegation to `send_from_directory`. This is a specific file I/O and content serving responsibility. If the static file serving mechanism needs to change (e.g., integrating with a CDN, different security checks, or a different storage backend), this method would require modification, which is a reason to change separate from the application's core request processing or routing logic.

### SRP-012 [MEDIUM] src/flask/app.py — Flask.open_resource
- **Confidence**: Found in 1 scan(s)
- **Lines**: 368–390
- **Type**: method
- **Description**: The 'open_resource' method handles file system I/O for reading resources relative to the application's root path.
- **Reasoning**: This method is directly concerned with filesystem operations (opening files). While an application needs to access resources, the specific mechanism of *how* those resources are loaded (e.g., from the local filesystem) is a distinct responsibility. If the resource loading strategy changes (e.g., loading from a different storage system or a database), this method would need to change, independent of the core application logic.

### SRP-013 [MEDIUM] src/flask/app.py — Flask.open_instance_resource
- **Confidence**: Found in 1 scan(s)
- **Lines**: 392–403
- **Type**: method
- **Description**: The 'open_instance_resource' method handles file system I/O for reading/writing resources relative to the application's instance path.
- **Reasoning**: Similar to `open_resource`, this method is directly concerned with filesystem operations for instance-specific files. This is a specific file I/O responsibility that is separate from the application's core concerns. Changes to the instance resource storage mechanism would require changes here, independent of the application's core logic.

### SRP-015 [MEDIUM] src/flask/blueprints.py — Blueprint.send_static_file
- **Confidence**: Found in 1 scan(s)
- **Lines**: 122–140
- **Type**: method
- **Description**: The 'send_static_file' method is responsible for serving static files from a blueprint's static folder.
- **Reasoning**: Similar to `Flask.send_static_file`, this method handles the specific task of serving static files for a blueprint. This is a distinct 'static file serving' responsibility, separate from the blueprint's role in organizing application components. Duplicating this logic across `Flask` and `Blueprint` indicates a lack of a centralized, single responsibility for static file serving.

### SRP-016 [MEDIUM] src/flask/blueprints.py — Blueprint.open_resource
- **Confidence**: Found in 1 scan(s)
- **Lines**: 142–164
- **Type**: method
- **Description**: The 'open_resource' method handles file system I/O for reading resources relative to the blueprint's root path.
- **Reasoning**: Similar to `Flask.open_resource`, this method is directly concerned with filesystem operations (opening files) for blueprint-specific resources. This is a distinct file I/O responsibility, separate from the blueprint's core role in organizing application components. Changes to resource loading mechanisms would affect this method, independent of the blueprint's registration logic.

### SRP-017 [MEDIUM] src/flask/app.py — Flask.get_send_file_max_age
- **Confidence**: Found in 1 scan(s)
- **Lines**: 218–234
- **Type**: method
- **Description**: Determines the max-age cache value for static files, a specific static file serving concern.
- **Reasoning**: This method's responsibility is related to static file caching logic, which is distinct from core application setup or request dispatching. It could be part of a dedicated static file serving utility or configuration.

### SRP-018 [MEDIUM] src/flask/app.py — Flask.send_static_file
- **Confidence**: Found in 1 scan(s)
- **Lines**: 236–249
- **Type**: method
- **Description**: Serves static files from the configured folder, mixing I/O and HTTP response generation with core app logic.
- **Reasoning**: Serving static files (reading from disk, setting HTTP headers) is a specialized I/O and HTTP response concern that is separate from the application's core logic or request handling flow. This responsibility could be delegated to a dedicated static asset manager.

### SRP-019 [MEDIUM] src/flask/app.py — Flask.open_resource
- **Confidence**: Found in 1 scan(s)
- **Lines**: 251–270
- **Type**: method
- **Description**: Handles opening resource files relative to the application's root path, mixing file I/O with core app logic.
- **Reasoning**: This method is concerned with file system access and path resolution (I/O), which is a separate responsibility from managing web requests or application configuration. It could be refactored into a dedicated resource management utility.

### SRP-020 [MEDIUM] src/flask/app.py — Flask.open_instance_resource
- **Confidence**: Found in 1 scan(s)
- **Lines**: 272–284
- **Type**: method
- **Description**: Handles opening resource files relative to the application's instance path, mixing file I/O with core app logic.
- **Reasoning**: Similar to `open_resource`, this method is focused on file system access and path resolution (I/O), a responsibility distinct from the core application logic. It contributes to the 'Flask' class taking on too many unrelated concerns.

### SRP-021 [HIGH] src/flask/app.py — Flask.run
- **Confidence**: Found in 1 scan(s)
- **Lines**: 574–648
- **Type**: method
- **Description**: Manages the local development server, including environment variable loading, debug mode settings, and calling Werkzeug's run_simple.
- **Reasoning**: This method takes on the significant responsibility of running a complete development server. This involves configuring environment variables, setting debug flags, and binding to a host/port. This is an operational concern that is separate from the core application logic. While convenient for development, it strongly violates SRP by mixing server management with application definition.

### SRP-022 [MEDIUM] src/flask/app.py — Flask.test_client
- **Confidence**: Found in 1 scan(s)
- **Lines**: 650–691
- **Type**: method
- **Description**: Creates a test client for the application, integrating testing concerns directly into the main app class.
- **Reasoning**: The responsibility of creating and configuring a test client (which involves instantiating `FlaskClient` and setting up its parameters) is specific to testing infrastructure, not the core runtime behavior of the application itself. This could be externalized to a testing utility module or factory.

### SRP-023 [MEDIUM] src/flask/app.py — Flask.test_cli_runner
- **Confidence**: Found in 1 scan(s)
- **Lines**: 693–706
- **Type**: method
- **Description**: Creates a CLI runner for testing, integrating CLI testing concerns directly into the main app class.
- **Reasoning**: Similar to `test_client`, creating a CLI runner for testing (`FlaskCliRunner`) is a concern of the testing framework. The core application class should not be directly responsible for instantiating and configuring test utilities.

### SRP-024 [HIGH] src/flask/app.py — Flask.wsgi_app
- **Confidence**: Found in 1 scan(s)
- **Lines**: 894–929
- **Type**: method
- **Description**: The main WSGI application entry point, orchestrating request context, dispatch, error handling, and response processing.
- **Reasoning**: This method is a central orchestrator, combining context management (`request_context`, `ctx.push`, `ctx.pop`), request dispatching (`full_dispatch_request`), and top-level error handling (`handle_exception`). While it's the core of the WSGI application, its broad orchestration role demonstrates a high coupling to many sub-responsibilities within the `Flask` class itself, making it a focal point of SRP violations.

### SRP-026 [MEDIUM] src/flask/sansio/app.py — App.make_config
- **Confidence**: Found in 1 scan(s)
- **Lines**: 387–399
- **Type**: method
- **Description**: Creates and initializes the application's configuration object, mixing configuration management with core app logic.
- **Reasoning**: The process of creating and populating the configuration object with defaults and handling instance-relative paths is a distinct responsibility. This factory-like method could reside outside the `App` class, promoting a separation between application definition and its configuration mechanism.

### SRP-027 [LOW] src/flask/sansio/app.py — App.make_aborter
- **Confidence**: Found in 1 scan(s)
- **Lines**: 410–419
- **Type**: method
- **Description**: Creates the aborter object, mixing object instantiation with core app logic.
- **Reasoning**: While the `App` class uses an aborter, the specific factory logic for creating an instance of `aborter_class` could be a static method or a simple function, rather than a method of the `App` instance, to better separate concerns.

### SRP-028 [MEDIUM] src/flask/sansio/app.py — App._find_error_handler
- **Confidence**: Found in 1 scan(s)
- **Lines**: 622–645
- **Type**: method
- **Description**: Locates the appropriate error handler for a given exception and blueprint context.
- **Reasoning**: This method contains specific logic for searching through registered error handlers across blueprints and the application. This is a complex lookup responsibility that could be part of a dedicated error handling registry or strategy, rather than embedded directly in the core application logic.

### SRP-029 [MEDIUM] src/flask/sansio/app.py — App.trap_http_exception
- **Confidence**: Found in 1 scan(s)
- **Lines**: 647–677
- **Type**: method
- **Description**: Determines whether an HTTP exception should be trapped based on configuration, mixing error policy with core app logic.
- **Reasoning**: This method contains policy logic for deciding when to trap HTTP exceptions (e.g., based on `TRAP_HTTP_EXCEPTIONS`, `TRAP_BAD_REQUEST_ERRORS`, debug mode). This is a configuration-driven decision-making process that could be part of an 'ExceptionPolicy' component, separate from the `App` class's primary role.

### SRP-031 [LOW] src/flask/sansio/scaffold.py — Scaffold.static_url_path
- **Confidence**: Found in 1 scan(s)
- **Lines**: 186–195
- **Type**: class
- **Description**: Property for deriving the URL prefix for static files, mixing URL generation logic with component registration.
- **Reasoning**: Similar to `static_folder`, the logic for generating a default URL path for static files is a URL generation concern. This could be moved to a URL utility or a static asset helper.

### SRP-032 [MEDIUM] src/flask/sansio/scaffold.py — Scaffold.jinja_loader
- **Confidence**: Found in 1 scan(s)
- **Lines**: 204–210
- **Type**: class
- **Description**: Property for creating the Jinja template loader, mixing templating setup with component registration.
- **Reasoning**: The responsibility of creating the Jinja `FileSystemLoader` for templates, including resolving its path, is a specific templating setup concern. While `Scaffold` needs a template folder, the actual creation of the loader could be externalized to a templating utility or factory, maintaining `Scaffold`'s focus on component registration.

### SRP-033 [MEDIUM] src/flask/blueprints.py — Blueprint.get_send_file_max_age
- **Confidence**: Found in 1 scan(s)
- **Lines**: 61–77
- **Type**: method
- **Description**: Determines the max-age cache value for static files, duplicating logic from Flask and mixing static file serving with blueprint definition.
- **Reasoning**: This method is a duplicate of the one in the `Flask` class and deals with specific caching logic for static files. A `Blueprint`'s core responsibility is to define a modular group of routes and components, not to implement static file serving details. This logic should be centralized in a shared utility or service that both `Flask` and `Blueprint` can use.

### SRP-034 [MEDIUM] src/flask/blueprints.py — Blueprint.send_static_file
- **Confidence**: Found in 1 scan(s)
- **Lines**: 79–93
- **Type**: method
- **Description**: Serves static files from the blueprint's static folder, duplicating logic from Flask and mixing static file serving with blueprint definition.
- **Reasoning**: This method also duplicates logic from the `Flask` class. Serving static files involves I/O and HTTP response construction, which is a distinct responsibility from defining modular application components. This logic should be externalized to a shared utility or service.

### SRP-035 [MEDIUM] src/flask/cli.py — load_dotenv
- **Confidence**: Found in 1 scan(s)
- **Lines**: 361–409
- **Type**: class
- **Description**: Loads environment variables from dotenv files, a distinct responsibility from CLI command execution or app discovery.
- **Reasoning**: The function's sole responsibility is to load environment variables from specified files. While crucial for CLI and app setup, this is a general configuration utility that isn't inherently tied to the CLI module's primary concern of defining and executing command-line commands. It could be placed in a more generic configuration or utility module.

### SRP-037 [LOW] src/flask/json/provider.py — DefaultJSONProvider.response
- **Confidence**: Found in 1 scan(s)
- **Lines**: 204–226
- **Type**: method
- **Description**: Combines JSON serialization with HTTP response object creation, including formatting based on debug mode.
- **Reasoning**: Similar to `JSONProvider.response`, this method mixes data serialization (JSON) with HTTP response construction. It further adds logic for formatting the JSON output (compact vs. pretty print) based on the application's debug status, which slightly increases its reasons to change (serialization logic, HTTP response details, and formatting preferences).

### SRP-038 [MEDIUM] src/flask/cli.py — ScriptInfo.load_app
- **Confidence**: Found in 1 scan(s)
- **Lines**: 160–189
- **Type**: method
- **Description**: The 'load_app' method is responsible for both locating/instantiating the Flask application and applying CLI-specific debug configuration to it.
- **Reasoning**: The primary responsibility of `load_app` should be to find and return the Flask application instance. However, it also includes logic to set the `app.debug` flag based on CLI context. This couples the application loading process with CLI-specific configuration application, giving it two reasons to change (how to find an app, and how to configure it for the CLI environment).

### SRP-039 [MEDIUM] src/flask/sansio/app.py — App.debug
- **Confidence**: Found in 1 scan(s)
- **Lines**: 307–317
- **Type**: class
- **Description**: The 'debug' property setter couples configuration setting with template engine behavior by modifying 'jinja_env.auto_reload'.
- **Reasoning**: The `debug` property's setter not only updates the `DEBUG` configuration key but also directly modifies the `auto_reload` setting of the `jinja_env`. This creates a tight coupling between the application's debug state and the template engine's behavior, meaning a change in how debug mode affects templating would require changing this property, violating SRP.

### SRP-042 [MEDIUM] src/flask/helpers.py — _prepare_send_file_kwargs
- **Confidence**: Found in 1 scan(s)
- **Lines**: 249–259
- **Type**: class
- **Description**: The '_prepare_send_file_kwargs' function is responsible for gathering various configuration parameters from 'current_app' and 'request' contexts for file sending.
- **Reasoning**: This helper function's sole purpose is to collect configuration from disparate sources (`app_ctx`, `app.get_send_file_max_age`, `app.config`, `request.environ`) to prepare arguments for `werkzeug.utils.send_file`. While it's a helper, the act of gathering and consolidating configuration from multiple global contexts is a distinct responsibility from the actual file-sending logic. This exhibits Feature Envy towards the `AppContext` and `Flask` objects.

### SRP-045 [HIGH] src/flask/sessions.py — SecureCookieSessionInterface
- **Confidence**: Found in 1 scan(s)
- **Lines**: 170–234
- **Type**: class
- **Description**: The 'SecureCookieSessionInterface' class combines cryptographic signing/serialization of session data with the actual setting and deletion of HTTP cookies on the response.
- **Reasoning**: This class is responsible for configuring and performing the secure serialization and deserialization of session data (using `itsdangerous` and a JSON serializer), and also for the HTTP-specific task of setting and deleting cookies on the `Response` object. These are separate concerns: data security/serialization and HTTP cookie management. Changes to the cryptographic details or serialization format, or changes to how cookies are manipulated, would both require modifying this class.

### SRP-047 [MEDIUM] src/flask/json/tag.py — TaggedJSONSerializer
- **Confidence**: Found in 1 scan(s)
- **Lines**: 201–260
- **Type**: class
- **Description**: The 'TaggedJSONSerializer' class manages the registration and ordering of JSON tags and performs the actual JSON serialization/deserialization using these tags.
- **Reasoning**: This class is responsible for two main concerns: managing a registry of `JSONTag` objects (adding, ordering, checking) and performing the actual JSON serialization (`dumps`) and deserialization (`loads`) of data, which involves applying these tags. The management of the tagging system is distinct from the core JSON serialization/deserialization process itself. Changes to how tags are registered or processed, or changes to the underlying JSON serialization logic, would both require modifying this class.

### SRP-048 [MEDIUM] src/flask/json/provider.py — JSONProvider
- **Confidence**: Found in 1 scan(s)
- **Lines**: 20–65
- **Type**: class
- **Description**: The 'JSONProvider' class defines the interface for JSON serialization/deserialization and also includes methods specifically for creating HTTP 'Response' objects with JSON content.
- **Reasoning**: This class has two distinct responsibilities: providing an interface for converting Python objects to JSON strings (`dumps`, `loads`) and providing methods (`_prepare_response_obj`, `response`) for packaging that JSON string into an HTTP `Response` object with the correct mimetype. Changes to the JSON serialization contract or changes to how HTTP responses are constructed would both require modifying this class.

### SRP-049 [MEDIUM] src/flask/json/provider.py — DefaultJSONProvider
- **Confidence**: Found in 1 scan(s)
- **Lines**: 92–160
- **Type**: class
- **Description**: The 'DefaultJSONProvider' class implements JSON serialization/deserialization, configures the underlying 'json' library, and handles specific formatting and mimetype for HTTP responses.
- **Reasoning**: This class is responsible for the concrete implementation of JSON serialization/deserialization (using Python's `json` module), configuring the behavior of that underlying library (e.g., `ensure_ascii`, `sort_keys`), and applying specific formatting rules (e.g., `compact`, `indent`) and mimetype for HTTP responses. These are separate concerns, violating SRP.

### SRP-050 [LOW] src/flask/templating.py — Environment
- **Confidence**: Found in 1 scan(s)
- **Lines**: 40–46
- **Type**: class
- **Description**: The 'Environment' class, a Jinja environment, is responsible for knowing how to get its loader from the Flask application.
- **Reasoning**: The `Environment` class's constructor directly calls `app.create_global_jinja_loader()`. While it's a Jinja environment, it takes on the responsibility of *knowing how to obtain its loader from the Flask application*, rather than simply being provided with a loader. This creates an Inappropriate Intimacy smell and a minor SRP violation.

### SRP-053 [MEDIUM] src/flask/logging.py — create_logger
- **Confidence**: Found in 1 scan(s)
- **Lines**: 42–55
- **Type**: class
- **Description**: The 'create_logger' function is responsible for both creating a logger instance and applying specific configuration policies to it (setting debug level, adding default handler).
- **Reasoning**: This function combines the responsibility of instantiating a Python logger with the responsibility of applying specific configuration policies based on the application's state (e.g., setting the debug level if `app.debug` is true, adding a default handler if none exists). These are distinct concerns: logger creation and logger configuration policy application. Changes to either would require modifying this function.

### SRP-054 [LOW] src/flask/json/provider.py — DefaultJSONProvider.response
- **Confidence**: Found in 1 scan(s)
- **Lines**: 161–182
- **Type**: method
- **Description**: The response method combines JSON serialization with HTTP response object creation and configuration.
- **Reasoning**: This method is responsible for serializing Python objects to JSON, and then, in the same method, creating a `Flask.Response` object, setting its `mimetype`, and applying formatting based on `app.debug` or `compact` settings. The concern of JSON serialization is distinct from the concern of HTTP response construction, indicating a Divergent Change smell.

### SRP-055 [HIGH] src/flask/cli.py — FlaskGroup
- **Confidence**: Found in 1 scan(s)
- **Lines**: 251–370
- **Type**: class
- **Description**: The FlaskGroup class acts as a God Class for Flask's command-line interface, combining many distinct responsibilities.
- **Reasoning**: It manages Click command parameters, default CLI commands, discovers and integrates plugin commands, handles loading the Flask application for CLI context, integrates app-specific CLI commands, and manages the overall CLI lifecycle (context creation, argument parsing). This broad set of responsibilities makes it highly susceptible to changes from various aspects of the CLI system.

### SRP-056 [MEDIUM] src/flask/cli.py — FlaskGroup
- **Confidence**: Found in 1 scan(s)
- **Lines**: 410–502
- **Type**: class
- **Description**: The 'FlaskGroup' class is a God Class for the Flask CLI, orchestrating various CLI-related responsibilities.
- **Reasoning**: This class combines responsibilities for managing the Click command group, adding default Flask CLI commands, discovering additional commands from plugins and the application instance, managing the CLI-specific application context, and orchestrating environment variable loading. These are several distinct concerns related to the CLI, making the class prone to changes from multiple sources and thus violating SRP.

### SRP-057 [MEDIUM] src/flask/testing.py — FlaskClient
- **Confidence**: Found in 1 scan(s)
- **Lines**: 90–205
- **Type**: class
- **Description**: The 'FlaskClient' class extends a generic HTTP test client with multiple Flask-specific testing concerns.
- **Reasoning**: This class is responsible for being a generic HTTP test client (inherited from Werkzeug's Client), for managing Flask's request context preservation during tests, for handling Flask's session lifecycle within test transactions, and for incorporating Flask-specific environment building logic. These are distinct testing-related responsibilities, and bundling them into one class violates SRP as changes to any of these areas would require modifying 'FlaskClient'.

### SRP-058 [LOW] src/flask/sansio/app.py — App._find_error_handler
- **Confidence**: Found in 1 scan(s)
- **Lines**: 801–826
- **Type**: method
- **Description**: The '_find_error_handler' method encapsulates the logic for looking up error handlers based on exception type and HTTP code, which is a specific error handling strategy responsibility.
- **Reasoning**: This method contains specific logic for traversing blueprint and application error handler registries to find the most suitable handler for a given exception. This 'lookup strategy' is a distinct responsibility from merely registering error handlers or managing the application's overall lifecycle. It could be extracted into a dedicated error handling utility or strategy class.

### SRP-060 [LOW] src/flask/ctx.py — AppContext._get_session
- **Confidence**: Found in 1 scan(s)
- **Lines**: 386–396
- **Type**: method
- **Description**: The '_get_session' method encapsulates logic for opening and potentially creating a null session, which is a session management responsibility.
- **Reasoning**: This method is responsible for interacting with the session interface to retrieve or create a session. This is a specific session management concern, distinct from the core responsibility of managing the application context's lifecycle. Changes to how sessions are opened or handled would require modifying this method within the context class.

### SRP-064 [MEDIUM] src/flask/sansio/blueprints.py — Blueprint.register
- **Confidence**: Found in 1 scan(s)
- **Lines**: 305–420
- **Type**: class
- **Description**: The 'register' method combines multiple responsibilities including blueprint validation, static file routing setup, merging blueprint functions, CLI command integration, and recursive registration of nested blueprints with complex URL/subdomain merging.
- **Reasoning**: The `register` method is overloaded with responsibilities. It performs:
1. **Validation**: Checks for unique blueprint names.
2. **Static File Setup**: Configures static URL rules if a static folder is present.
3. **Function Merging**: Calls `_merge_blueprint_funcs` to integrate the blueprint's handlers into the main application.
4. **CLI Integration**: Handles the blueprint's CLI commands, potentially merging them into the app's CLI group.
5. **Recursive Blueprint Registration**: Iterates and registers nested blueprints, which involves complex logic for combining `url_prefix` and `subdomain` options.
Each of these aspects could change independently, providing multiple reasons for the `register` method to be modified, thus violating SRP within this method.
