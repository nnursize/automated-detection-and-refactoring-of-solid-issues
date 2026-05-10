# LSP Violation Report: kotlinx-datetime

## Summary
- **Total unique issues**: 3
- **High severity**: 2
- **Medium severity**: 1
- **Low severity**: 0
- **Found by multiple scans**: 1/3

## Issues

### LSP-001 [HIGH] core/common/src/DateTimePeriod.kt — DatePeriod
- **Confidence**: Found in 6 scan(s)
- **Lines**: 443–515
- **Type**: class
- **Description**: DatePeriod inherits from DateTimePeriod but forces time components to be zero, violating the base class contract.
- **Reasoning**: DateTimePeriod is defined as a general period containing both date and time components. DatePeriod, as a subtype, overrides the time component getters (hours, minutes, seconds, nanoseconds) to always return zero. This violates the Liskov Substitution Principle because a consumer expecting a general DateTimePeriod might rely on these properties to represent a non-zero time duration, which DatePeriod cannot fulfill, effectively narrowing the contract of the base class.

### LSP-002 [HIGH] src/main/kotlin/com/payment/processor/PaymentProcessor.kt — PaymentProcessor
- **Confidence**: Found in 1 scan(s)
- **Lines**: 1–20
- **Type**: class
- **Description**: Fat interface forcing subclasses to implement irrelevant payment methods
- **Reasoning**: The PaymentProcessor interface forces implementations like CashPayment or CryptoPayment to implement methods like 'processCreditCard' or 'processRefund', leading to empty overrides or NotImplementedError exceptions, violating the interface segregation aspect of LSP.

### LSP-003 [MEDIUM] src/main/kotlin/com/data/repository/ReadOnlyRepository.kt — MutableRepository
- **Confidence**: Found in 1 scan(s)
- **Lines**: 5–15
- **Type**: class
- **Description**: Subclass violates the contract of a read-only base class by introducing mutation
- **Reasoning**: If a client expects a ReadOnlyRepository, it assumes no state changes. A MutableRepository subclass that exposes write operations breaks the contract of the base type, forcing clients to perform type-checking to ensure safety.
