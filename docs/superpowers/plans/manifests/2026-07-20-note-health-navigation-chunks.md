# note-health 导航实施分块

> 每块涉及的唯一 tracked 文件不超过 25。文件可以跨块重复，但同一模块的块必须顺序执行。

## NAV-01: 01.java / collection
- Defects: 8
- Unique files: 7
- Files:
  - `note/01.java/collection/ArrayList/README.md`
  - `note/01.java/collection/ConcurrentHashMap/README.md`
  - `note/01.java/collection/LinkedHashSet/README.md`
  - `note/01.java/collection/LinkedList/README.md`
  - `note/01.java/collection/README.md`
  - `note/01.java/collection/TreeMap/README.md`
  - `note/01.java/collection/WeakHashMap/README.md`
- Defect rows:
  - `one-way: note/01.java/collection/ArrayList/README.md`
  - `one-way: note/01.java/collection/ConcurrentHashMap/README.md`
  - `one-way: note/01.java/collection/LinkedHashSet/README.md`
  - `orphan: note/01.java/collection/LinkedHashSet/README.md`
  - `one-way: note/01.java/collection/LinkedList/README.md`
  - `one-way: note/01.java/collection/TreeMap/README.md`
  - `one-way: note/01.java/collection/WeakHashMap/README.md`
  - `orphan: note/01.java/collection/WeakHashMap/README.md`

## NAV-02: 01.java / concepts
- Defects: 1
- Unique files: 2
- Files:
  - `note/01.java/concepts/README.md`
  - `note/01.java/concepts/date-time/README.md`
- Defect rows:
  - `one-way: note/01.java/concepts/date-time/README.md`

## NAV-03: 01.java / concurrency
- Defects: 11
- Unique files: 8
- Files:
  - `note/01.java/concurrency/README.md`
  - `note/01.java/concurrency/concurrent-collections/README.md`
  - `note/01.java/concurrency/concurrent-collections/copy-on-write/README.md`
  - `note/01.java/concurrency/concurrent-collections/queue/README.md`
  - `note/01.java/concurrency/concurrent-collections/skip-list/README.md`
  - `note/01.java/concurrency/juc-locks/README.md`
  - `note/01.java/concurrency/thread-basics/README.md`
  - `note/01.java/concurrency/utilities/README.md`
- Defect rows:
  - `invalid-return: note/01.java/concurrency/concurrent-collections/README.md`
  - `self-return: note/01.java/concurrency/concurrent-collections/README.md`
  - `invalid-return: note/01.java/concurrency/concurrent-collections/copy-on-write/README.md`
  - `self-return: note/01.java/concurrency/concurrent-collections/copy-on-write/README.md`
  - `invalid-return: note/01.java/concurrency/concurrent-collections/queue/README.md`
  - `self-return: note/01.java/concurrency/concurrent-collections/queue/README.md`
  - `invalid-return: note/01.java/concurrency/concurrent-collections/skip-list/README.md`
  - `self-return: note/01.java/concurrency/concurrent-collections/skip-list/README.md`
  - `one-way: note/01.java/concurrency/juc-locks/README.md`
  - `one-way: note/01.java/concurrency/thread-basics/README.md`
  - `one-way: note/01.java/concurrency/utilities/README.md`

## NAV-04: 01.java / design-patterns
- Defects: 6
- Unique files: 4
- Files:
  - `note/01.java/design-patterns/README.md`
  - `note/01.java/design-patterns/behavioral/README.md`
  - `note/01.java/design-patterns/creation/README.md`
  - `note/01.java/design-patterns/structural/README.md`
- Defect rows:
  - `invalid-return: note/01.java/design-patterns/behavioral/README.md`
  - `self-return: note/01.java/design-patterns/behavioral/README.md`
  - `invalid-return: note/01.java/design-patterns/creation/README.md`
  - `self-return: note/01.java/design-patterns/creation/README.md`
  - `invalid-return: note/01.java/design-patterns/structural/README.md`
  - `self-return: note/01.java/design-patterns/structural/README.md`

## NAV-05: 01.java / io
- Defects: 3
- Unique files: 3
- Files:
  - `note/01.java/io/README.md`
  - `note/01.java/io/nio/README.md`
  - `note/01.java/io/zero-copy/README.md`
- Defect rows:
  - `one-way: note/01.java/io/nio/README.md`
  - `one-way: note/01.java/io/zero-copy/README.md`
  - `orphan: note/01.java/io/zero-copy/README.md`

## NAV-06: 02.computer-basics / 01-network
- Defects: 14
- Unique files: 9
- Files:
  - `note/02.computer-basics/01-network/01-tcp-ip/README.md`
  - `note/02.computer-basics/01-network/02-http/README.md`
  - `note/02.computer-basics/01-network/03-dns/README.md`
  - `note/02.computer-basics/01-network/04-https-tls/README.md`
  - `note/02.computer-basics/01-network/README.md`
  - `note/02.computer-basics/01-network/protocols/README.md`
  - `note/02.computer-basics/01-network/protocols/tcp-packet/README.md`
  - `note/02.computer-basics/01-network/wcag/README.md`
  - `note/02.computer-basics/README.md`
- Defect rows:
  - `invalid-return: note/02.computer-basics/01-network/01-tcp-ip/README.md`
  - `wrong-return: note/02.computer-basics/01-network/01-tcp-ip/README.md`
  - `invalid-return: note/02.computer-basics/01-network/02-http/README.md`
  - `wrong-return: note/02.computer-basics/01-network/02-http/README.md`
  - `invalid-return: note/02.computer-basics/01-network/03-dns/README.md`
  - `orphan: note/02.computer-basics/01-network/03-dns/README.md`
  - `wrong-return: note/02.computer-basics/01-network/03-dns/README.md`
  - `invalid-return: note/02.computer-basics/01-network/04-https-tls/README.md`
  - `orphan: note/02.computer-basics/01-network/04-https-tls/README.md`
  - `wrong-return: note/02.computer-basics/01-network/04-https-tls/README.md`
  - `invalid-return: note/02.computer-basics/01-network/protocols/tcp-packet/README.md`
  - `self-return: note/02.computer-basics/01-network/protocols/tcp-packet/README.md`
  - `one-way: note/02.computer-basics/01-network/wcag/README.md`
  - `orphan: note/02.computer-basics/01-network/wcag/README.md`

## NAV-07: 02.computer-basics / 02-algorithms
- Defects: 24
- Unique files: 16
- Files:
  - `note/02.computer-basics/02-algorithms/README.md`
  - `note/02.computer-basics/02-algorithms/clustering/README.md`
  - `note/02.computer-basics/02-algorithms/clustering/k-means/README.md`
  - `note/02.computer-basics/02-algorithms/complexity/README.md`
  - `note/02.computer-basics/02-algorithms/complexity/space-complexity/README.md`
  - `note/02.computer-basics/02-algorithms/complexity/time-complexity/README.md`
  - `note/02.computer-basics/02-algorithms/decision-tree/README.md`
  - `note/02.computer-basics/02-algorithms/dimensionality-reduction/README.md`
  - `note/02.computer-basics/02-algorithms/dimensionality-reduction/pca/README.md`
  - `note/02.computer-basics/02-algorithms/ensemble/README.md`
  - `note/02.computer-basics/02-algorithms/optimization/README.md`
  - `note/02.computer-basics/02-algorithms/optimization/gradient-descent/README.md`
  - `note/02.computer-basics/02-algorithms/search/README.md`
  - `note/02.computer-basics/02-algorithms/search/branch-and-bound/README.md`
  - `note/02.computer-basics/02-algorithms/string-algorithms/README.md`
  - `note/02.computer-basics/README.md`
- Defect rows:
  - `one-way: note/02.computer-basics/02-algorithms/clustering/README.md`
  - `invalid-return: note/02.computer-basics/02-algorithms/clustering/k-means/README.md`
  - `wrong-return: note/02.computer-basics/02-algorithms/clustering/k-means/README.md`
  - `invalid-return: note/02.computer-basics/02-algorithms/complexity/space-complexity/README.md`
  - `self-return: note/02.computer-basics/02-algorithms/complexity/space-complexity/README.md`
  - `invalid-return: note/02.computer-basics/02-algorithms/complexity/time-complexity/README.md`
  - `self-return: note/02.computer-basics/02-algorithms/complexity/time-complexity/README.md`
  - `one-way: note/02.computer-basics/02-algorithms/decision-tree/README.md`
  - `wrong-return: note/02.computer-basics/02-algorithms/decision-tree/README.md`
  - `one-way: note/02.computer-basics/02-algorithms/dimensionality-reduction/README.md`
  - `invalid-return: note/02.computer-basics/02-algorithms/dimensionality-reduction/pca/README.md`
  - `wrong-return: note/02.computer-basics/02-algorithms/dimensionality-reduction/pca/README.md`
  - `one-way: note/02.computer-basics/02-algorithms/ensemble/README.md`
  - `orphan: note/02.computer-basics/02-algorithms/ensemble/README.md`
  - `wrong-return: note/02.computer-basics/02-algorithms/ensemble/README.md`
  - `one-way: note/02.computer-basics/02-algorithms/optimization/README.md`
  - `invalid-return: note/02.computer-basics/02-algorithms/optimization/gradient-descent/README.md`
  - `wrong-return: note/02.computer-basics/02-algorithms/optimization/gradient-descent/README.md`
  - `one-way: note/02.computer-basics/02-algorithms/search/README.md`
  - `wrong-return: note/02.computer-basics/02-algorithms/search/README.md`
  - `invalid-return: note/02.computer-basics/02-algorithms/search/branch-and-bound/README.md`
  - `wrong-return: note/02.computer-basics/02-algorithms/search/branch-and-bound/README.md`
  - `invalid-return: note/02.computer-basics/02-algorithms/string-algorithms/README.md`
  - `wrong-return: note/02.computer-basics/02-algorithms/string-algorithms/README.md`

## NAV-08: 03.database / README.md
- Defects: 1
- Unique files: 1
- Files:
  - `note/03.database/README.md`
- Defect rows:
  - `broken: note/03.database/README.md`

## NAV-09: 04.system-design / 01-foundation
- Defects: 28
- Unique files: 20
- Files:
  - `note/04.system-design/01-foundation/02-evolution/01-monolith-to-microservices/README.md`
  - `note/04.system-design/01-foundation/02-evolution/02-serverless-architecture/README.md`
  - `note/04.system-design/01-foundation/02-evolution/README.md`
  - `note/04.system-design/01-foundation/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/api/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/archimate/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/architecture-diagram/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/architecture-evolution/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/eda-vs-async/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/it4it/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/microservices/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/microservices/data-consistency/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/microservices/migration-and-organization/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/microservices/service-communication/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/microservices/service-contract/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/microservices/service-decomposition/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/ood/README.md`
  - `note/04.system-design/01-foundation/system-design-basics/togaf/README.md`
  - `note/04.system-design/README.md`
- Defect rows:
  - `one-way: note/04.system-design/01-foundation/02-evolution/01-monolith-to-microservices/README.md`
  - `one-way: note/04.system-design/01-foundation/02-evolution/02-serverless-architecture/README.md`
  - `orphan: note/04.system-design/01-foundation/02-evolution/02-serverless-architecture/README.md`
  - `invalid-return: note/04.system-design/01-foundation/02-evolution/README.md`
  - `wrong-return: note/04.system-design/01-foundation/02-evolution/README.md`
  - `invalid-return: note/04.system-design/01-foundation/system-design-basics/api/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/api/README.md`
  - `invalid-return: note/04.system-design/01-foundation/system-design-basics/archimate/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/archimate/README.md`
  - `invalid-return: note/04.system-design/01-foundation/system-design-basics/architecture-diagram/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/architecture-diagram/README.md`
  - `invalid-return: note/04.system-design/01-foundation/system-design-basics/architecture-evolution/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/architecture-evolution/README.md`
  - `invalid-return: note/04.system-design/01-foundation/system-design-basics/eda-vs-async/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/eda-vs-async/README.md`
  - `invalid-return: note/04.system-design/01-foundation/system-design-basics/it4it/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/it4it/README.md`
  - `invalid-return: note/04.system-design/01-foundation/system-design-basics/microservices/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/microservices/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/microservices/data-consistency/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/microservices/migration-and-organization/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/microservices/service-communication/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/microservices/service-contract/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/microservices/service-decomposition/README.md`
  - `invalid-return: note/04.system-design/01-foundation/system-design-basics/ood/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/ood/README.md`
  - `invalid-return: note/04.system-design/01-foundation/system-design-basics/togaf/README.md`
  - `self-return: note/04.system-design/01-foundation/system-design-basics/togaf/README.md`

## NAV-10: 04.system-design / 02-distributed
- Defects: 20
- Unique files: 14
- Files:
  - `note/04.system-design/02-distributed/README.md`
  - `note/04.system-design/02-distributed/api-gateway/README.md`
  - `note/04.system-design/02-distributed/cap-and-base/README.md`
  - `note/04.system-design/02-distributed/cap-and-base/base/README.md`
  - `note/04.system-design/02-distributed/cap-and-base/cap/README.md`
  - `note/04.system-design/02-distributed/distributed-cache/README.md`
  - `note/04.system-design/02-distributed/distributed-id/README.md`
  - `note/04.system-design/02-distributed/distributed-id/uuid/README.md`
  - `note/04.system-design/02-distributed/distributed-lock/README.md`
  - `note/04.system-design/02-distributed/distributed-transaction/README.md`
  - `note/04.system-design/02-distributed/rpc/README.md`
  - `note/04.system-design/02-distributed/rpc/apache-dubbo/README.md`
  - `note/04.system-design/02-distributed/rpc/rpc-and-rest/README.md`
  - `note/04.system-design/02-distributed/service-discovery/README.md`
- Defect rows:
  - `invalid-return: note/04.system-design/02-distributed/api-gateway/README.md`
  - `self-return: note/04.system-design/02-distributed/api-gateway/README.md`
  - `one-way: note/04.system-design/02-distributed/cap-and-base/README.md`
  - `self-return: note/04.system-design/02-distributed/cap-and-base/README.md`
  - `invalid-return: note/04.system-design/02-distributed/cap-and-base/base/README.md`
  - `self-return: note/04.system-design/02-distributed/cap-and-base/base/README.md`
  - `invalid-return: note/04.system-design/02-distributed/cap-and-base/cap/README.md`
  - `self-return: note/04.system-design/02-distributed/cap-and-base/cap/README.md`
  - `invalid-return: note/04.system-design/02-distributed/distributed-cache/README.md`
  - `self-return: note/04.system-design/02-distributed/distributed-cache/README.md`
  - `one-way: note/04.system-design/02-distributed/distributed-id/uuid/README.md`
  - `invalid-return: note/04.system-design/02-distributed/distributed-lock/README.md`
  - `self-return: note/04.system-design/02-distributed/distributed-lock/README.md`
  - `invalid-return: note/04.system-design/02-distributed/distributed-transaction/README.md`
  - `self-return: note/04.system-design/02-distributed/distributed-transaction/README.md`
  - `one-way: note/04.system-design/02-distributed/rpc/apache-dubbo/README.md`
  - `invalid-return: note/04.system-design/02-distributed/rpc/rpc-and-rest/README.md`
  - `self-return: note/04.system-design/02-distributed/rpc/rpc-and-rest/README.md`
  - `invalid-return: note/04.system-design/02-distributed/service-discovery/README.md`
  - `self-return: note/04.system-design/02-distributed/service-discovery/README.md`

## NAV-11: 04.system-design / 03-high-availability
- Defects: 14
- Unique files: 12
- Files:
  - `note/04.system-design/03-high-availability/README.md`
  - `note/04.system-design/03-high-availability/circuit-break/README.md`
  - `note/04.system-design/03-high-availability/code-quality/2-lines-8-lines/README.md`
  - `note/04.system-design/03-high-availability/code-quality/README.md`
  - `note/04.system-design/03-high-availability/rate-limiting/README.md`
  - `note/04.system-design/03-high-availability/rate-limiting/seckill-without-redis.md`
  - `note/04.system-design/03-high-availability/redundancy-design/README.md`
  - `note/04.system-design/03-high-availability/redundancy-design/cluster/README.md`
  - `note/04.system-design/03-high-availability/redundancy-design/multi-site-active-active/README.md`
  - `note/04.system-design/03-high-availability/retry/README.md`
  - `note/04.system-design/03-high-availability/service-degradation/README.md`
  - `note/04.system-design/03-high-availability/timeout/README.md`
- Defect rows:
  - `invalid-return: note/04.system-design/03-high-availability/circuit-break/README.md`
  - `self-return: note/04.system-design/03-high-availability/circuit-break/README.md`
  - `one-way: note/04.system-design/03-high-availability/code-quality/2-lines-8-lines/README.md`
  - `invalid-return: note/04.system-design/03-high-availability/rate-limiting/README.md`
  - `self-return: note/04.system-design/03-high-availability/rate-limiting/README.md`
  - `one-way: note/04.system-design/03-high-availability/rate-limiting/seckill-without-redis.md`
  - `one-way: note/04.system-design/03-high-availability/redundancy-design/cluster/README.md`
  - `one-way: note/04.system-design/03-high-availability/redundancy-design/multi-site-active-active/README.md`
  - `invalid-return: note/04.system-design/03-high-availability/retry/README.md`
  - `self-return: note/04.system-design/03-high-availability/retry/README.md`
  - `invalid-return: note/04.system-design/03-high-availability/service-degradation/README.md`
  - `self-return: note/04.system-design/03-high-availability/service-degradation/README.md`
  - `invalid-return: note/04.system-design/03-high-availability/timeout/README.md`
  - `self-return: note/04.system-design/03-high-availability/timeout/README.md`

## NAV-12: 04.system-design / 04-high-performance
- Defects: 17
- Unique files: 10
- Files:
  - `note/04.system-design/04-high-performance/README.md`
  - `note/04.system-design/04-high-performance/cache-patterns/README.md`
  - `note/04.system-design/04-high-performance/cdn/README.md`
  - `note/04.system-design/04-high-performance/connection-pool/README.md`
  - `note/04.system-design/04-high-performance/database-optimization/README.md`
  - `note/04.system-design/04-high-performance/database-optimization/db-sharding/README.md`
  - `note/04.system-design/04-high-performance/database-optimization/db-sharding/sharding-sphere/README.md`
  - `note/04.system-design/04-high-performance/java/README.md`
  - `note/04.system-design/04-high-performance/load-balance/README.md`
  - `note/04.system-design/04-high-performance/serialization/README.md`
- Defect rows:
  - `invalid-return: note/04.system-design/04-high-performance/cache-patterns/README.md`
  - `self-return: note/04.system-design/04-high-performance/cache-patterns/README.md`
  - `invalid-return: note/04.system-design/04-high-performance/cdn/README.md`
  - `self-return: note/04.system-design/04-high-performance/cdn/README.md`
  - `invalid-return: note/04.system-design/04-high-performance/connection-pool/README.md`
  - `self-return: note/04.system-design/04-high-performance/connection-pool/README.md`
  - `invalid-return: note/04.system-design/04-high-performance/database-optimization/README.md`
  - `self-return: note/04.system-design/04-high-performance/database-optimization/README.md`
  - `invalid-return: note/04.system-design/04-high-performance/database-optimization/db-sharding/README.md`
  - `self-return: note/04.system-design/04-high-performance/database-optimization/db-sharding/README.md`
  - `one-way: note/04.system-design/04-high-performance/database-optimization/db-sharding/sharding-sphere/README.md`
  - `invalid-return: note/04.system-design/04-high-performance/java/README.md`
  - `self-return: note/04.system-design/04-high-performance/java/README.md`
  - `invalid-return: note/04.system-design/04-high-performance/load-balance/README.md`
  - `self-return: note/04.system-design/04-high-performance/load-balance/README.md`
  - `invalid-return: note/04.system-design/04-high-performance/serialization/README.md`
  - `self-return: note/04.system-design/04-high-performance/serialization/README.md`

## NAV-13: 04.system-design / 05-security
- Defects: 14
- Unique files: 8
- Files:
  - `note/04.system-design/05-security/README.md`
  - `note/04.system-design/05-security/access-control/01-traditional/README.md`
  - `note/04.system-design/05-security/access-control/02-role-and-attribute/README.md`
  - `note/04.system-design/05-security/access-control/03-relationship-and-hybrid/README.md`
  - `note/04.system-design/05-security/access-control/README.md`
  - `note/04.system-design/05-security/api-security/README.md`
  - `note/04.system-design/05-security/jwt-security/README.md`
  - `note/04.system-design/05-security/oauth2-oidc/README.md`
- Defect rows:
  - `invalid-return: note/04.system-design/05-security/access-control/01-traditional/README.md`
  - `self-return: note/04.system-design/05-security/access-control/01-traditional/README.md`
  - `invalid-return: note/04.system-design/05-security/access-control/02-role-and-attribute/README.md`
  - `self-return: note/04.system-design/05-security/access-control/02-role-and-attribute/README.md`
  - `invalid-return: note/04.system-design/05-security/access-control/03-relationship-and-hybrid/README.md`
  - `self-return: note/04.system-design/05-security/access-control/03-relationship-and-hybrid/README.md`
  - `invalid-return: note/04.system-design/05-security/access-control/README.md`
  - `self-return: note/04.system-design/05-security/access-control/README.md`
  - `invalid-return: note/04.system-design/05-security/api-security/README.md`
  - `self-return: note/04.system-design/05-security/api-security/README.md`
  - `invalid-return: note/04.system-design/05-security/jwt-security/README.md`
  - `self-return: note/04.system-design/05-security/jwt-security/README.md`
  - `invalid-return: note/04.system-design/05-security/oauth2-oidc/README.md`
  - `self-return: note/04.system-design/05-security/oauth2-oidc/README.md`

## NAV-14: 04.system-design / 06-idempotency
- Defects: 10
- Unique files: 6
- Files:
  - `note/04.system-design/06-idempotency/README.md`
  - `note/04.system-design/06-idempotency/deduplication-table/README.md`
  - `note/04.system-design/06-idempotency/idempotency-key/README.md`
  - `note/04.system-design/06-idempotency/optimistic-lock/README.md`
  - `note/04.system-design/06-idempotency/state-machine/README.md`
  - `note/04.system-design/06-idempotency/vs-distributed-transaction/README.md`
- Defect rows:
  - `invalid-return: note/04.system-design/06-idempotency/deduplication-table/README.md`
  - `self-return: note/04.system-design/06-idempotency/deduplication-table/README.md`
  - `invalid-return: note/04.system-design/06-idempotency/idempotency-key/README.md`
  - `self-return: note/04.system-design/06-idempotency/idempotency-key/README.md`
  - `invalid-return: note/04.system-design/06-idempotency/optimistic-lock/README.md`
  - `self-return: note/04.system-design/06-idempotency/optimistic-lock/README.md`
  - `invalid-return: note/04.system-design/06-idempotency/state-machine/README.md`
  - `self-return: note/04.system-design/06-idempotency/state-machine/README.md`
  - `invalid-return: note/04.system-design/06-idempotency/vs-distributed-transaction/README.md`
  - `self-return: note/04.system-design/06-idempotency/vs-distributed-transaction/README.md`

## NAV-15: 04.system-design / 07-deployment
- Defects: 6
- Unique files: 4
- Files:
  - `note/04.system-design/07-deployment/README.md`
  - `note/04.system-design/07-deployment/capacity-planning/README.md`
  - `note/04.system-design/07-deployment/deploy/README.md`
  - `note/04.system-design/07-deployment/observability/README.md`
- Defect rows:
  - `invalid-return: note/04.system-design/07-deployment/capacity-planning/README.md`
  - `self-return: note/04.system-design/07-deployment/capacity-planning/README.md`
  - `invalid-return: note/04.system-design/07-deployment/deploy/README.md`
  - `self-return: note/04.system-design/07-deployment/deploy/README.md`
  - `invalid-return: note/04.system-design/07-deployment/observability/README.md`
  - `self-return: note/04.system-design/07-deployment/observability/README.md`

## NAV-16: 04.system-design / 09-emerging-tech
- Defects: 8
- Unique files: 6
- Files:
  - `note/04.system-design/09-emerging-tech/01-ebpf/README.md`
  - `note/04.system-design/09-emerging-tech/02-wasm/README.md`
  - `note/04.system-design/09-emerging-tech/03-service-mesh-deep/README.md`
  - `note/04.system-design/09-emerging-tech/04-cloud-native-trends/README.md`
  - `note/04.system-design/09-emerging-tech/README.md`
  - `note/04.system-design/README.md`
- Defect rows:
  - `invalid-return: note/04.system-design/09-emerging-tech/01-ebpf/README.md`
  - `wrong-return: note/04.system-design/09-emerging-tech/01-ebpf/README.md`
  - `invalid-return: note/04.system-design/09-emerging-tech/02-wasm/README.md`
  - `wrong-return: note/04.system-design/09-emerging-tech/02-wasm/README.md`
  - `invalid-return: note/04.system-design/09-emerging-tech/03-service-mesh-deep/README.md`
  - `wrong-return: note/04.system-design/09-emerging-tech/03-service-mesh-deep/README.md`
  - `invalid-return: note/04.system-design/09-emerging-tech/04-cloud-native-trends/README.md`
  - `wrong-return: note/04.system-design/09-emerging-tech/04-cloud-native-trends/README.md`

## NAV-17: 05.tools / 02-docker
- Defects: 2
- Unique files: 2
- Files:
  - `note/05.tools/02-docker/README.md`
  - `note/05.tools/02-docker/docker-compose/README.md`
- Defect rows:
  - `invalid-return: note/05.tools/02-docker/docker-compose/README.md`
  - `self-return: note/05.tools/02-docker/docker-compose/README.md`

## NAV-18: 05.tools / 04-nginx
- Defects: 1
- Unique files: 1
- Files:
  - `note/05.tools/04-nginx/README.md`
- Defect rows:
  - `broken: note/05.tools/04-nginx/README.md`

## NAV-19: 05.tools / 05-monorepo
- Defects: 1
- Unique files: 1
- Files:
  - `note/05.tools/05-monorepo/README.md`
- Defect rows:
  - `broken: note/05.tools/05-monorepo/README.md`

## NAV-20: 05.tools / 06-ali-microservices
- Defects: 1
- Unique files: 1
- Files:
  - `note/05.tools/06-ali-microservices/README.md`
- Defect rows:
  - `broken: note/05.tools/06-ali-microservices/README.md`

## NAV-21: 06.spring / 01-core
- Defects: 4
- Unique files: 4
- Files:
  - `note/06.spring/01-core/README.md`
  - `note/06.spring/01-core/aop/README.md`
  - `note/06.spring/01-core/ioc/README.md`
  - `note/06.spring/01-core/minispring/README.md`
- Defect rows:
  - `self-return: note/06.spring/01-core/aop/README.md`
  - `self-return: note/06.spring/01-core/ioc/README.md`
  - `invalid-return: note/06.spring/01-core/minispring/README.md`
  - `self-return: note/06.spring/01-core/minispring/README.md`

## NAV-22: 06.spring / 02-web
- Defects: 2
- Unique files: 3
- Files:
  - `note/06.spring/02-web/README.md`
  - `note/06.spring/02-web/mvc/README.md`
  - `note/06.spring/02-web/webflux/README.md`
- Defect rows:
  - `self-return: note/06.spring/02-web/mvc/README.md`
  - `self-return: note/06.spring/02-web/webflux/README.md`

## NAV-23: 06.spring / 03-data
- Defects: 5
- Unique files: 6
- Files:
  - `note/06.spring/03-data/README.md`
  - `note/06.spring/03-data/cache/README.md`
  - `note/06.spring/03-data/mybatis/03-spring-integration/README.md`
  - `note/06.spring/03-data/mybatis/README.md`
  - `note/06.spring/03-data/transaction/README.md`
  - `note/06.spring/03-data/transaction/distributed/README.md`
- Defect rows:
  - `self-return: note/06.spring/03-data/cache/README.md`
  - `self-return: note/06.spring/03-data/mybatis/03-spring-integration/README.md`
  - `self-return: note/06.spring/03-data/transaction/README.md`
  - `one-way: note/06.spring/03-data/transaction/distributed/README.md`
  - `wrong-return: note/06.spring/03-data/transaction/distributed/README.md`

## NAV-24: 06.spring / 05-spring-cloud
- Defects: 2
- Unique files: 2
- Files:
  - `note/06.spring/05-spring-cloud/README.md`
  - `note/06.spring/05-spring-cloud/service-registry/README.md`
- Defect rows:
  - `invalid-return: note/06.spring/05-spring-cloud/service-registry/README.md`
  - `self-return: note/06.spring/05-spring-cloud/service-registry/README.md`

## NAV-25: 06.spring / 06-integration
- Defects: 2
- Unique files: 2
- Files:
  - `note/06.spring/06-integration/README.md`
  - `note/06.spring/06-integration/validation/README.md`
- Defect rows:
  - `invalid-return: note/06.spring/06-integration/validation/README.md`
  - `self-return: note/06.spring/06-integration/validation/README.md`

## NAV-26: 07.workflow / apache-eventmesh
- Defects: 3
- Unique files: 3
- Files:
  - `note/07.workflow/apache-eventmesh/README.md`
  - `note/07.workflow/apache-eventmesh/cloud-flow/README.md`
  - `note/README.md`
- Defect rows:
  - `invalid-return: note/07.workflow/apache-eventmesh/cloud-flow/README.md`
  - `orphan: note/07.workflow/apache-eventmesh/cloud-flow/README.md`
  - `wrong-return: note/07.workflow/apache-eventmesh/cloud-flow/README.md`

## NAV-27: 07.workflow / define
- Defects: 1
- Unique files: 2
- Files:
  - `note/07.workflow/README.md`
  - `note/07.workflow/define/README.md`
- Defect rows:
  - `self-return: note/07.workflow/define/README.md`

## NAV-28: 07.workflow / process-engine
- Defects: 9
- Unique files: 6
- Files:
  - `note/07.workflow/README.md`
  - `note/07.workflow/process-engine/README.md`
  - `note/07.workflow/process-engine/camunda/README.md`
  - `note/07.workflow/process-engine/camunda/camunda-7/README.md`
  - `note/07.workflow/process-engine/camunda/camunda-8/README.md`
  - `note/07.workflow/process-engine/camunda/camunda-8/zeebe/README.md`
- Defect rows:
  - `self-return: note/07.workflow/process-engine/README.md`
  - `invalid-return: note/07.workflow/process-engine/camunda/README.md`
  - `wrong-return: note/07.workflow/process-engine/camunda/README.md`
  - `invalid-return: note/07.workflow/process-engine/camunda/camunda-7/README.md`
  - `wrong-return: note/07.workflow/process-engine/camunda/camunda-7/README.md`
  - `invalid-return: note/07.workflow/process-engine/camunda/camunda-8/README.md`
  - `wrong-return: note/07.workflow/process-engine/camunda/camunda-8/README.md`
  - `invalid-return: note/07.workflow/process-engine/camunda/camunda-8/zeebe/README.md`
  - `wrong-return: note/07.workflow/process-engine/camunda/camunda-8/zeebe/README.md`

## NAV-29: 08.application-systems / 01-rd-innovation
- Defects: 6
- Unique files: 5
- Files:
  - `note/08.application-systems/01-rd-innovation/README.md`
  - `note/08.application-systems/01-rd-innovation/cms/README.md`
  - `note/08.application-systems/01-rd-innovation/pdm/README.md`
  - `note/08.application-systems/01-rd-innovation/plm/README.md`
  - `note/08.application-systems/README.md`
- Defect rows:
  - `invalid-return: note/08.application-systems/01-rd-innovation/cms/README.md`
  - `wrong-return: note/08.application-systems/01-rd-innovation/cms/README.md`
  - `invalid-return: note/08.application-systems/01-rd-innovation/pdm/README.md`
  - `wrong-return: note/08.application-systems/01-rd-innovation/pdm/README.md`
  - `invalid-return: note/08.application-systems/01-rd-innovation/plm/README.md`
  - `wrong-return: note/08.application-systems/01-rd-innovation/plm/README.md`

## NAV-30: 08.application-systems / 02-production
- Defects: 8
- Unique files: 6
- Files:
  - `note/08.application-systems/02-production/README.md`
  - `note/08.application-systems/02-production/aps/README.md`
  - `note/08.application-systems/02-production/mes/README.md`
  - `note/08.application-systems/02-production/mom/README.md`
  - `note/08.application-systems/02-production/scada/README.md`
  - `note/08.application-systems/README.md`
- Defect rows:
  - `invalid-return: note/08.application-systems/02-production/aps/README.md`
  - `wrong-return: note/08.application-systems/02-production/aps/README.md`
  - `invalid-return: note/08.application-systems/02-production/mes/README.md`
  - `wrong-return: note/08.application-systems/02-production/mes/README.md`
  - `invalid-return: note/08.application-systems/02-production/mom/README.md`
  - `wrong-return: note/08.application-systems/02-production/mom/README.md`
  - `invalid-return: note/08.application-systems/02-production/scada/README.md`
  - `wrong-return: note/08.application-systems/02-production/scada/README.md`

## NAV-31: 08.application-systems / 03-supply-chain
- Defects: 8
- Unique files: 6
- Files:
  - `note/08.application-systems/03-supply-chain/README.md`
  - `note/08.application-systems/03-supply-chain/scm/README.md`
  - `note/08.application-systems/03-supply-chain/srm/README.md`
  - `note/08.application-systems/03-supply-chain/tms/README.md`
  - `note/08.application-systems/03-supply-chain/wms/README.md`
  - `note/08.application-systems/README.md`
- Defect rows:
  - `invalid-return: note/08.application-systems/03-supply-chain/scm/README.md`
  - `wrong-return: note/08.application-systems/03-supply-chain/scm/README.md`
  - `invalid-return: note/08.application-systems/03-supply-chain/srm/README.md`
  - `wrong-return: note/08.application-systems/03-supply-chain/srm/README.md`
  - `invalid-return: note/08.application-systems/03-supply-chain/tms/README.md`
  - `wrong-return: note/08.application-systems/03-supply-chain/tms/README.md`
  - `invalid-return: note/08.application-systems/03-supply-chain/wms/README.md`
  - `wrong-return: note/08.application-systems/03-supply-chain/wms/README.md`

## NAV-32: 08.application-systems / 04-sales-service
- Defects: 6
- Unique files: 5
- Files:
  - `note/08.application-systems/04-sales-service/README.md`
  - `note/08.application-systems/04-sales-service/crm/README.md`
  - `note/08.application-systems/04-sales-service/oms/README.md`
  - `note/08.application-systems/04-sales-service/scrm/README.md`
  - `note/08.application-systems/README.md`
- Defect rows:
  - `invalid-return: note/08.application-systems/04-sales-service/crm/README.md`
  - `wrong-return: note/08.application-systems/04-sales-service/crm/README.md`
  - `invalid-return: note/08.application-systems/04-sales-service/oms/README.md`
  - `wrong-return: note/08.application-systems/04-sales-service/oms/README.md`
  - `invalid-return: note/08.application-systems/04-sales-service/scrm/README.md`
  - `wrong-return: note/08.application-systems/04-sales-service/scrm/README.md`

## NAV-33: 08.application-systems / 05-operations
- Defects: 10
- Unique files: 7
- Files:
  - `note/08.application-systems/05-operations/README.md`
  - `note/08.application-systems/05-operations/bi/README.md`
  - `note/08.application-systems/05-operations/eam/README.md`
  - `note/08.application-systems/05-operations/erp/README.md`
  - `note/08.application-systems/05-operations/oa/README.md`
  - `note/08.application-systems/05-operations/qms/README.md`
  - `note/08.application-systems/README.md`
- Defect rows:
  - `invalid-return: note/08.application-systems/05-operations/bi/README.md`
  - `wrong-return: note/08.application-systems/05-operations/bi/README.md`
  - `invalid-return: note/08.application-systems/05-operations/eam/README.md`
  - `wrong-return: note/08.application-systems/05-operations/eam/README.md`
  - `invalid-return: note/08.application-systems/05-operations/erp/README.md`
  - `wrong-return: note/08.application-systems/05-operations/erp/README.md`
  - `invalid-return: note/08.application-systems/05-operations/oa/README.md`
  - `wrong-return: note/08.application-systems/05-operations/oa/README.md`
  - `invalid-return: note/08.application-systems/05-operations/qms/README.md`
  - `wrong-return: note/08.application-systems/05-operations/qms/README.md`

## NAV-34: 08.application-systems / 06-specialized
- Defects: 4
- Unique files: 4
- Files:
  - `note/08.application-systems/06-specialized/README.md`
  - `note/08.application-systems/06-specialized/lims/README.md`
  - `note/08.application-systems/06-specialized/pms/README.md`
  - `note/08.application-systems/README.md`
- Defect rows:
  - `invalid-return: note/08.application-systems/06-specialized/lims/README.md`
  - `wrong-return: note/08.application-systems/06-specialized/lims/README.md`
  - `invalid-return: note/08.application-systems/06-specialized/pms/README.md`
  - `wrong-return: note/08.application-systems/06-specialized/pms/README.md`

## NAV-35: 09.front-end / 08-cross-platform
- Defects: 2
- Unique files: 2
- Files:
  - `note/09.front-end/08-cross-platform/README.md`
  - `note/09.front-end/08-cross-platform/mobile-tech-stack/README.md`
- Defect rows:
  - `invalid-return: note/09.front-end/08-cross-platform/mobile-tech-stack/README.md`
  - `self-return: note/09.front-end/08-cross-platform/mobile-tech-stack/README.md`

## NAV-36: 10.big-data / 03-realtime-compute
- Defects: 1
- Unique files: 3
- Files:
  - `note/10.big-data/03-realtime-compute/01-flink-vs-spark-streaming/README.md`
  - `note/10.big-data/03-realtime-compute/README.md`
  - `note/README.md`
- Defect rows:
  - `wrong-return: note/10.big-data/03-realtime-compute/01-flink-vs-spark-streaming/README.md`

## NAV-37: 10.big-data / 04-data-lake
- Defects: 1
- Unique files: 3
- Files:
  - `note/10.big-data/04-data-lake/01-iceberg-vs-delta-vs-hudi/README.md`
  - `note/10.big-data/04-data-lake/README.md`
  - `note/README.md`
- Defect rows:
  - `wrong-return: note/10.big-data/04-data-lake/01-iceberg-vs-delta-vs-hudi/README.md`

## NAV-38: 10.big-data / 05-olap
- Defects: 1
- Unique files: 3
- Files:
  - `note/10.big-data/05-olap/01-clickhouse-vs-doris-vs-starrocks/README.md`
  - `note/10.big-data/05-olap/README.md`
  - `note/README.md`
- Defect rows:
  - `wrong-return: note/10.big-data/05-olap/01-clickhouse-vs-doris-vs-starrocks/README.md`

## NAV-39: 11.ai / 01-fundamentals
- Defects: 4
- Unique files: 3
- Files:
  - `note/11.ai/01-fundamentals/README.md`
  - `note/11.ai/01-fundamentals/dropout-in-llm/README.md`
  - `note/11.ai/01-fundamentals/transformer/README.md`
- Defect rows:
  - `invalid-return: note/11.ai/01-fundamentals/dropout-in-llm/README.md`
  - `self-return: note/11.ai/01-fundamentals/dropout-in-llm/README.md`
  - `invalid-return: note/11.ai/01-fundamentals/transformer/README.md`
  - `self-return: note/11.ai/01-fundamentals/transformer/README.md`

## NAV-40: 11.ai / 02-technology-stack
- Defects: 15
- Unique files: 9
- Files:
  - `note/11.ai/02-technology-stack/README.md`
  - `note/11.ai/02-technology-stack/context-engineering/README.md`
  - `note/11.ai/02-technology-stack/function-calling/README.md`
  - `note/11.ai/02-technology-stack/paged-attention/README.md`
  - `note/11.ai/02-technology-stack/prompt-engineering/README.md`
  - `note/11.ai/02-technology-stack/token-billing/README.md`
  - `note/11.ai/02-technology-stack/vector-search-algorithms/README.md`
  - `note/11.ai/02-technology-stack/vector-search-at-scale/README.md`
  - `note/11.ai/02-technology-stack/vector-search-trillion/README.md`
- Defect rows:
  - `invalid-return: note/11.ai/02-technology-stack/context-engineering/README.md`
  - `self-return: note/11.ai/02-technology-stack/context-engineering/README.md`
  - `invalid-return: note/11.ai/02-technology-stack/function-calling/README.md`
  - `self-return: note/11.ai/02-technology-stack/function-calling/README.md`
  - `broken: note/11.ai/02-technology-stack/paged-attention/README.md`
  - `invalid-return: note/11.ai/02-technology-stack/prompt-engineering/README.md`
  - `self-return: note/11.ai/02-technology-stack/prompt-engineering/README.md`
  - `invalid-return: note/11.ai/02-technology-stack/token-billing/README.md`
  - `self-return: note/11.ai/02-technology-stack/token-billing/README.md`
  - `invalid-return: note/11.ai/02-technology-stack/vector-search-algorithms/README.md`
  - `self-return: note/11.ai/02-technology-stack/vector-search-algorithms/README.md`
  - `invalid-return: note/11.ai/02-technology-stack/vector-search-at-scale/README.md`
  - `self-return: note/11.ai/02-technology-stack/vector-search-at-scale/README.md`
  - `invalid-return: note/11.ai/02-technology-stack/vector-search-trillion/README.md`
  - `self-return: note/11.ai/02-technology-stack/vector-search-trillion/README.md`

## NAV-41: 11.ai / 03-engineering
- Defects: 12
- Unique files: 12
- Files:
  - `note/11.ai/03-engineering/README.md`
  - `note/11.ai/03-engineering/agent-spec-tools/README.md`
  - `note/11.ai/03-engineering/ai-platforms/README.md`
  - `note/11.ai/03-engineering/frameworks/README.md`
  - `note/11.ai/03-engineering/frameworks/deep-learning/README.md`
  - `note/11.ai/03-engineering/frameworks/langgraph-migration/README.md`
  - `note/11.ai/03-engineering/frameworks/llm-app/README.md`
  - `note/11.ai/03-engineering/harness-engineering/README.md`
  - `note/11.ai/03-engineering/local-deployment/README.md`
  - `note/11.ai/03-engineering/local-deployment/iflow-cli/README.md`
  - `note/11.ai/03-engineering/local-deployment/linux-deploy/README.md`
  - `note/11.ai/03-engineering/loop-engineering/README.md`
- Defect rows:
  - `invalid-return: note/11.ai/03-engineering/agent-spec-tools/README.md`
  - `self-return: note/11.ai/03-engineering/agent-spec-tools/README.md`
  - `self-return: note/11.ai/03-engineering/ai-platforms/README.md`
  - `one-way: note/11.ai/03-engineering/frameworks/deep-learning/README.md`
  - `one-way: note/11.ai/03-engineering/frameworks/langgraph-migration/README.md`
  - `one-way: note/11.ai/03-engineering/frameworks/llm-app/README.md`
  - `invalid-return: note/11.ai/03-engineering/harness-engineering/README.md`
  - `self-return: note/11.ai/03-engineering/harness-engineering/README.md`
  - `one-way: note/11.ai/03-engineering/local-deployment/iflow-cli/README.md`
  - `one-way: note/11.ai/03-engineering/local-deployment/linux-deploy/README.md`
  - `invalid-return: note/11.ai/03-engineering/loop-engineering/README.md`
  - `self-return: note/11.ai/03-engineering/loop-engineering/README.md`

## NAV-42: 11.ai / 04-architecture
- Defects: 9
- Unique files: 7
- Files:
  - `note/11.ai/04-architecture/README.md`
  - `note/11.ai/04-architecture/agent-architecture/README.md`
  - `note/11.ai/04-architecture/agent-execution-patterns/README.md`
  - `note/11.ai/04-architecture/agent-memory/README.md`
  - `note/11.ai/04-architecture/intelligent-system-layers/README.md`
  - `note/11.ai/04-architecture/intelligent-system-layers/system-three-layers.md`
  - `note/11.ai/04-architecture/llm-control-evolution/README.md`
- Defect rows:
  - `invalid-return: note/11.ai/04-architecture/agent-architecture/README.md`
  - `self-return: note/11.ai/04-architecture/agent-architecture/README.md`
  - `invalid-return: note/11.ai/04-architecture/agent-execution-patterns/README.md`
  - `wrong-return: note/11.ai/04-architecture/agent-execution-patterns/README.md`
  - `invalid-return: note/11.ai/04-architecture/agent-memory/README.md`
  - `self-return: note/11.ai/04-architecture/agent-memory/README.md`
  - `orphan: note/11.ai/04-architecture/intelligent-system-layers/system-three-layers.md`
  - `invalid-return: note/11.ai/04-architecture/llm-control-evolution/README.md`
  - `self-return: note/11.ai/04-architecture/llm-control-evolution/README.md`

## NAV-43: 11.ai / 05-applications
- Defects: 18
- Unique files: 19
- Files:
  - `note/11.ai/05-applications/README.md`
  - `note/11.ai/05-applications/automotive/README.md`
  - `note/11.ai/05-applications/automotive/gan-industrial-design/README.md`
  - `note/11.ai/05-applications/automotive/ml-to-rl/README.md`
  - `note/11.ai/05-applications/automotive/overview/README.md`
  - `note/11.ai/05-applications/automotive/smart-cockpit/README.md`
  - `note/11.ai/05-applications/case-studies/01-anthropic-claude-code/README.md`
  - `note/11.ai/05-applications/case-studies/02-cursor-tab/README.md`
  - `note/11.ai/05-applications/case-studies/03-klarna-ai-customer-service/README.md`
  - `note/11.ai/05-applications/case-studies/04-harvey-ai-legal/README.md`
  - `note/11.ai/05-applications/case-studies/05-khan-academy-khanmigo/README.md`
  - `note/11.ai/05-applications/case-studies/06-duolingo-max/README.md`
  - `note/11.ai/05-applications/case-studies/07-jpmorgan-coin/README.md`
  - `note/11.ai/05-applications/case-studies/08-microsoft-365-copilot/README.md`
  - `note/11.ai/05-applications/case-studies/09-glean-enterprise-search/README.md`
  - `note/11.ai/05-applications/case-studies/10-salesforce-agentforce/README.md`
  - `note/11.ai/05-applications/case-studies/11-hippocratic-ai/README.md`
  - `note/11.ai/05-applications/case-studies/12-siemens-industrial-copilot/README.md`
  - `note/11.ai/05-applications/case-studies/README.md`
- Defect rows:
  - `one-way: note/11.ai/05-applications/automotive/gan-industrial-design/README.md`
  - `one-way: note/11.ai/05-applications/automotive/ml-to-rl/README.md`
  - `one-way: note/11.ai/05-applications/automotive/overview/README.md`
  - `one-way: note/11.ai/05-applications/automotive/smart-cockpit/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/01-anthropic-claude-code/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/02-cursor-tab/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/03-klarna-ai-customer-service/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/04-harvey-ai-legal/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/05-khan-academy-khanmigo/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/06-duolingo-max/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/07-jpmorgan-coin/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/08-microsoft-365-copilot/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/09-glean-enterprise-search/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/10-salesforce-agentforce/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/11-hippocratic-ai/README.md`
  - `one-way: note/11.ai/05-applications/case-studies/12-siemens-industrial-copilot/README.md`
  - `invalid-return: note/11.ai/05-applications/case-studies/README.md`
  - `self-return: note/11.ai/05-applications/case-studies/README.md`

## NAV-44: 11.ai / 07-research
- Defects: 1
- Unique files: 2
- Files:
  - `note/11.ai/07-research/distillation/README.md`
  - `note/11.ai/07-research/distillation/tools/README.md`
- Defect rows:
  - `one-way: note/11.ai/07-research/distillation/tools/README.md`

## NAV-45: 11.ai / 08-llmops
- Defects: 18
- Unique files: 12
- Files:
  - `note/11.ai/08-llmops/01-rag-vs-finetuning/README.md`
  - `note/11.ai/08-llmops/02-llmops-stack/README.md`
  - `note/11.ai/08-llmops/03-vector-db-vs-cache/README.md`
  - `note/11.ai/08-llmops/04-llm-evaluation/README.md`
  - `note/11.ai/08-llmops/05-llm-security/README.md`
  - `note/11.ai/08-llmops/06-rag-out-of-domain-rejection/README.md`
  - `note/11.ai/08-llmops/README.md`
  - `note/11.ai/08-llmops/agent-evaluation/02-ab-testing-design/README.md`
  - `note/11.ai/08-llmops/agent-evaluation/09-rag-evaluation/README.md`
  - `note/11.ai/08-llmops/agent-evaluation/README.md`
  - `note/11.ai/08-llmops/agentic-search-vs-rag/README.md`
  - `note/11.ai/README.md`
- Defect rows:
  - `invalid-return: note/11.ai/08-llmops/01-rag-vs-finetuning/README.md`
  - `wrong-return: note/11.ai/08-llmops/01-rag-vs-finetuning/README.md`
  - `invalid-return: note/11.ai/08-llmops/02-llmops-stack/README.md`
  - `wrong-return: note/11.ai/08-llmops/02-llmops-stack/README.md`
  - `invalid-return: note/11.ai/08-llmops/03-vector-db-vs-cache/README.md`
  - `wrong-return: note/11.ai/08-llmops/03-vector-db-vs-cache/README.md`
  - `invalid-return: note/11.ai/08-llmops/04-llm-evaluation/README.md`
  - `wrong-return: note/11.ai/08-llmops/04-llm-evaluation/README.md`
  - `invalid-return: note/11.ai/08-llmops/05-llm-security/README.md`
  - `wrong-return: note/11.ai/08-llmops/05-llm-security/README.md`
  - `invalid-return: note/11.ai/08-llmops/06-rag-out-of-domain-rejection/README.md`
  - `self-return: note/11.ai/08-llmops/06-rag-out-of-domain-rejection/README.md`
  - `invalid-return: note/11.ai/08-llmops/agent-evaluation/02-ab-testing-design/README.md`
  - `self-return: note/11.ai/08-llmops/agent-evaluation/02-ab-testing-design/README.md`
  - `invalid-return: note/11.ai/08-llmops/agent-evaluation/09-rag-evaluation/README.md`
  - `wrong-return: note/11.ai/08-llmops/agent-evaluation/09-rag-evaluation/README.md`
  - `invalid-return: note/11.ai/08-llmops/agentic-search-vs-rag/README.md`
  - `self-return: note/11.ai/08-llmops/agentic-search-vs-rag/README.md`

## NAV-46: 12.story / 01-ai-agent-architecture.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/01-ai-agent-architecture.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/01-ai-agent-architecture.md`

## NAV-47: 12.story / 02-system-architecture-evolution.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/02-system-architecture-evolution.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/02-system-architecture-evolution.md`

## NAV-48: 12.story / 11-ai-learning-paradox.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/11-ai-learning-paradox.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/11-ai-learning-paradox.md`

## NAV-49: 12.story / 25-ai-org-transformation.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/25-ai-org-transformation.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/25-ai-org-transformation.md`

## NAV-50: 12.story / 26-ai-native-startup.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/26-ai-native-startup.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/26-ai-native-startup.md`

## NAV-51: 12.story / 27-self-evolving-company.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/27-self-evolving-company.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/27-self-evolving-company.md`

## NAV-52: 12.story / 28-ai-hallucination-safety.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/28-ai-hallucination-safety.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/28-ai-hallucination-safety.md`

## NAV-53: 12.story / 29-codebase-cognitive-debt.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/29-codebase-cognitive-debt.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/29-codebase-cognitive-debt.md`

## NAV-54: 12.story / 30-agent-harness.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/30-agent-harness.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/30-agent-harness.md`

## NAV-55: 12.story / 31-ai-fatal-trio.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/31-ai-fatal-trio.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/31-ai-fatal-trio.md`

## NAV-56: 12.story / 32a-ai-evaluation-fundamentals.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/32a-ai-evaluation-fundamentals.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/32a-ai-evaluation-fundamentals.md`

## NAV-57: 12.story / 32b-ai-evaluation-pipeline.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/32b-ai-evaluation-pipeline.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/32b-ai-evaluation-pipeline.md`

## NAV-58: 12.story / 33a-mcp-protocol.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/33a-mcp-protocol.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/33a-mcp-protocol.md`

## NAV-59: 12.story / 33b-a2a-protocol.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/33b-a2a-protocol.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/33b-a2a-protocol.md`

## NAV-60: 12.story / 34a-ai-token-cost-structure.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/34a-ai-token-cost-structure.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/34a-ai-token-cost-structure.md`

## NAV-61: 12.story / 34b-ai-token-cost-optimization.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/34b-ai-token-cost-optimization.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/34b-ai-token-cost-optimization.md`

## NAV-62: 12.story / 35-ai-observability.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/35-ai-observability.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/35-ai-observability.md`

## NAV-63: 12.story / 36-rag-retrieval-augmented-generation.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/36-rag-retrieval-augmented-generation.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/36-rag-retrieval-augmented-generation.md`

## NAV-64: 12.story / 37-vector-database-and-embedding.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/37-vector-database-and-embedding.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/37-vector-database-and-embedding.md`

## NAV-65: 12.story / 38-ai-compliance-and-regulation.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/38-ai-compliance-and-regulation.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/38-ai-compliance-and-regulation.md`

## NAV-66: 12.story / 39-ai-private-deployment.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/39-ai-private-deployment.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/39-ai-private-deployment.md`

## NAV-67: 12.story / STORY-FORMAT-SPEC.md
- Defects: 1
- Unique files: 2
- Files:
  - `note/12.story/STORY-FORMAT-SPEC.md`
  - `note/12.story/index.md`
- Defect rows:
  - `one-way: note/12.story/STORY-FORMAT-SPEC.md`

## NAV-68: 13.split-hairs / 01.java
- Defects: 49
- Unique files: 25
- Files:
  - `note/13.split-hairs/01.java/README.md`
  - `note/13.split-hairs/01.java/aqs/README.md`
  - `note/13.split-hairs/01.java/arrayList-distinct/README.md`
  - `note/13.split-hairs/01.java/class-loading/README.md`
  - `note/13.split-hairs/01.java/completable-future/README.md`
  - `note/13.split-hairs/01.java/concurrency-vs-parallelism/README.md`
  - `note/13.split-hairs/01.java/concurrent-hashmap/README.md`
  - `note/13.split-hairs/01.java/cpu-spike-troubleshooting/README.md`
  - `note/13.split-hairs/01.java/create-object/README.md`
  - `note/13.split-hairs/01.java/equals-hashcode/README.md`
  - `note/13.split-hairs/01.java/final-finally-finalize/README.md`
  - `note/13.split-hairs/01.java/gc-algorithms/README.md`
  - `note/13.split-hairs/01.java/generics-erasure/README.md`
  - `note/13.split-hairs/01.java/hashmap-resizing/README.md`
  - `note/13.split-hairs/01.java/if-before-switch/README.md`
  - `note/13.split-hairs/01.java/integer-cache/README.md`
  - `note/13.split-hairs/01.java/jvm-memory-pitfall/README.md`
  - `note/13.split-hairs/01.java/jvm-memory/README.md`
  - `note/13.split-hairs/01.java/large-data-into-hashmap/README.md`
  - `note/13.split-hairs/01.java/new-string/README.md`
  - `note/13.split-hairs/01.java/object/README.md`
  - `note/13.split-hairs/01.java/parent-child-thread/README.md`
  - `note/13.split-hairs/01.java/questions/README.md`
  - `note/13.split-hairs/01.java/record-t/README.md`
  - `note/13.split-hairs/01.java/reflection/README.md`
- Defect rows:
  - `invalid-return: note/13.split-hairs/01.java/aqs/README.md`
  - `self-return: note/13.split-hairs/01.java/aqs/README.md`
  - `invalid-return: note/13.split-hairs/01.java/arrayList-distinct/README.md`
  - `self-return: note/13.split-hairs/01.java/arrayList-distinct/README.md`
  - `invalid-return: note/13.split-hairs/01.java/class-loading/README.md`
  - `self-return: note/13.split-hairs/01.java/class-loading/README.md`
  - `invalid-return: note/13.split-hairs/01.java/completable-future/README.md`
  - `self-return: note/13.split-hairs/01.java/completable-future/README.md`
  - `invalid-return: note/13.split-hairs/01.java/concurrency-vs-parallelism/README.md`
  - `self-return: note/13.split-hairs/01.java/concurrency-vs-parallelism/README.md`
  - `invalid-return: note/13.split-hairs/01.java/concurrent-hashmap/README.md`
  - `self-return: note/13.split-hairs/01.java/concurrent-hashmap/README.md`
  - `invalid-return: note/13.split-hairs/01.java/cpu-spike-troubleshooting/README.md`
  - `self-return: note/13.split-hairs/01.java/cpu-spike-troubleshooting/README.md`
  - `invalid-return: note/13.split-hairs/01.java/create-object/README.md`
  - `self-return: note/13.split-hairs/01.java/create-object/README.md`
  - `invalid-return: note/13.split-hairs/01.java/equals-hashcode/README.md`
  - `self-return: note/13.split-hairs/01.java/equals-hashcode/README.md`
  - `invalid-return: note/13.split-hairs/01.java/final-finally-finalize/README.md`
  - `self-return: note/13.split-hairs/01.java/final-finally-finalize/README.md`
  - `invalid-return: note/13.split-hairs/01.java/gc-algorithms/README.md`
  - `self-return: note/13.split-hairs/01.java/gc-algorithms/README.md`
  - `invalid-return: note/13.split-hairs/01.java/generics-erasure/README.md`
  - `self-return: note/13.split-hairs/01.java/generics-erasure/README.md`
  - `invalid-return: note/13.split-hairs/01.java/hashmap-resizing/README.md`
  - `self-return: note/13.split-hairs/01.java/hashmap-resizing/README.md`
  - `invalid-return: note/13.split-hairs/01.java/if-before-switch/README.md`
  - `self-return: note/13.split-hairs/01.java/if-before-switch/README.md`
  - `invalid-return: note/13.split-hairs/01.java/integer-cache/README.md`
  - `self-return: note/13.split-hairs/01.java/integer-cache/README.md`
  - `invalid-return: note/13.split-hairs/01.java/jvm-memory-pitfall/README.md`
  - `self-return: note/13.split-hairs/01.java/jvm-memory-pitfall/README.md`
  - `invalid-return: note/13.split-hairs/01.java/jvm-memory/README.md`
  - `self-return: note/13.split-hairs/01.java/jvm-memory/README.md`
  - `invalid-return: note/13.split-hairs/01.java/large-data-into-hashmap/README.md`
  - `self-return: note/13.split-hairs/01.java/large-data-into-hashmap/README.md`
  - `invalid-return: note/13.split-hairs/01.java/new-string/README.md`
  - `self-return: note/13.split-hairs/01.java/new-string/README.md`
  - `invalid-return: note/13.split-hairs/01.java/object/README.md`
  - `self-return: note/13.split-hairs/01.java/object/README.md`
  - `broken: note/13.split-hairs/01.java/parent-child-thread/README.md`
  - `invalid-return: note/13.split-hairs/01.java/parent-child-thread/README.md`
  - `self-return: note/13.split-hairs/01.java/parent-child-thread/README.md`
  - `invalid-return: note/13.split-hairs/01.java/questions/README.md`
  - `self-return: note/13.split-hairs/01.java/questions/README.md`
  - `invalid-return: note/13.split-hairs/01.java/record-t/README.md`
  - `self-return: note/13.split-hairs/01.java/record-t/README.md`
  - `invalid-return: note/13.split-hairs/01.java/reflection/README.md`
  - `self-return: note/13.split-hairs/01.java/reflection/README.md`

## NAV-69: 13.split-hairs / 01.java
- Defects: 28
- Unique files: 15
- Files:
  - `note/13.split-hairs/01.java/README.md`
  - `note/13.split-hairs/01.java/replace-linkedlist-with-hashset/README.md`
  - `note/13.split-hairs/01.java/replace-synchronized-with-atomic/README.md`
  - `note/13.split-hairs/01.java/reuse-of-stringbuilder/README.md`
  - `note/13.split-hairs/01.java/singleton-pattern/README.md`
  - `note/13.split-hairs/01.java/sort-map/README.md`
  - `note/13.split-hairs/01.java/spi/README.md`
  - `note/13.split-hairs/01.java/string-builder-buffer/README.md`
  - `note/13.split-hairs/01.java/synchronized-lock-upgrade/README.md`
  - `note/13.split-hairs/01.java/thread-pool/README.md`
  - `note/13.split-hairs/01.java/thread-sequential-execution/README.md`
  - `note/13.split-hairs/01.java/threadlocal/README.md`
  - `note/13.split-hairs/01.java/try-catch-performance/README.md`
  - `note/13.split-hairs/01.java/virtual-threads/README.md`
  - `note/13.split-hairs/01.java/volatile/README.md`
- Defect rows:
  - `invalid-return: note/13.split-hairs/01.java/replace-linkedlist-with-hashset/README.md`
  - `self-return: note/13.split-hairs/01.java/replace-linkedlist-with-hashset/README.md`
  - `invalid-return: note/13.split-hairs/01.java/replace-synchronized-with-atomic/README.md`
  - `self-return: note/13.split-hairs/01.java/replace-synchronized-with-atomic/README.md`
  - `invalid-return: note/13.split-hairs/01.java/reuse-of-stringbuilder/README.md`
  - `self-return: note/13.split-hairs/01.java/reuse-of-stringbuilder/README.md`
  - `invalid-return: note/13.split-hairs/01.java/singleton-pattern/README.md`
  - `self-return: note/13.split-hairs/01.java/singleton-pattern/README.md`
  - `invalid-return: note/13.split-hairs/01.java/sort-map/README.md`
  - `self-return: note/13.split-hairs/01.java/sort-map/README.md`
  - `invalid-return: note/13.split-hairs/01.java/spi/README.md`
  - `self-return: note/13.split-hairs/01.java/spi/README.md`
  - `invalid-return: note/13.split-hairs/01.java/string-builder-buffer/README.md`
  - `self-return: note/13.split-hairs/01.java/string-builder-buffer/README.md`
  - `invalid-return: note/13.split-hairs/01.java/synchronized-lock-upgrade/README.md`
  - `self-return: note/13.split-hairs/01.java/synchronized-lock-upgrade/README.md`
  - `invalid-return: note/13.split-hairs/01.java/thread-pool/README.md`
  - `self-return: note/13.split-hairs/01.java/thread-pool/README.md`
  - `invalid-return: note/13.split-hairs/01.java/thread-sequential-execution/README.md`
  - `self-return: note/13.split-hairs/01.java/thread-sequential-execution/README.md`
  - `invalid-return: note/13.split-hairs/01.java/threadlocal/README.md`
  - `self-return: note/13.split-hairs/01.java/threadlocal/README.md`
  - `invalid-return: note/13.split-hairs/01.java/try-catch-performance/README.md`
  - `self-return: note/13.split-hairs/01.java/try-catch-performance/README.md`
  - `invalid-return: note/13.split-hairs/01.java/virtual-threads/README.md`
  - `self-return: note/13.split-hairs/01.java/virtual-threads/README.md`
  - `invalid-return: note/13.split-hairs/01.java/volatile/README.md`
  - `self-return: note/13.split-hairs/01.java/volatile/README.md`

## NAV-70: 13.split-hairs / 02.computer-basics
- Defects: 3
- Unique files: 3
- Files:
  - `note/13.split-hairs/02.computer-basics/README.md`
  - `note/13.split-hairs/02.computer-basics/machine-learning/README.md`
  - `note/13.split-hairs/02.computer-basics/port-reuse-so-reuseport/README.md`
- Defect rows:
  - `one-way: note/13.split-hairs/02.computer-basics/machine-learning/README.md`
  - `invalid-return: note/13.split-hairs/02.computer-basics/port-reuse-so-reuseport/README.md`
  - `self-return: note/13.split-hairs/02.computer-basics/port-reuse-so-reuseport/README.md`

## NAV-71: 13.split-hairs / 03.database
- Defects: 20
- Unique files: 12
- Files:
  - `note/13.split-hairs/03.database/README.md`
  - `note/13.split-hairs/03.database/bplus-tree/README.md`
  - `note/13.split-hairs/03.database/deadlock/README.md`
  - `note/13.split-hairs/03.database/mvcc/README.md`
  - `note/13.split-hairs/03.database/mysql-join/README.md`
  - `note/13.split-hairs/03.database/mysql-time-types/README.md`
  - `note/13.split-hairs/03.database/mysql-what-lock/README.md`
  - `note/13.split-hairs/03.database/redis-big-key/README.md`
  - `note/13.split-hairs/03.database/redis-cluster/README.md`
  - `note/13.split-hairs/03.database/redis-eviction/README.md`
  - `note/13.split-hairs/03.database/redis-persistence/README.md`
  - `note/13.split-hairs/03.database/replication-lag/README.md`
- Defect rows:
  - `invalid-return: note/13.split-hairs/03.database/bplus-tree/README.md`
  - `self-return: note/13.split-hairs/03.database/bplus-tree/README.md`
  - `invalid-return: note/13.split-hairs/03.database/deadlock/README.md`
  - `self-return: note/13.split-hairs/03.database/deadlock/README.md`
  - `invalid-return: note/13.split-hairs/03.database/mvcc/README.md`
  - `self-return: note/13.split-hairs/03.database/mvcc/README.md`
  - `invalid-return: note/13.split-hairs/03.database/mysql-join/README.md`
  - `self-return: note/13.split-hairs/03.database/mysql-join/README.md`
  - `broken: note/13.split-hairs/03.database/mysql-time-types/README.md`
  - `broken: note/13.split-hairs/03.database/mysql-what-lock/README.md`
  - `invalid-return: note/13.split-hairs/03.database/redis-big-key/README.md`
  - `self-return: note/13.split-hairs/03.database/redis-big-key/README.md`
  - `invalid-return: note/13.split-hairs/03.database/redis-cluster/README.md`
  - `self-return: note/13.split-hairs/03.database/redis-cluster/README.md`
  - `invalid-return: note/13.split-hairs/03.database/redis-eviction/README.md`
  - `self-return: note/13.split-hairs/03.database/redis-eviction/README.md`
  - `invalid-return: note/13.split-hairs/03.database/redis-persistence/README.md`
  - `self-return: note/13.split-hairs/03.database/redis-persistence/README.md`
  - `invalid-return: note/13.split-hairs/03.database/replication-lag/README.md`
  - `self-return: note/13.split-hairs/03.database/replication-lag/README.md`

## NAV-72: 13.split-hairs / 04.system-design
- Defects: 14
- Unique files: 7
- Files:
  - `note/13.split-hairs/04.system-design/README.md`
  - `note/13.split-hairs/04.system-design/cap-theorem/README.md`
  - `note/13.split-hairs/04.system-design/circuit-breaker/README.md`
  - `note/13.split-hairs/04.system-design/idempotency/README.md`
  - `note/13.split-hairs/04.system-design/microservices-vs-monolith/README.md`
  - `note/13.split-hairs/04.system-design/multi-tenant-saas/README.md`
  - `note/13.split-hairs/04.system-design/url-shortener/README.md`
- Defect rows:
  - `broken: note/13.split-hairs/04.system-design/README.md`
  - `invalid-return: note/13.split-hairs/04.system-design/cap-theorem/README.md`
  - `self-return: note/13.split-hairs/04.system-design/cap-theorem/README.md`
  - `invalid-return: note/13.split-hairs/04.system-design/circuit-breaker/README.md`
  - `self-return: note/13.split-hairs/04.system-design/circuit-breaker/README.md`
  - `invalid-return: note/13.split-hairs/04.system-design/idempotency/README.md`
  - `self-return: note/13.split-hairs/04.system-design/idempotency/README.md`
  - `invalid-return: note/13.split-hairs/04.system-design/microservices-vs-monolith/README.md`
  - `self-return: note/13.split-hairs/04.system-design/microservices-vs-monolith/README.md`
  - `invalid-return: note/13.split-hairs/04.system-design/multi-tenant-saas/README.md`
  - `self-return: note/13.split-hairs/04.system-design/multi-tenant-saas/README.md`
  - `broken: note/13.split-hairs/04.system-design/url-shortener/README.md`
  - `invalid-return: note/13.split-hairs/04.system-design/url-shortener/README.md`
  - `self-return: note/13.split-hairs/04.system-design/url-shortener/README.md`

## NAV-73: 13.split-hairs / 05.security
- Defects: 5
- Unique files: 3
- Files:
  - `note/13.split-hairs/05.security/README.md`
  - `note/13.split-hairs/05.security/access-control-design/README.md`
  - `note/13.split-hairs/05.security/sso/README.md`
- Defect rows:
  - `broken: note/13.split-hairs/05.security/README.md`
  - `invalid-return: note/13.split-hairs/05.security/access-control-design/README.md`
  - `self-return: note/13.split-hairs/05.security/access-control-design/README.md`
  - `invalid-return: note/13.split-hairs/05.security/sso/README.md`
  - `self-return: note/13.split-hairs/05.security/sso/README.md`

## NAV-74: 13.split-hairs / 06.spring
- Defects: 28
- Unique files: 15
- Files:
  - `note/13.split-hairs/06.spring/README.md`
  - `note/13.split-hairs/06.spring/aop-principle/README.md`
  - `note/13.split-hairs/06.spring/async-pitfalls/README.md`
  - `note/13.split-hairs/06.spring/auto-configuration/README.md`
  - `note/13.split-hairs/06.spring/bean-lifecycle/README.md`
  - `note/13.split-hairs/06.spring/bean-vs-component/README.md`
  - `note/13.split-hairs/06.spring/cache-degradation/README.md`
  - `note/13.split-hairs/06.spring/circular-dependency/README.md`
  - `note/13.split-hairs/06.spring/clarify-various-o/README.md`
  - `note/13.split-hairs/06.spring/event-mechanism/README.md`
  - `note/13.split-hairs/06.spring/jdk-proxy-vs-cglib/README.md`
  - `note/13.split-hairs/06.spring/not-use-@autowired/README.md`
  - `note/13.split-hairs/06.spring/spring-mvc-flow/README.md`
  - `note/13.split-hairs/06.spring/transactional-pitfalls/README.md`
  - `note/13.split-hairs/06.spring/transactional-propagation/README.md`
- Defect rows:
  - `invalid-return: note/13.split-hairs/06.spring/aop-principle/README.md`
  - `self-return: note/13.split-hairs/06.spring/aop-principle/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/async-pitfalls/README.md`
  - `self-return: note/13.split-hairs/06.spring/async-pitfalls/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/auto-configuration/README.md`
  - `self-return: note/13.split-hairs/06.spring/auto-configuration/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/bean-lifecycle/README.md`
  - `self-return: note/13.split-hairs/06.spring/bean-lifecycle/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/bean-vs-component/README.md`
  - `self-return: note/13.split-hairs/06.spring/bean-vs-component/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/cache-degradation/README.md`
  - `self-return: note/13.split-hairs/06.spring/cache-degradation/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/circular-dependency/README.md`
  - `self-return: note/13.split-hairs/06.spring/circular-dependency/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/clarify-various-o/README.md`
  - `self-return: note/13.split-hairs/06.spring/clarify-various-o/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/event-mechanism/README.md`
  - `self-return: note/13.split-hairs/06.spring/event-mechanism/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/jdk-proxy-vs-cglib/README.md`
  - `self-return: note/13.split-hairs/06.spring/jdk-proxy-vs-cglib/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/not-use-@autowired/README.md`
  - `self-return: note/13.split-hairs/06.spring/not-use-@autowired/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/spring-mvc-flow/README.md`
  - `self-return: note/13.split-hairs/06.spring/spring-mvc-flow/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/transactional-pitfalls/README.md`
  - `self-return: note/13.split-hairs/06.spring/transactional-pitfalls/README.md`
  - `invalid-return: note/13.split-hairs/06.spring/transactional-propagation/README.md`
  - `self-return: note/13.split-hairs/06.spring/transactional-propagation/README.md`

## NAV-75: 13.split-hairs / 09.front-end
- Defects: 48
- Unique files: 25
- Files:
  - `note/13.split-hairs/09.front-end/README.md`
  - `note/13.split-hairs/09.front-end/async-await-try-catch/README.md`
  - `note/13.split-hairs/09.front-end/bfc/README.md`
  - `note/13.split-hairs/09.front-end/closure/README.md`
  - `note/13.split-hairs/09.front-end/cors/README.md`
  - `note/13.split-hairs/09.front-end/css-button-styling/README.md`
  - `note/13.split-hairs/09.front-end/css-render-blocking/README.md`
  - `note/13.split-hairs/09.front-end/debounce-throttle/README.md`
  - `note/13.split-hairs/09.front-end/deep-copy/README.md`
  - `note/13.split-hairs/09.front-end/event-loop/README.md`
  - `note/13.split-hairs/09.front-end/from-url-to-page/README.md`
  - `note/13.split-hairs/09.front-end/get-and-post/README.md`
  - `note/13.split-hairs/09.front-end/http-cache/README.md`
  - `note/13.split-hairs/09.front-end/https-handshake/README.md`
  - `note/13.split-hairs/09.front-end/lazy-load-preload/README.md`
  - `note/13.split-hairs/09.front-end/message/README.md`
  - `note/13.split-hairs/09.front-end/playwright-vs-selenium/README.md`
  - `note/13.split-hairs/09.front-end/promise-handwriting/README.md`
  - `note/13.split-hairs/09.front-end/prototype-chain/README.md`
  - `note/13.split-hairs/09.front-end/react-hooks/README.md`
  - `note/13.split-hairs/09.front-end/reflow-repaint/README.md`
  - `note/13.split-hairs/09.front-end/script-async-defer/README.md`
  - `note/13.split-hairs/09.front-end/storage/README.md`
  - `note/13.split-hairs/09.front-end/this-binding/README.md`
  - `note/13.split-hairs/09.front-end/virtual-dom-diff/README.md`
- Defect rows:
  - `invalid-return: note/13.split-hairs/09.front-end/async-await-try-catch/README.md`
  - `self-return: note/13.split-hairs/09.front-end/async-await-try-catch/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/bfc/README.md`
  - `self-return: note/13.split-hairs/09.front-end/bfc/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/closure/README.md`
  - `self-return: note/13.split-hairs/09.front-end/closure/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/cors/README.md`
  - `self-return: note/13.split-hairs/09.front-end/cors/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/css-button-styling/README.md`
  - `self-return: note/13.split-hairs/09.front-end/css-button-styling/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/css-render-blocking/README.md`
  - `self-return: note/13.split-hairs/09.front-end/css-render-blocking/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/debounce-throttle/README.md`
  - `self-return: note/13.split-hairs/09.front-end/debounce-throttle/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/deep-copy/README.md`
  - `self-return: note/13.split-hairs/09.front-end/deep-copy/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/event-loop/README.md`
  - `self-return: note/13.split-hairs/09.front-end/event-loop/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/from-url-to-page/README.md`
  - `self-return: note/13.split-hairs/09.front-end/from-url-to-page/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/get-and-post/README.md`
  - `self-return: note/13.split-hairs/09.front-end/get-and-post/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/http-cache/README.md`
  - `self-return: note/13.split-hairs/09.front-end/http-cache/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/https-handshake/README.md`
  - `self-return: note/13.split-hairs/09.front-end/https-handshake/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/lazy-load-preload/README.md`
  - `self-return: note/13.split-hairs/09.front-end/lazy-load-preload/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/message/README.md`
  - `self-return: note/13.split-hairs/09.front-end/message/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/playwright-vs-selenium/README.md`
  - `self-return: note/13.split-hairs/09.front-end/playwright-vs-selenium/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/promise-handwriting/README.md`
  - `self-return: note/13.split-hairs/09.front-end/promise-handwriting/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/prototype-chain/README.md`
  - `self-return: note/13.split-hairs/09.front-end/prototype-chain/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/react-hooks/README.md`
  - `self-return: note/13.split-hairs/09.front-end/react-hooks/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/reflow-repaint/README.md`
  - `self-return: note/13.split-hairs/09.front-end/reflow-repaint/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/script-async-defer/README.md`
  - `self-return: note/13.split-hairs/09.front-end/script-async-defer/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/storage/README.md`
  - `self-return: note/13.split-hairs/09.front-end/storage/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/this-binding/README.md`
  - `self-return: note/13.split-hairs/09.front-end/this-binding/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/virtual-dom-diff/README.md`
  - `self-return: note/13.split-hairs/09.front-end/virtual-dom-diff/README.md`

## NAV-76: 13.split-hairs / 09.front-end
- Defects: 4
- Unique files: 3
- Files:
  - `note/13.split-hairs/09.front-end/README.md`
  - `note/13.split-hairs/09.front-end/vue-reactivity/README.md`
  - `note/13.split-hairs/09.front-end/xss-csrf/README.md`
- Defect rows:
  - `invalid-return: note/13.split-hairs/09.front-end/vue-reactivity/README.md`
  - `self-return: note/13.split-hairs/09.front-end/vue-reactivity/README.md`
  - `invalid-return: note/13.split-hairs/09.front-end/xss-csrf/README.md`
  - `self-return: note/13.split-hairs/09.front-end/xss-csrf/README.md`

## NAV-77: 13.split-hairs / 11.ai
- Defects: 48
- Unique files: 25
- Files:
  - `note/13.split-hairs/11.ai/README.md`
  - `note/13.split-hairs/11.ai/agent-ab-testing/README.md`
  - `note/13.split-hairs/11.ai/agent-dag-vs-react/README.md`
  - `note/13.split-hairs/11.ai/agent-memory-classification/README.md`
  - `note/13.split-hairs/11.ai/ai-code-churn/README.md`
  - `note/13.split-hairs/11.ai/ai-code-review/README.md`
  - `note/13.split-hairs/11.ai/ai-coding-productivity-paradox/README.md`
  - `note/13.split-hairs/11.ai/ai-coding-roi/README.md`
  - `note/13.split-hairs/11.ai/ai-thinking/README.md`
  - `note/13.split-hairs/11.ai/claude-code-agentic-search/README.md`
  - `note/13.split-hairs/11.ai/context-engineering-interview/README.md`
  - `note/13.split-hairs/11.ai/dropout-in-llm/README.md`
  - `note/13.split-hairs/11.ai/function-calling/README.md`
  - `note/13.split-hairs/11.ai/hallucination/README.md`
  - `note/13.split-hairs/11.ai/harness-engineering/README.md`
  - `note/13.split-hairs/11.ai/incremental-embedding/README.md`
  - `note/13.split-hairs/11.ai/inference-engine-selection/README.md`
  - `note/13.split-hairs/11.ai/llm-alignment/README.md`
  - `note/13.split-hairs/11.ai/llm-inference/README.md`
  - `note/13.split-hairs/11.ai/long-context-agent-strategy/README.md`
  - `note/13.split-hairs/11.ai/loop-engineering/README.md`
  - `note/13.split-hairs/11.ai/multi-agent-shared-memory/README.md`
  - `note/13.split-hairs/11.ai/multi-agent-system-design/README.md`
  - `note/13.split-hairs/11.ai/multi-turn-tool-reasoning/README.md`
  - `note/13.split-hairs/11.ai/production-thinking-5q/README.md`
- Defect rows:
  - `broken: note/13.split-hairs/11.ai/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/agent-ab-testing/README.md`
  - `self-return: note/13.split-hairs/11.ai/agent-ab-testing/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/agent-dag-vs-react/README.md`
  - `self-return: note/13.split-hairs/11.ai/agent-dag-vs-react/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/agent-memory-classification/README.md`
  - `self-return: note/13.split-hairs/11.ai/agent-memory-classification/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/ai-code-churn/README.md`
  - `self-return: note/13.split-hairs/11.ai/ai-code-churn/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/ai-code-review/README.md`
  - `self-return: note/13.split-hairs/11.ai/ai-code-review/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/ai-coding-productivity-paradox/README.md`
  - `self-return: note/13.split-hairs/11.ai/ai-coding-productivity-paradox/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/ai-coding-roi/README.md`
  - `self-return: note/13.split-hairs/11.ai/ai-coding-roi/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/ai-thinking/README.md`
  - `self-return: note/13.split-hairs/11.ai/ai-thinking/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/claude-code-agentic-search/README.md`
  - `self-return: note/13.split-hairs/11.ai/claude-code-agentic-search/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/context-engineering-interview/README.md`
  - `self-return: note/13.split-hairs/11.ai/context-engineering-interview/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/dropout-in-llm/README.md`
  - `self-return: note/13.split-hairs/11.ai/dropout-in-llm/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/function-calling/README.md`
  - `self-return: note/13.split-hairs/11.ai/function-calling/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/hallucination/README.md`
  - `self-return: note/13.split-hairs/11.ai/hallucination/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/harness-engineering/README.md`
  - `self-return: note/13.split-hairs/11.ai/harness-engineering/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/incremental-embedding/README.md`
  - `self-return: note/13.split-hairs/11.ai/incremental-embedding/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/inference-engine-selection/README.md`
  - `self-return: note/13.split-hairs/11.ai/inference-engine-selection/README.md`
  - `one-way: note/13.split-hairs/11.ai/llm-alignment/README.md`
  - `orphan: note/13.split-hairs/11.ai/llm-alignment/README.md`
  - `one-way: note/13.split-hairs/11.ai/llm-inference/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/long-context-agent-strategy/README.md`
  - `self-return: note/13.split-hairs/11.ai/long-context-agent-strategy/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/loop-engineering/README.md`
  - `self-return: note/13.split-hairs/11.ai/loop-engineering/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/multi-agent-shared-memory/README.md`
  - `self-return: note/13.split-hairs/11.ai/multi-agent-shared-memory/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/multi-agent-system-design/README.md`
  - `self-return: note/13.split-hairs/11.ai/multi-agent-system-design/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/multi-turn-tool-reasoning/README.md`
  - `self-return: note/13.split-hairs/11.ai/multi-turn-tool-reasoning/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/production-thinking-5q/README.md`
  - `self-return: note/13.split-hairs/11.ai/production-thinking-5q/README.md`

## NAV-78: 13.split-hairs / 11.ai
- Defects: 24
- Unique files: 13
- Files:
  - `note/13.split-hairs/11.ai/README.md`
  - `note/13.split-hairs/11.ai/prompt-engineering/README.md`
  - `note/13.split-hairs/11.ai/rag-out-of-domain-rejection/README.md`
  - `note/13.split-hairs/11.ai/rag/README.md`
  - `note/13.split-hairs/11.ai/react-vs-plan-execute/README.md`
  - `note/13.split-hairs/11.ai/skill-design/README.md`
  - `note/13.split-hairs/11.ai/skill-hit-rate/README.md`
  - `note/13.split-hairs/11.ai/temperature-zero-myth/README.md`
  - `note/13.split-hairs/11.ai/token/README.md`
  - `note/13.split-hairs/11.ai/transformer/README.md`
  - `note/13.split-hairs/11.ai/vector-search-algorithms/README.md`
  - `note/13.split-hairs/11.ai/vector-search-at-scale/README.md`
  - `note/13.split-hairs/11.ai/vector-search-trillion/README.md`
- Defect rows:
  - `invalid-return: note/13.split-hairs/11.ai/prompt-engineering/README.md`
  - `self-return: note/13.split-hairs/11.ai/prompt-engineering/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/rag-out-of-domain-rejection/README.md`
  - `self-return: note/13.split-hairs/11.ai/rag-out-of-domain-rejection/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/rag/README.md`
  - `self-return: note/13.split-hairs/11.ai/rag/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/react-vs-plan-execute/README.md`
  - `self-return: note/13.split-hairs/11.ai/react-vs-plan-execute/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/skill-design/README.md`
  - `self-return: note/13.split-hairs/11.ai/skill-design/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/skill-hit-rate/README.md`
  - `self-return: note/13.split-hairs/11.ai/skill-hit-rate/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/temperature-zero-myth/README.md`
  - `self-return: note/13.split-hairs/11.ai/temperature-zero-myth/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/token/README.md`
  - `self-return: note/13.split-hairs/11.ai/token/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/transformer/README.md`
  - `self-return: note/13.split-hairs/11.ai/transformer/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/vector-search-algorithms/README.md`
  - `self-return: note/13.split-hairs/11.ai/vector-search-algorithms/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/vector-search-at-scale/README.md`
  - `self-return: note/13.split-hairs/11.ai/vector-search-at-scale/README.md`
  - `invalid-return: note/13.split-hairs/11.ai/vector-search-trillion/README.md`
  - `self-return: note/13.split-hairs/11.ai/vector-search-trillion/README.md`

## NAV-79: 14.project-management / scripts
- Defects: 2
- Unique files: 2
- Files:
  - `note/14.project-management/README.md`
  - `note/14.project-management/scripts/README.md`
- Defect rows:
  - `one-way: note/14.project-management/scripts/README.md`
  - `orphan: note/14.project-management/scripts/README.md`

## NAV-80: README.md / _root
- Defects: 1
- Unique files: 1
- Files:
  - `note/README.md`
- Defect rows:
  - `broken: note/README.md`
