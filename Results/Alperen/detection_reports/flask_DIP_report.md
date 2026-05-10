# DIP Violation Report: flask

## Summary
- **Total unique issues**: 11
- **High severity**: 5
- **Medium severity**: 6
- **Low severity**: 0
- **Found by multiple scans**: 6/11

## Issues

### DIP-001 [HIGH] src/flask/app.py — Flask.__init__
- **Confidence**: Found in 12 scan(s)
- **Lines**: 288–288
- **Type**: class
- **Description**: Direct instantiation of CLI command group
- **Reasoning**: The Flask class directly instantiates cli.AppGroup in its constructor. This creates a tight coupling between the high-level application class and the low-level CLI implementation detail, violating the principle that high-level modules should not depend on low-level modules.

### DIP-003 [MEDIUM] src/flask/sansio/app.py — App.__init__
- **Confidence**: Found in 8 scan(s)
- **Lines**: 214–214
- **Type**: class
- **Description**: Direct instantiation of JSONProvider via json_provider_class
- **Reasoning**: The App class instantiates its own JSON provider during initialization. This violates DIP because the high-level App class is responsible for creating its own low-level utility for JSON processing, rather than receiving a provider through dependency injection.

### DIP-002 [HIGH] src/flask/blueprints.py — Blueprint.__init__
- **Confidence**: Found in 4 scan(s)
- **Lines**: 48–48
- **Type**: class
- **Description**: Direct instantiation of CLI AppGroup in Blueprint
- **Reasoning**: The Blueprint class directly instantiates AppGroup in its __init__ method. This creates a hard-coded dependency on the CLI implementation, preventing the use of blueprints in environments where the CLI component might not be desired or might need to be different.

### DIP-004 [MEDIUM] src/flask/ctx.py — AppContext.__init__
- **Confidence**: Found in 3 scan(s)
- **Lines**: 215–215
- **Type**: class
- **Description**: Direct instantiation of the globals container (_AppCtxGlobals)
- **Reasoning**: AppContext directly instantiates the concrete class for request globals (via app.app_ctx_globals_class). This couples the context management logic to a specific implementation of the storage container.

### DIP-005 [MEDIUM] src/flask/cli.py — FlaskGroup.make_context
- **Confidence**: Found in 2 scan(s)
- **Lines**: 651–671
- **Type**: class
- **Description**: Direct instantiation of ScriptInfo within the method.
- **Reasoning**: The method directly instantiates ScriptInfo instead of receiving it through injection or using a configurable factory. This tight coupling prevents the substitution of alternative script information handlers.

### DIP-009 [HIGH] src/flask/json/provider.py — JSONProvider
- **Confidence**: Found in 2 scan(s)
- **Lines**: 19–105
- **Type**: class
- **Description**: Low-level JSON provider depends on the concrete high-level App class.
- **Reasoning**: The JSONProvider (a low-level utility) is initialized with a concrete App instance, creating a bidirectional coupling between high-level application logic and low-level JSON serialization details.

### DIP-006 [MEDIUM] src/flask/sansio/scaffold.py — Scaffold.jinja_loader
- **Confidence**: Found in 1 scan(s)
- **Lines**: 240–249
- **Type**: class
- **Description**: Direct instantiation of a concrete template loader.
- **Reasoning**: The jinja_loader property directly instantiates FileSystemLoader. This couples the Scaffold class (and its children, Flask and Blueprint) to a specific filesystem-based template loading mechanism rather than an abstraction.

### DIP-007 [HIGH] src/flask/config.py — Config.from_pyfile
- **Confidence**: Found in 1 scan(s)
- **Lines**: 187–187
- **Type**: class
- **Description**: High-level configuration class depends on low-level file system details.
- **Reasoning**: The Config class contains methods that directly interact with the file system and Python's import machinery to load settings. This couples the configuration abstraction to specific storage and format details, violating the rule that high-level modules should not depend on low-level details.

### DIP-008 [MEDIUM] src/flask/sessions.py — SessionInterface.make_null_session
- **Confidence**: Found in 1 scan(s)
- **Lines**: 150–150
- **Type**: class
- **Description**: Abstraction depends on concrete implementation detail (NullSession).
- **Reasoning**: The SessionInterface (an abstraction) directly instantiates NullSession (a concrete detail). Furthermore, its methods depend on the concrete Flask class, creating a circular dependency where the abstraction depends on specific implementation details.

### DIP-010 [HIGH] src/flask/templating.py — Environment
- **Confidence**: Found in 1 scan(s)
- **Lines**: 36–46
- **Type**: class
- **Description**: Templating environment depends on the concrete App class.
- **Reasoning**: The Jinja Environment implementation depends directly on the high-level App class, violating the principle that low-level details should not depend on high-level modules unless through abstractions.

### DIP-011 [MEDIUM] src/flask/templating.py — DispatchingJinjaLoader
- **Confidence**: Found in 1 scan(s)
- **Lines**: 49–120
- **Type**: class
- **Description**: Low-level template loader depends on the high-level App object.
- **Reasoning**: The Jinja loader is a low-level utility for file/resource access, but it depends directly on the App instance (L54). This dependency should be inverted by passing only the necessary abstractions (like a list of search paths) rather than the entire application object.
