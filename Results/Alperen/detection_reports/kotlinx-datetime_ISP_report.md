# ISP Violation Report: kotlinx-datetime

## Summary
- **Total unique issues**: 10
- **High severity**: 3
- **Medium severity**: 5
- **Low severity**: 2
- **Found by multiple scans**: 3/10

## Issues

### ISP-001 [MEDIUM] core/common/src/DateTimePeriod.kt — DateTimePeriod
- **Confidence**: Found in 3 scan(s)
- **Lines**: 65–125
- **Type**: class
- **Description**: DateTimePeriod forces implementations to provide both date and time components, even when only one is relevant.
- **Reasoning**: The class defines abstract properties for both date (years, months, days) and time (hours, minutes, seconds, nanoseconds). Subclasses like DatePeriod are forced to implement time-based properties (hours, minutes, etc.) and return zero, violating the principle that clients should not depend on methods they do not use or that are irrelevant to the specific subtype.

### ISP-002 [HIGH] core/common/src/format/DateTimeComponents.kt — DateTimeComponents
- **Confidence**: Found in 3 scan(s)
- **Lines**: 26–500
- **Type**: class
- **Description**: DateTimeComponents is a 'fat' interface/class containing fields for date, time, offset, and timezone, forcing users to depend on all of them.
- **Reasoning**: The class acts as a container for date, time, offset, and timezone fields. Many operations only require a subset of these (e.g., just date or just time). By bundling all these into a single class, any client using this class is forced to depend on the entire structure, even if they only need to format a date or a time.

### ISP-003 [MEDIUM] core/common/src/DateTimePeriod.kt — DatePeriod
- **Confidence**: Found in 2 scan(s)
- **Lines**: 400–440
- **Type**: class
- **Description**: DatePeriod is forced to implement time-based properties inherited from DateTimePeriod that are semantically irrelevant to a date-only period.
- **Reasoning**: Refused Bequest smell -> ISP violation. DatePeriod inherits from DateTimePeriod, which serves as a fat base class combining both date components (years, months, days) and time components (hours, minutes, seconds, nanoseconds). Because of this inheritance, DatePeriod is forced to expose and provide implementations for time-based properties (lines 419-429), even though it is explicitly designed to represent only date-based differences. This forces clients of DatePeriod to depend on an interface that includes irrelevant time-based members, which are hardcoded to return zero to satisfy the base class contract.

### ISP-004 [HIGH] app/src/main/java/com/example/app/ui/MultiFunctionPrinter.kt — IMachine
- **Confidence**: Found in 1 scan(s)
- **Lines**: 3–7
- **Type**: class
- **Description**: Fat interface that bundles multiple unrelated functionalities (print, scan, fax).
- **Reasoning**: The IMachine interface violates the Interface Segregation Principle by grouping printing, scanning, and faxing into a single contract. This forces all implementing classes to provide logic for all three operations, even if the underlying hardware only supports a subset of these features.

### ISP-005 [HIGH] app/src/main/java/com/example/app/ui/MultiFunctionPrinter.kt — OldPrinter
- **Confidence**: Found in 1 scan(s)
- **Lines**: 9–20
- **Type**: class
- **Description**: Class forced to implement methods it does not use or support.
- **Reasoning**: OldPrinter implements the IMachine interface but only provides functional logic for the print method. The scan and fax methods are left with empty 'Not supported' implementations. This violates ISP because the class is forced to depend on and implement methods that it does not use.

### ISP-006 [MEDIUM] src/main/kotlin/com/example/ISP_Violation.kt — Worker
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5–17
- **Type**: class
- **Description**: Worker class implements a broad interface with unrelated methods.
- **Reasoning**: The Worker interface (or abstract class in this case) contains methods for both basic work (work()) and complex management tasks (manageProject(), assignTask()). A simple worker might only need to perform basic tasks, but is forced to inherit or implement the management methods, violating ISP. This could be split into a 'BasicWorker' and a 'Manager' interface.

### ISP-007 [MEDIUM] src/main/kotlin/com/example/ISP_Violation.kt — Robot
- **Confidence**: Found in 1 scan(s)
- **Lines**: 20–25
- **Type**: class
- **Description**: Robot class implements methods it cannot perform.
- **Reasoning**: The Robot class implements the Worker interface but has empty implementations for 'manageProject()' and 'assignTask()'. This indicates that the Robot does not need these methods, but is forced to implement them due to the broad nature of the Worker interface, violating ISP.

### ISP-008 [LOW] src/main/kotlin/com/example/ISP_Violation.kt — HumanWorker
- **Confidence**: Found in 1 scan(s)
- **Lines**: 28–34
- **Type**: class
- **Description**: HumanWorker implements all methods, but some might be less relevant.
- **Reasoning**: While HumanWorker implements all methods, the management methods (manageProject, assignTask) might not be the primary responsibility of every human worker. If there were a significant number of human workers who never manage projects, this could be considered a minor ISP violation. However, it's less severe than the Robot example as the methods are conceptually applicable.

### ISP-009 [MEDIUM] src/main/kotlin/com/example/ISPExample.kt — Worker
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1–21
- **Type**: class
- **Description**: Worker class implements a single interface with methods for both basic and advanced tasks, forcing all workers to have methods they may not need.
- **Reasoning**: The `Work` interface contains methods for both `work()` and `manage()`. A class like `RobotWorker` might only be capable of `work()` and not `manage()`. By implementing `Work`, it's forced to either provide an empty implementation or throw `NotImplementedError` for `manage()`, violating ISP. This could be segregated into `BasicWorker` and `Manager` interfaces.

### ISP-010 [LOW] src/main/kotlin/com/example/ISPExample.kt — RobotWorker
- **Confidence**: Found in 1 scan(s)
- **Lines**: 23–30
- **Type**: class
- **Description**: RobotWorker implements the Work interface but does not implement the manage method, indicating it does not use that part of the interface.
- **Reasoning**: The `RobotWorker` class implements the `Work` interface but explicitly does not implement the `manage()` method, which is expected to throw `NotImplementedError`. This indicates that the `RobotWorker` client does not need the functionality provided by the `manage()` method, but it is still forced to acknowledge its existence through the interface contract. This suggests the `Work` interface is too broad for clients like `RobotWorker`.
