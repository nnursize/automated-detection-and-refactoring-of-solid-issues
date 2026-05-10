# Refactor OCP-007 (OCP): Switch statement used to dispatch CLI command execution

**Status:** `applied_unverified`  
**Branch:** `refactor/OCP-007` -> `main`  
**Head commit:** `96d85fa348172e7cc1fc9f51827dd87ad353d526`  
**LLM finish:** `FinishReason.STOP` (prompt 4854, completion 2817)  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/secret/cli/SecretStoreCli.java`
- **Entity**: `SecretStoreCli.command` (method)
- **Lines (at detection time)**: L191–L285
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** Switch statement used to dispatch CLI command execution

**Reasoning.** The command method uses a switch statement to execute logic for different secret store operations (CREATE, LIST, ADD, REMOVE). Adding a new CLI command requires modifying this method. Implementing a Command pattern would allow adding new commands by creating new classes rather than modifying the central CLI controller.

## Fix logic

- **Model**: `gemini-3.1-flash-lite-preview` (temperature 0.2)
- **Patch blocks**: 2
- **Files modified** (1): `logstash-core/src/main/java/org/logstash/secret/cli/SecretStoreCli.java`

**Summary.** Refactor SecretStoreCli to use a Command pattern to resolve OCP violation

**Rationale.** Replaced the switch statement in SecretStoreCli.command with a map of CommandExecutor instances. This allows adding new commands by implementing the CommandExecutor interface without modifying the main CLI class.

## Changes overview

_2 patch block(s). Code blocks are previewed up to 60 lines each — full text is in `pull_request.json` (`fix_logic.changes`)._

### 1. EDIT `logstash-core/src/main/java/org/logstash/secret/cli/SecretStoreCli.java` (5-line block → 6-line replacement)

**Replaces:**

```java
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import static org.logstash.secret.store.SecretStoreFactory.LOGSTASH_MARKER;
```

**With:**

```java
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import static org.logstash.secret.store.SecretStoreFactory.LOGSTASH_MARKER;
```

### 2. EDIT `logstash-core/src/main/java/org/logstash/secret/cli/SecretStoreCli.java` (123-line block → 115-line replacement)

**Replaces:**

```java
    public void command(String primaryCommand, SecureConfig config, String... allArguments) {
        terminal.writeLine("");

        final Optional<CommandLine> commandParseResult;
        try {
            commandParseResult = Command.parse(primaryCommand, allArguments);
        } catch (InvalidCommandException e) {
            terminal.writeLine(String.format("ERROR: %s", e.getMessage()));
            return;
        }

        if (commandParseResult.isEmpty()) {
            printHelp();
            return;
        }

        final CommandLine commandLine = commandParseResult.get();
        switch (commandLine.getCommand()) {
            case CREATE: {
                if (commandLine.hasOption(CommandOptions.HELP)) {
                    terminal.writeLine("Creates a new keystore. For example: 'bin/logstash-keystore create'");
                    return;
                }
                if (secretStoreFactory.exists(config.clone())) {
                    terminal.write("An Logstash keystore already exists. Overwrite ? [y/N] ");
                    if (isYes(terminal.readLine())) {
                        create(config);
                    }
                } else {
                    create(config);
                }
                break;
            }
            case LIST: {
                if (commandLine.hasOption(CommandOptions.HELP)) {
                    terminal.writeLine("List all secret identifiers from the keystore. For example: " +
                            "`bin/logstash-keystore list`. Note - only the identifiers will be listed, not the secrets.");
                    return;
                }
                Collection<SecretIdentifier> ids = secretStoreFactory.load(config).list();
                List<String> keys = ids.stream().filter(id -> !id.equals(LOGSTASH_MARKER)).map(id -> id.getKey()).collect(Collectors.toList());
                Collections.sort(keys);
                keys.forEach(terminal::writeLine);
                break;
            }
            case ADD: {
                if (commandLine.hasOption(CommandOptions.HELP)) {
                    terminal.writeLine("Add secrets to the keystore. For example: " +
                            "`bin/logstash-keystore add my-secret`, at the prompt enter your secret. You will use the identifier ${my-secret} in your Logstash configuration.");
                    return;
                }
                if (commandLine.getArguments().isEmpty()) {
                    terminal.writeLine("ERROR: You must supply an identifier to add. (e.g. bin/logstash-keystore add my-secret)");
                    return;
                }
                if (secretStoreFactory.exists(config.clone())) {
                    final SecretStore secretStore = secretStoreFactory.load(config);
                    for (String argument : commandLine.getArguments()) {
                        if (!ConfigVariableExpander.KEY_PATTERN.matcher(argument).matches()) {
                            throw new IllegalArgumentException(String.format("Invalid secret key name `%s` provided. %s", argument, ConfigVariableExpander.KEY_PATTERN_DESCRIPTION));
... (63 more line(s) truncated)
```

**With:**

```java
    private interface CommandExecutor {
        void execute(CommandLine commandLine, SecureConfig config);
    }

    private final Map<Command, CommandExecutor> executors = Map.of(
        Command.CREATE, (cl, cfg) -> {
            if (cl.hasOption(CommandOptions.HELP)) {
                terminal.writeLine("Creates a new keystore. For example: 'bin/logstash-keystore create'");
                return;
            }
            if (secretStoreFactory.exists(cfg.clone())) {
                terminal.write("An Logstash keystore already exists. Overwrite ? [y/N] ");
                if (isYes(terminal.readLine())) {
                    create(cfg);
                }
            } else {
                create(cfg);
            }
        },
        Command.LIST, (cl, cfg) -> {
            if (cl.hasOption(CommandOptions.HELP)) {
                terminal.writeLine("List all secret identifiers from the keystore. For example: " +
                        "`bin/logstash-keystore list`. Note - only the identifiers will be listed, not the secrets.");
                return;
            }
            Collection<SecretIdentifier> ids = secretStoreFactory.load(cfg).list();
            List<String> keys = ids.stream().filter(id -> !id.equals(LOGSTASH_MARKER)).map(id -> id.getKey()).collect(Collectors.toList());
            Collections.sort(keys);
            keys.forEach(terminal::writeLine);
        },
        Command.ADD, (cl, cfg) -> {
            if (cl.hasOption(CommandOptions.HELP)) {
                terminal.writeLine("Add secrets to the keystore. For example: " +
                        "`bin/logstash-keystore add my-secret`, at the prompt enter your secret. You will use the identifier ${my-secret} in your Logstash configuration.");
                return;
            }
            if (cl.getArguments().isEmpty()) {
                terminal.writeLine("ERROR: You must supply an identifier to add. (e.g. bin/logstash-keystore add my-secret)");
                return;
            }
            if (secretStoreFactory.exists(cfg.clone())) {
                final SecretStore secretStore = secretStoreFactory.load(cfg);
                for (String argument : cl.getArguments()) {
                    if (!ConfigVariableExpander.KEY_PATTERN.matcher(argument).matches()) {
                        throw new IllegalArgumentException(String.format("Invalid secret key name `%s` provided. %s", argument, ConfigVariableExpander.KEY_PATTERN_DESCRIPTION));
                    }
                    final SecretIdentifier id = new SecretIdentifier(argument);
                    final byte[] existingValue = secretStore.retrieveSecret(id);
                    if (existingValue != null) {
                        SecretStoreUtil.clearBytes(existingValue);
                        terminal.write(String.format("%s already exists. Overwrite ? [y/N] ", argument));
                        if (!isYes(terminal.readLine())) {
                            continue;
                        }
                    }
                    final String enterValueMessage = String.format("Enter value for %s: ", argument);
                    char[] secret = null;
                    while (secret == null) {
                        terminal.write(enterValueMessage);
                        final char[] readSecret = terminal.readSecret();
... (55 more line(s) truncated)
```

## Code-quality metrics

Per file. Cells show `before → after`. For non-Python files, MI is unavailable and CC is approximate (branching-keyword count divided by detected functions).

| File | LOC | Funcs | Avg CC | Max CC | MI |
|------|-----|------:|-------:|-------:|---:|
| `logstash-core/src/main/java/org/logstash/secret/cli/SecretStoreCli.java` | 327 → 328 | 10 → 10 | 5.9 → 5.5 | 50 → 46 | 0 → 0 |

## Diff

```diff
diff --git a/logstash-core/src/main/java/org/logstash/secret/cli/SecretStoreCli.java b/logstash-core/src/main/java/org/logstash/secret/cli/SecretStoreCli.java
index f83fac8..e67f58a 100644
--- a/logstash-core/src/main/java/org/logstash/secret/cli/SecretStoreCli.java
+++ b/logstash-core/src/main/java/org/logstash/secret/cli/SecretStoreCli.java
@@ -35,6 +35,7 @@ import java.util.Collection;
 import java.util.Collections;
 import java.util.EnumSet;
 import java.util.List;
+import java.util.Map;
 import java.util.Optional;
 import java.util.Set;
 import java.util.stream.Collectors;
@@ -204,9 +205,107 @@ public class SecretStoreCli {
      * @param config         The configuration needed to work a secret store. May be null for help.
      * @param allArguments   This can be either identifiers for a secret, or a sub command like --help. May be null.
      */
+    private interface CommandExecutor {
+        void execute(CommandLine commandLine, SecureConfig config);
+    }
+
+    private final Map<Command, CommandExecutor> executors = Map.of(
+        Command.CREATE, (cl, cfg) -> {
+            if (cl.hasOption(CommandOptions.HELP)) {
+                terminal.writeLine("Creates a new keystore. For example: 'bin/logstash-keystore create'");
+                return;
+            }
+            if (secretStoreFactory.exists(cfg.clone())) {
+                terminal.write("An Logstash keystore already exists. Overwrite ? [y/N] ");
+                if (isYes(terminal.readLine())) {
+                    create(cfg);
+                }
+            } else {
+                create(cfg);
+            }
+        },
+        Command.LIST, (cl, cfg) -> {
+            if (cl.hasOption(CommandOptions.HELP)) {
+                terminal.writeLine("List all secret identifiers from the keystore. For example: " +
+                        "`bin/logstash-keystore list`. Note - only the identifiers will be listed, not the secrets.");
+                return;
+            }
+            Collection<SecretIdentifier> ids = secretStoreFactory.load(cfg).list();
+            List<String> keys = ids.stream().filter(id -> !id.equals(LOGSTASH_MARKER)).map(id -> id.getKey()).collect(Collectors.toList());
+            Collections.sort(keys);
+            keys.forEach(terminal::writeLine);
+        },
+        Command.ADD, (cl, cfg) -> {
+            if (cl.hasOption(CommandOptions.HELP)) {
+                terminal.writeLine("Add secrets to the keystore. For example: " +
+                        "`bin/logstash-keystore add my-secret`, at the prompt enter your secret. You will use the identifier ${my-secret} in your Logstash configuration.");
+                return;
+            }
+            if (cl.getArguments().isEmpty()) {
+                terminal.writeLine("ERROR: You must supply an identifier to add. (e.g. bin/logstash-keystore add my-secret)");
+                return;
+            }
+            if (secretStoreFactory.exists(cfg.clone())) {
+                final SecretStore secretStore = secretStoreFactory.load(cfg);
+                for (String argument : cl.getArguments()) {
+                    if (!ConfigVariableExpander.KEY_PATTERN.matcher(argument).matches()) {
+                        throw new IllegalArgumentException(String.format("Invalid secret key name `%s` provided. %s", argument, ConfigVariableExpander.KEY_PATTERN_DESCRIPTION));
+                    }
+                    final SecretIdentifier id = new SecretIdentifier(argument);
+                    final byte[] existingValue = secretStore.retrieveSecret(id);
+                    if (existingValue != null) {
+                        SecretStoreUtil.clearBytes(existingValue);
+                        terminal.write(String.format("%s already exists. Overwrite ? [y/N] ", argument));
+                        if (!isYes(terminal.readLine())) {
+                            continue;
+                        }
+                    }
+                    final String enterValueMessage = String.format("Enter value for %s: ", argument);
+                    char[] secret = null;
+                    while (secret == null) {
+                        terminal.write(enterValueMessage);
+                        final char[] readSecret = terminal.readSecret();
+                        if (readSecret == null || readSecret.length == 0) {
+                            terminal.writeLine("ERROR: Value cannot be empty");
+                            continue;
+                        }
+                        if (!ASCII_ENCODER.canEncode(CharBuffer.wrap(readSecret))) {
+                            terminal.writeLine("ERROR: Value must contain only ASCII characters");
+                            continue;
+                        }
+                        secret = readSecret;
+                    }
+                    add(secretStore, id, SecretStoreUtil.asciiCharToBytes(secret));
+                }
+            } else {
+                terminal.writeLine("ERROR: Logstash keystore not found. Use 'create' command to create one.");
+            }
+        },
+        Command.REMOVE, (cl, cfg) -> {
+            if (cl.hasOption(CommandOptions.HELP)) {
+                terminal.writeLine("Remove secrets from the keystore. For example: " +
+                        "`bin/logstash-keystore remove my-secret`");
+                return;
+            }
+            if (cl.getArguments().isEmpty()) {
+                terminal.writeLine("ERROR: You must supply a value to remove. (e.g. bin/logstash-keystore remove my-secret)");
+                return;
+            }
+            final SecretStore secretStore = secretStoreFactory.load(cfg);
+            for (String argument : cl.getArguments()) {
+                SecretIdentifier id = new SecretIdentifier(argument);
+                if (secretStore.containsSecret(id)) {
+                    secretStore.purgeSecret(id);
+                    terminal.writeLine(String.format("Removed '%s' from the Logstash keystore.", id.getKey()));
+                } else {
+                    terminal.writeLine(String.format("ERROR: '%s' does not exist in the Logstash keystore.", argument));
+                }
+            }
+        }
+    );
+
     public void command(String primaryCommand, SecureConfig config, String... allArguments) {
         terminal.writeLine("");
-
         final Optional<CommandLine> commandParseResult;
         try {
             commandParseResult = Command.parse(primaryCommand, allArguments);
@@ -214,118 +313,12 @@ public class SecretStoreCli {
             terminal.writeLine(String.format("ERROR: %s", e.getMessage()));
             return;
         }
-
         if (commandParseResult.isEmpty()) {
             printHelp();
             return;
         }
-
         final CommandLine commandLine = commandParseResult.get();
-        switch (commandLine.getCommand()) {
-            case CREATE: {
-                if (commandLine.hasOption(CommandOptions.HELP)) {
-                    terminal.writeLine("Creates a new keystore. For example: 'bin/logstash-keystore create'");
-                    return;
-                }
-                if (secretStoreFactory.exists(config.clone())) {
-                    terminal.write("An Logstash keystore already exists. Overwrite ? [y/N] ");
-                    if (isYes(terminal.readLine())) {
-                        create(config);
-                    }
-                } else {
-                    create(config);
-                }
-                break;
-            }
-            case LIST: {
-                if (commandLine.hasOption(CommandOptions.HELP)) {
-                    terminal.writeLine("List all secret identifiers from the keystore. For example: " +
-                            "`bin/logstash-keystore list`. Note - only the identifiers will be listed, not the secrets.");
-                    return;
-                }
-                Collection<SecretIdentifier> ids = secretStoreFactory.load(config).list();
-                List<String> keys = ids.stream().filter(id -> !id.equals(LOGSTASH_MARKER)).map(id -> id.getKey()).collect(Collectors.toList());
-                Collections.sort(keys);
-                keys.forEach(terminal::writeLine);
-                break;
-            }
-            case ADD: {
-                if (commandLine.hasOption(CommandOptions.HELP)) {
-                    terminal.writeLine("Add secrets to the keystore. For example: " +
-                            "`bin/logstash-keystore add my-secret`, at the prompt enter your secret. You will use the identifier ${my-secret} in your Logstash configuration.");
-                    return;
-                }
-                if (commandLine.getArguments().isEmpty()) {
-                    terminal.writeLine("ERROR: You must supply an identifier to add. (e.g. bin/logstash-keystore add my-secret)");
-                    return;
-                }
-                if (secretStoreFactory.exists(config.clone())) {
-                    final SecretStore secretStore = secretStoreFactory.load(config);
-                    for (String argument : commandLine.getArguments()) {
-                        if (!ConfigVariableExpander.KEY_PATTERN.matcher(argument).matches()) {
-                            throw new IllegalArgumentException(String.format("Invalid secret key name `%s` provided. %s", argument, ConfigVariableExpander.KEY_PATTERN_DESCRIPTION));
-                        }
-                        final SecretIdentifier id = new SecretIdentifier(argument);
-                        final byte[] existingValue = secretStore.retrieveSecret(id);
-                        if (existingValue != null) {
-                            SecretStoreUtil.clearBytes(existingValue);
-                            terminal.write(String.format("%s already exists. Overwrite ? [y/N] ", argument));
-                            if (!isYes(terminal.readLine())) {
-                                continue;
-                            }
-                        }
-
-                        final String enterValueMessage = String.format("Enter value for %s: ", argument);
-                        char[] secret = null;
-                        while (secret == null) {
-                            terminal.write(enterValueMessage);
-                            final char[] readSecret = terminal.readSecret();
-
-                            if (readSecret == null || readSecret.length == 0) {
-                                terminal.writeLine("ERROR: Value cannot be empty");
-                                continue;
-                            }
-
-                            if (!ASCII_ENCODER.canEncode(CharBuffer.wrap(readSecret))) {
-                                terminal.writeLine("ERROR: Value must contain only ASCII characters");
-                                continue;
-                            }
-
-                            secret = readSecret;
-                        }
-
-                        add(secretStore, id, SecretStoreUtil.asciiCharToBytes(secret));
-                    }
-                } else {
-                    terminal.writeLine("ERROR: Logstash keystore not found. Use 'create' command to create one.");
-                }
-                break;
-            }
-            case REMOVE: {
-                if (commandLine.hasOption(CommandOptions.HELP)) {
-                    terminal.writeLine("Remove secrets from the keystore. For example: " +
-                            "`bin/logstash-keystore remove my-secret`");
-                    return;
-                }
-                if (commandLine.getArguments().isEmpty()) {
-                    terminal.writeLine("ERROR: You must supply a value to remove. (e.g. bin/logstash-keystore remove my-secret)");
-                    return;
-                }
-
-                final SecretStore secretStore = secretStoreFactory.load(config);
-                for (String argument : commandLine.getArguments()) {
-                    SecretIdentifier id = new SecretIdentifier(argument);
-                    if (secretStore.containsSecret(id)) {
-                        secretStore.purgeSecret(id);
-                        terminal.writeLine(String.format("Removed '%s' from the Logstash keystore.", id.getKey()));
-                    } else {
-                        terminal.writeLine(String.format("ERROR: '%s' does not exist in the Logstash keystore.", argument));
-                    }
-                }
-
-                break;
-            }
-        }
+        executors.get(commandLine.getCommand()).execute(commandLine, config);
     }
 
     private void printHelp() {

```
