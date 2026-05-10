# Refactor ISP-005 (ISP): The RubyIntegration.PluginFactory interface combines methods for building dif...

**Status:** `obsolete`  
**Branch:** `refactor/ISP-005` -> `main`  
**Head commit:** `22b093a1453fbe4f3f30563aa4cab10cf4907391`  

## Detected issue

- **File**: `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java`
- **Entity**: `RubyIntegration.PluginFactory` (class)
- **Lines (at detection time)**: L20–L100
- **Severity**: medium
- **Confidence**: detected by 2 scan(s)

**Description.** The RubyIntegration.PluginFactory interface combines methods for building different types of plugins.

**Reasoning.** The `RubyIntegration.PluginFactory` interface defines methods for building various types of plugins (`buildInput`, `buildOutput`, `buildFilter`, `buildCodec`) as well as specific codec-related methods (`buildDefaultCodec`, `buildRubyCodecWrapper`). A client that only needs to build, for instance, input plugins, is forced to depend on the methods for building output, filter, and codec plugins, which it does not use. This makes the interface less focused and increases the surface area of dependency for clients. The interface could be segregated into more specific factory interfaces, such as `InputPluginFactory`, `OutputPluginFactory`, `FilterPluginFactory`, and `CodecFactory`.

## Obsolete

entity `RubyIntegration.PluginFactory` not found in current source of `logstash-core/src/main/java/org/logstash/plugins/factory/PluginFactoryExt.java` — likely renamed/removed by an earlier refactor

## Diff

*(no diff — patch was not applied)*
