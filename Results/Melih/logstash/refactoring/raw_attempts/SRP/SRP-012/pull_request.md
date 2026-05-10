# Refactor SRP-012 (SRP): FieldReference mixes parsing logic, global configuration, and multi-layered c...

**Status:** `obsolete`  
**Branch:** `refactor/SRP-012` -> `main`  
**Head commit:** `35dea20c06626fcdd3105683ab602910f8605765`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/FieldReference.java`
- **Entity**: `org.logstash.FieldReference` (class)
- **Lines (at detection time)**: L36–L261
- **Severity**: low
- **Confidence**: detected by 1 scan(s)

**Description.** FieldReference mixes parsing logic, global configuration, and multi-layered caching.

**Reasoning.** This class encapsulates field paths but also contains the grammar/tokenizer logic for parsing those paths, manages global static state for escape styles, and maintains two separate concurrent caches (Java String and JRuby RubyString). The parsing logic (StrictTokenizer) and the global configuration of escape styles could be extracted to separate concerns.

## Obsolete

entity `org.logstash.FieldReference` not found in current source of `logstash-core/src/main/java/org/logstash/FieldReference.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
