# Refactor Shortlist: flask

Quota: 12 issues × 5 principles = 60 total.
Selected: **59**.

> **Note:** the following principles have fewer issues than the quota. Per the project brief, seed violations manually to fill the gap:
> - DIP: 11 / 12

Ranking: `scan_count` desc, then severity (high > medium > low), then file_path, then line_start.

## SRP (12 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | SRP-001 | 11 scan(s) | medium | `src/flask/app.py` Flask.send_static_file (L306–316) | The Flask application directly implements static file serving logic. |
| 2 | SRP-040 | 7 scan(s) | high | `src/flask/sansio/blueprints.py` Blueprint.register (L160–230) | The 'register' method is responsible for both defining the blueprint's components and orchestrating their integration into the main 'App' object, including merging various types of functions and static files. |
| 3 | SRP-025 | 6 scan(s) | medium | `src/flask/sansio/app.py` App.auto_find_instance_path (L401–408) | Automatically locates the application's instance path, mixing file system path resolution with core app logic. |
| 4 | SRP-004 | 5 scan(s) | medium | `src/flask/app.py` Flask.run (L409–486) | The Flask application directly implements the logic for running a development server. |
| 5 | SRP-030 | 5 scan(s) | low | `src/flask/sansio/scaffold.py` Scaffold.static_folder (L169–175) | Property for resolving the absolute path of the static folder, mixing path resolution with component registration. |
| 6 | SRP-014 | 4 scan(s) | medium | `src/flask/blueprints.py` Blueprint.get_send_file_max_age (L105–120) | The 'get_send_file_max_age' method handles specific logic for determining cache control for static files within a blueprint. |
| 7 | SRP-036 | 4 scan(s) | low | `src/flask/json/provider.py` JSONProvider.response (L98–105) | Combines JSON serialization with HTTP response object creation. |
| 8 | SRP-046 | 3 scan(s) | high | `src/flask/config.py` Config (L35–241) | The 'Config' class acts as a dictionary for configuration storage but also implements numerous strategies for loading configuration from environment variables, Python files, generic files, and objects. |
| 9 | SRP-043 | 3 scan(s) | high | `src/flask/ctx.py` AppContext (L98–280) | The 'AppContext' class manages the entire lifecycle of application and request contexts, including state, session initialization, routing, and teardown orchestration. |
| 10 | SRP-044 | 3 scan(s) | high | `src/flask/sessions.py` SessionInterface (L78–166) | The 'SessionInterface' class defines the core contract for session storage and also provides a comprehensive set of methods for configuring all aspects of the session cookie. |
| 11 | SRP-005 | 3 scan(s) | medium | `src/flask/app.py` Flask.test_client (L488–536) | The Flask application provides methods for creating a test client. |
| 12 | SRP-061 | 3 scan(s) | medium | `src/flask/cli.py` FlaskGroup.get_command (L590–614) | The 'get_command' method combines responsibilities for loading plugin commands, loading the Flask application, and pushing an application context, in addition to its primary role of retrieving a CLI command. |

## OCP (12 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | OCP-001 | 5 scan(s) | high | `src/flask/app.py` Flask.make_response (L1007–1069) | The method uses a long if/elif/else chain to convert various return types into a Response object. |
| 2 | OCP-002 | 4 scan(s) | medium | `src/flask/cli.py` find_best_app (L41–79) | Hardcoded logic to discover Flask application instances or factory functions by specific names. |
| 3 | OCP-003 | 4 scan(s) | medium | `src/flask/cli.py` find_app_by_string (L94–142) | Fixed parsing logic for app string and type-checking for attribute handling. |
| 4 | OCP-008 | 4 scan(s) | medium | `src/flask/sansio/app.py` App.select_jinja_autoescape (L404–408) | Hardcoded list of file extensions to determine Jinja autoescape behavior. |
| 5 | OCP-011 | 4 scan(s) | medium | `src/flask/sansio/blueprints.py` Blueprint.register (L161–236) | Contains multiple if/elif/else blocks for handling blueprint registration options and nested blueprints. |
| 6 | OCP-010 | 4 scan(s) | medium | `src/flask/sansio/scaffold.py` Scaffold._get_exc_class_and_code (L401–435) | Fixed logic for determining exception class and HTTP code from various input types. |
| 7 | OCP-027 | 3 scan(s) | high | `src/flask/app.py` Flask.make_response (L818–907) | Extensive if/elif chain with isinstance checks for various return types to convert to a Response object. |
| 8 | OCP-013 | 3 scan(s) | high | `src/flask/json/provider.py` DefaultJSONProvider._default (L100–113) | A series of if statements to handle custom JSON serialization for specific Python types. |
| 9 | OCP-042 | 3 scan(s) | medium | `src/flask/cli.py` FlaskGroup.get_command (L609–609) | The `get_command` method might contain logic to find commands that needs modification to support new command discovery mechanisms. |
| 10 | OCP-033 | 2 scan(s) | high | `src/flask/app.py` Flask.make_response (L920–977) | The method uses extensive type-checking and conditional logic to convert various return values into a Response object. |
| 11 | OCP-020 | 2 scan(s) | medium | `src/flask/app.py` Flask.create_url_adapter (L361–393) | Conditional logic based on host_matching and subdomain_matching config flags. |
| 12 | OCP-022 | 2 scan(s) | medium | `src/flask/app.py` Flask.run (L448–509) | Multiple conditional branches for configuration, environment variables, and argument handling. |

## LSP (12 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | LSP-027 | 3 scan(s) | medium | `src/flask/sansio/blueprints.py` Blueprint.app_template_filter (L450–450) | Abstract method `app_template_filter` in base class `Blueprint` is not implemented by subclasses. |
| 2 | LSP-024 | 3 scan(s) | medium | `src/flask/sansio/scaffold.py` Scaffold._check_setup_finished (L71–77) | Subclasses must implement _check_setup_finished to prevent modification after registration. |
| 3 | LSP-022 | 3 scan(s) | low | `src/flask/sansio/app.py` App.create_jinja_environment (L246–255) | Subclass must implement create_jinja_environment to provide a Jinja environment. |
| 4 | LSP-001 | 2 scan(s) | medium | `src/flask/app.py` Flask.handle_http_exception (L510–531) | Subclass might override handle_http_exception and not handle RoutingException or RequestRedirect correctly. |
| 5 | LSP-017 | 1 scan(s) | high | `src/flask/app.py` Flask.wsgi_app (L1331–1368) | Subclass might override wsgi_app and not correctly handle the WSGI application lifecycle, including context management and exception handling. |
| 6 | LSP-025 | 1 scan(s) | high | `src/flask/views.py` View.dispatch_request (L67–72) | Subclasses must implement dispatch_request to define view logic. |
| 7 | LSP-002 | 1 scan(s) | medium | `src/flask/app.py` Flask.handle_user_exception (L534–557) | Subclass might override handle_user_exception and not correctly delegate HTTP exceptions or handle error handlers. |
| 8 | LSP-003 | 1 scan(s) | medium | `src/flask/app.py` Flask.handle_exception (L560–619) | Subclass might override handle_exception and alter the propagation of exceptions or the finalization of requests. |
| 9 | LSP-005 | 1 scan(s) | medium | `src/flask/app.py` Flask.dispatch_request (L633–662) | Subclass might override dispatch_request and not handle routing exceptions, OPTIONS requests, or view function dispatching correctly. |
| 10 | LSP-006 | 1 scan(s) | medium | `src/flask/app.py` Flask.full_dispatch_request (L665–695) | Subclass might override full_dispatch_request and alter the request lifecycle, including preprocessing, dispatching, exception handling, and finalization. |
| 11 | LSP-007 | 1 scan(s) | medium | `src/flask/app.py` Flask.finalize_request (L698–729) | Subclass might override finalize_request and not correctly process the response or send the request_finished signal. |
| 12 | LSP-011 | 1 scan(s) | medium | `src/flask/app.py` Flask.url_for (L896–971) | Subclass might override url_for and not correctly generate URLs or handle URL build errors. |

## ISP (12 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | ISP-074 | 4 scan(s) | medium | `src/flask/sessions.py` SessionInterface (L72–250) | The SessionInterface defines many configuration getters and core methods, potentially forcing implementers to provide unused functionality. |
| 2 | ISP-001 | 3 scan(s) | medium | `src/flask/app.py` Flask.handle_http_exception (L488–503) | The handle_http_exception method handles both routing exceptions and other HTTP exceptions, violating ISP. |
| 3 | ISP-083 | 3 scan(s) | medium | `src/flask/ctx.py` AppContext (L260–525) | AppContext violates ISP by merging request-specific functionality into a general application context. |
| 4 | ISP-079 | 3 scan(s) | medium | `src/flask/json/provider.py` JSONProvider (L24–97) | Fat interface mixing JSON serialization with Flask-specific HTTP response logic. |
| 5 | ISP-044 | 3 scan(s) | medium | `src/flask/sansio/scaffold.py` Scaffold.add_url_rule (L328–379) | The add_url_rule method handles methods, endpoint naming, automatic OPTIONS, defaults, and rule object creation, violating ISP. |
| 6 | ISP-027 | 2 scan(s) | medium | `src/flask/sansio/app.py` App.create_jinja_environment (L336–359) | The create_jinja_environment method configures Jinja with autoescape and auto_reload based on app debug status, potentially forcing unwanted configurations. |
| 7 | ISP-084 | 1 scan(s) | high | `src/flask/sessions.py` NullSession (L83–97) | NullSession implements a mutable session interface only to disable it by raising errors. |
| 8 | ISP-002 | 1 scan(s) | medium | `src/flask/app.py` Flask.handle_user_exception (L505–528) | The handle_user_exception method handles general exceptions and HTTP exceptions, violating ISP. |
| 9 | ISP-003 | 1 scan(s) | medium | `src/flask/app.py` Flask.handle_exception (L530–571) | The handle_exception method handles unhandled exceptions and propagates them, potentially involving other handlers, violating ISP. |
| 10 | ISP-005 | 1 scan(s) | medium | `src/flask/app.py` Flask.dispatch_request (L580–595) | The dispatch_request method handles routing exceptions, OPTIONS responses, and view function calls, violating ISP. |
| 11 | ISP-006 | 1 scan(s) | medium | `src/flask/app.py` Flask.full_dispatch_request (L597–619) | The full_dispatch_request method orchestrates request processing, including preprocessing, dispatching, and exception handling, violating ISP. |
| 12 | ISP-007 | 1 scan(s) | medium | `src/flask/app.py` Flask.finalize_request (L621–637) | The finalize_request method handles response creation, postprocessing, and signal sending, violating ISP. |

## DIP (11 selected)

| # | Issue ID | Confidence | Severity | Location | Description |
|---|----------|-----------:|----------|----------|-------------|
| 1 | DIP-001 | 12 scan(s) | high | `src/flask/app.py` Flask.__init__ (L288–288) | Direct instantiation of CLI command group |
| 2 | DIP-003 | 8 scan(s) | medium | `src/flask/sansio/app.py` App.__init__ (L214–214) | Direct instantiation of JSONProvider via json_provider_class |
| 3 | DIP-002 | 4 scan(s) | high | `src/flask/blueprints.py` Blueprint.__init__ (L48–48) | Direct instantiation of CLI AppGroup in Blueprint |
| 4 | DIP-004 | 3 scan(s) | medium | `src/flask/ctx.py` AppContext.__init__ (L215–215) | Direct instantiation of the globals container (_AppCtxGlobals) |
| 5 | DIP-009 | 2 scan(s) | high | `src/flask/json/provider.py` JSONProvider (L19–105) | Low-level JSON provider depends on the concrete high-level App class. |
| 6 | DIP-005 | 2 scan(s) | medium | `src/flask/cli.py` FlaskGroup.make_context (L651–671) | Direct instantiation of ScriptInfo within the method. |
| 7 | DIP-007 | 1 scan(s) | high | `src/flask/config.py` Config.from_pyfile (L187–187) | High-level configuration class depends on low-level file system details. |
| 8 | DIP-010 | 1 scan(s) | high | `src/flask/templating.py` Environment (L36–46) | Templating environment depends on the concrete App class. |
| 9 | DIP-006 | 1 scan(s) | medium | `src/flask/sansio/scaffold.py` Scaffold.jinja_loader (L240–249) | Direct instantiation of a concrete template loader. |
| 10 | DIP-008 | 1 scan(s) | medium | `src/flask/sessions.py` SessionInterface.make_null_session (L150–150) | Abstraction depends on concrete implementation detail (NullSession). |
| 11 | DIP-011 | 1 scan(s) | medium | `src/flask/templating.py` DispatchingJinjaLoader (L49–120) | Low-level template loader depends on the high-level App object. |
