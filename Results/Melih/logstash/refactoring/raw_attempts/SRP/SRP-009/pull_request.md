# Refactor SRP-009 (SRP): The Event class mixes data encapsulation with serialization and interpolation...

**Status:** `obsolete`  
**Branch:** `refactor/SRP-009` -> `main`  
**Head commit:** `1c876b4b4de952ca93cb22874807365b68658b60`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/Event.java`
- **Entity**: `org.logstash.Event` (class)
- **Lines (at detection time)**: L52–L329
- **Severity**: medium
- **Confidence**: detected by 1 scan(s)

**Description.** The Event class mixes data encapsulation with serialization and interpolation logic.

**Reasoning.** While its primary responsibility is to encapsulate Logstash event data, it also contains methods for JSON serialization/deserialization (toJson, fromJson), CBOR serialization, and complex string interpolation logic (sprintf). Serialization and formatting are external concerns that should be handled by dedicated codec or utility classes rather than the core data object.

## Obsolete

entity `org.logstash.Event` not found in current source of `logstash-core/src/main/java/org/logstash/Event.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
