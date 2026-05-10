# Refactor OCP-001 (OCP): Type-checking logic using instanceof chain for expression compilation

**Status:** `obsolete`  
**Branch:** `refactor/OCP-001` -> `main`  
**Head commit:** `c1ce15e4298601410fdaf3b54f3ac48c0b3c9865`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java`
- **Entity**: `EventCondition.Compiler.buildCondition` (method)
- **Lines (at detection time)**: L100–L125
- **Severity**: high
- **Confidence**: detected by 5 scan(s)

**Description.** Type-checking logic using instanceof chain for expression compilation

**Reasoning.** The buildCondition method uses a long chain of instanceof checks to determine how to compile different BooleanExpression types. Adding a new expression type to the Logstash configuration language requires modifying this central compiler method instead of extending the system through polymorphism or a visitor pattern.

## Obsolete

entity `EventCondition.Compiler.buildCondition` not found in current source of `logstash-core/src/main/java/org/logstash/config/ir/compiler/EventCondition.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
