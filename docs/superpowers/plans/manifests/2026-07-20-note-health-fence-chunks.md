# note-health 裸围栏实施分块

> 每块不超过 25 文件；lines 是初始 opening fence 行号，前序修改可能导致行号漂移，实施时按内容重新定位。

## FENCE-01: 01.java / build-tools
- Files: 1
- Openings: 3
- `note/01.java/build-tools/README.md` — lines: 219, 330, 335

## FENCE-02: 01.java / collection
- Files: 9
- Openings: 102
- `note/01.java/collection/ArrayList/README.md` — lines: 16, 62, 126, 182, 252, 332, 378, 514, 550, 566
- `note/01.java/collection/ConcurrentHashMap/README.md` — lines: 19, 46, 77, 95, 110, 138, 171, 183, 237, 267, 396, 407, 455, 470, 499, 533, 552, 581, 634, 661, 682, 712, 788, 814, 839, 889, 1013
- `note/01.java/collection/LinkedHashSet/README.md` — lines: 87
- `note/01.java/collection/LinkedList/README.md` — lines: 16, 98, 184, 206, 313
- `note/01.java/collection/README.md` — lines: 19, 70, 108, 132, 266, 413
- `note/01.java/collection/TreeMap/README.md` — lines: 25, 45, 83, 151, 166, 232, 298, 397, 475, 499, 683, 699, 712, 747, 761, 791, 847, 874
- `note/01.java/collection/WeakHashMap/README.md` — lines: 21, 37, 95, 197, 213, 297, 530, 566
- `note/01.java/collection/concurrent.md` — lines: 11, 28, 89, 120, 139, 151, 162, 166, 180, 200, 266, 318, 338, 430
- `note/01.java/collection/hashmap.md` — lines: 11, 40, 67, 90, 98, 120, 155, 178, 203, 235, 258, 277, 305

## FENCE-03: 01.java / concepts
- Files: 3
- Openings: 5
- `note/01.java/concepts/date-time/README.md` — lines: 655
- `note/01.java/concepts/exception/README.md` — lines: 535
- `note/01.java/concepts/spi/README.md` — lines: 120, 126, 298

## FENCE-04: 01.java / concurrency
- Files: 18
- Openings: 144
- `note/01.java/concurrency/README.md` — lines: 29, 96, 230, 343, 405, 459, 583, 656
- `note/01.java/concurrency/atomic/README.md` — lines: 23, 93, 332, 361, 438, 475, 521
- `note/01.java/concurrency/completablefuture/README.md` — lines: 500
- `note/01.java/concurrency/concurrent-collections/README.md` — lines: 56, 74, 135, 155, 184
- `note/01.java/concurrency/concurrent-collections/copy-on-write/README.md` — lines: 21, 97, 115, 178
- `note/01.java/concurrency/concurrent-collections/queue/README.md` — lines: 21, 38, 146, 168, 192, 215, 274, 285, 358, 374, 431, 502, 512, 572, 588, 633
- `note/01.java/concurrency/concurrent-collections/skip-list/README.md` — lines: 19, 49, 71, 99, 151, 175
- `note/01.java/concurrency/java-locks/README.md` — lines: 40, 44, 166, 216, 288, 337, 362, 502, 643, 738, 779, 806
- `note/01.java/concurrency/jmm/README.md` — lines: 23, 68, 115, 121, 245, 291, 338, 343, 354, 359, 486, 531, 537, 545, 617
- `note/01.java/concurrency/juc-locks/README.md` — lines: 35, 47, 79, 109, 158, 172, 339, 349, 588, 629, 643, 674, 729, 779, 800, 823
- `note/01.java/concurrency/synchronized/README.md` — lines: 82, 104, 122, 161, 210, 276, 291
- `note/01.java/concurrency/thread-basics/README.md` — lines: 167, 396, 457, 510, 585
- `note/01.java/concurrency/thread-basics/sequential-execution.md` — lines: 24, 353
- `note/01.java/concurrency/thread-pool/README.md` — lines: 57, 152, 185, 513, 565, 697, 817
- `note/01.java/concurrency/threadlocal/README.md` — lines: 36, 73, 148, 188, 258, 301, 348, 395, 427, 447, 519, 588
- `note/01.java/concurrency/utilities/README.md` — lines: 52, 159, 280, 432, 560, 678
- `note/01.java/concurrency/virtual-threads/README.md` — lines: 22, 46, 281
- `note/01.java/concurrency/volatile/README.md` — lines: 125, 162, 190, 198, 240, 257, 312, 368, 376, 441, 474, 515

## FENCE-05: 01.java / io
- Files: 3
- Openings: 20
- `note/01.java/io/README.md` — lines: 44, 597, 623
- `note/01.java/io/nio/README.md` — lines: 27, 37, 55, 105, 121, 209, 283, 744, 764, 855, 916
- `note/01.java/io/zero-copy/README.md` — lines: 52, 72, 94, 111, 132, 253

## FENCE-06: 01.java / java-agent
- Files: 2
- Openings: 5
- `note/01.java/java-agent/README.md` — lines: 31, 342, 382
- `note/01.java/java-agent/api/README.md` — lines: 21, 290

## FENCE-07: 01.java / jdbc
- Files: 1
- Openings: 2
- `note/01.java/jdbc/README.md` — lines: 19, 610

## FENCE-08: 01.java / jvm
- Files: 3
- Openings: 34
- `note/01.java/jvm/README.md` — lines: 27, 53, 68, 105, 135, 203, 215, 275, 302, 311, 323, 355, 376, 399, 422, 460, 526, 561
- `note/01.java/jvm/parameters.md` — lines: 254, 346, 372
- `note/01.java/jvm/tuning.md` — lines: 70, 113, 138, 151, 164, 177, 190, 205, 609, 659, 727, 812, 833

## FENCE-09: 01.java / logging
- Files: 1
- Openings: 7
- `note/01.java/logging/README.md` — lines: 243, 354, 476, 562, 626, 643, 806

## FENCE-10: 01.java / modules
- Files: 1
- Openings: 10
- `note/01.java/modules/README.md` — lines: 33, 146, 183, 260, 452, 470, 502, 508, 553, 594

## FENCE-11: 01.java / network
- Files: 1
- Openings: 7
- `note/01.java/network/README.md` — lines: 18, 159, 443, 500, 525, 558, 738

## FENCE-12: 01.java / testing
- Files: 1
- Openings: 3
- `note/01.java/testing/README.md` — lines: 42, 136, 784

## FENCE-13: 01.java / version
- Files: 3
- Openings: 3
- `note/01.java/version/README.md` — lines: 100
- `note/01.java/version/java-21/README.md` — lines: 421
- `note/01.java/version/java-8/README.md` — lines: 273

## FENCE-14: 02.computer-basics / 01-network
- Files: 8
- Openings: 42
- `note/02.computer-basics/01-network/01-tcp-ip/README.md` — lines: 19, 68, 89, 168, 190, 222, 250
- `note/02.computer-basics/01-network/02-http/README.md` — lines: 39, 55, 61, 90, 106, 118, 130, 150
- `note/02.computer-basics/01-network/03-dns/README.md` — lines: 27, 60, 83, 169, 194, 210
- `note/02.computer-basics/01-network/04-https-tls/README.md` — lines: 27, 61, 74, 104, 118, 142, 263, 272
- `note/02.computer-basics/01-network/osi-model/README.md` — lines: 19, 94
- `note/02.computer-basics/01-network/protocols/sse-vs-websocket/README.md` — lines: 35, 59, 85, 101, 126, 143, 176, 215
- `note/02.computer-basics/01-network/protocols/tcp-packet/README.md` — lines: 62
- `note/02.computer-basics/01-network/tcp-ip-model/README.md` — lines: 19, 61

## FENCE-15: 02.computer-basics / 02-algorithms
- Files: 10
- Openings: 25
- `note/02.computer-basics/02-algorithms/clustering/k-means/README.md` — lines: 22, 89
- `note/02.computer-basics/02-algorithms/decision-tree/README.md` — lines: 34, 48, 61, 93
- `note/02.computer-basics/02-algorithms/dimensionality-reduction/pca/README.md` — lines: 26, 69, 91
- `note/02.computer-basics/02-algorithms/ensemble/README.md` — lines: 131
- `note/02.computer-basics/02-algorithms/optimization/gradient-descent/README.md` — lines: 22, 65
- `note/02.computer-basics/02-algorithms/search/README.md` — lines: 42
- `note/02.computer-basics/02-algorithms/search/branch-and-bound/README.md` — lines: 20, 32, 41
- `note/02.computer-basics/02-algorithms/string-algorithms/02-kmp-algorithm.md` — lines: 20, 34, 48, 150
- `note/02.computer-basics/02-algorithms/string-algorithms/03-ac-automaton.md` — lines: 22, 39
- `note/02.computer-basics/02-algorithms/string-algorithms/README.md` — lines: 37, 109, 144

## FENCE-16: 02.computer-basics / 06-operating-system
- Files: 5
- Openings: 34
- `note/02.computer-basics/06-operating-system/README.md` — lines: 26, 60
- `note/02.computer-basics/06-operating-system/filesystem/README.md` — lines: 18, 85, 111, 127, 203, 238, 285, 377
- `note/02.computer-basics/06-operating-system/memory/README.md` — lines: 29, 71, 102, 120, 161, 180, 197, 258
- `note/02.computer-basics/06-operating-system/processes/README.md` — lines: 28, 51, 127, 159, 224
- `note/02.computer-basics/06-operating-system/scheduling/README.md` — lines: 26, 52, 69, 86, 107, 149, 163, 194, 242, 271, 306

## FENCE-17: 03.database / 02-sql
- Files: 1
- Openings: 2
- `note/03.database/02-sql/README.md` — lines: 140, 444

## FENCE-18: 03.database / 03-transaction
- Files: 1
- Openings: 4
- `note/03.database/03-transaction/README.md` — lines: 47, 55, 211, 300

## FENCE-19: 03.database / 04-index
- Files: 1
- Openings: 6
- `note/03.database/04-index/README.md` — lines: 59, 137, 265, 274, 313, 376

## FENCE-20: 03.database / 05-mysql
- Files: 1
- Openings: 6
- `note/03.database/05-mysql/README.md` — lines: 53, 91, 121, 131, 159, 197

## FENCE-21: 03.database / 06-cache
- Files: 1
- Openings: 8
- `note/03.database/06-cache/README.md` — lines: 74, 92, 140, 149, 159, 167, 200, 281

## FENCE-22: 03.database / 07-redis
- Files: 1
- Openings: 7
- `note/03.database/07-redis/README.md` — lines: 136, 148, 167, 186, 298, 374, 475

## FENCE-23: 03.database / 08-nosql
- Files: 5
- Openings: 11
- `note/03.database/08-nosql/README.md` — lines: 98, 122
- `note/03.database/08-nosql/cassandra/README.md` — lines: 46
- `note/03.database/08-nosql/elasticsearch/README.md` — lines: 41, 78, 112, 127, 236
- `note/03.database/08-nosql/mongodb/README.md` — lines: 100, 123
- `note/03.database/08-nosql/neo4j/README.md` — lines: 103

## FENCE-24: 03.database / 09-connection-pool
- Files: 1
- Openings: 3
- `note/03.database/09-connection-pool/README.md` — lines: 46, 166, 272

## FENCE-25: 03.database / 10-data-migration
- Files: 1
- Openings: 5
- `note/03.database/10-data-migration/README.md` — lines: 58, 145, 157, 384, 416

## FENCE-26: 03.database / 11-monitoring
- Files: 1
- Openings: 1
- `note/03.database/11-monitoring/README.md` — lines: 36

## FENCE-27: 03.database / 12-cloud-database
- Files: 1
- Openings: 5
- `note/03.database/12-cloud-database/README.md` — lines: 91, 108, 166, 347, 391

## FENCE-28: 03.database / 13-postgresql
- Files: 1
- Openings: 4
- `note/03.database/13-postgresql/README.md` — lines: 50, 84, 287, 317

## FENCE-29: 04.system-design / 01-foundation
- Files: 24
- Openings: 88
- `note/04.system-design/01-foundation/02-evolution/02-serverless-architecture/README.md` — lines: 51, 67, 77, 139, 286, 329, 335, 341, 347, 353
- `note/04.system-design/01-foundation/02-evolution/README.md` — lines: 24, 66, 96, 108, 141
- `note/04.system-design/01-foundation/system-design-basics/archimate/README.md` — lines: 92, 125
- `note/04.system-design/01-foundation/system-design-basics/archimate/in-practice.md` — lines: 17, 24, 103, 215, 308
- `note/04.system-design/01-foundation/system-design-basics/archimate/viewpoints.md` — lines: 114, 296
- `note/04.system-design/01-foundation/system-design-basics/architecture-evolution/README.md` — lines: 24, 48, 72, 112, 129, 165, 244, 307
- `note/04.system-design/01-foundation/system-design-basics/ddd/README.md` — lines: 54
- `note/04.system-design/01-foundation/system-design-basics/it4it/README.md` — lines: 96, 129
- `note/04.system-design/01-foundation/system-design-basics/it4it/in-practice.md` — lines: 181, 328
- `note/04.system-design/01-foundation/system-design-basics/it4it/value-streams.md` — lines: 98, 104, 143, 150, 201, 256
- `note/04.system-design/01-foundation/system-design-basics/microservices/README.md` — lines: 70, 121, 226
- `note/04.system-design/01-foundation/system-design-basics/microservices/data-consistency/README.md` — lines: 27, 37
- `note/04.system-design/01-foundation/system-design-basics/microservices/microservices-and-ddd/README.md` — lines: 102, 136, 150, 206
- `note/04.system-design/01-foundation/system-design-basics/microservices/migration-and-organization/README.md` — lines: 47, 157, 206, 286, 325
- `note/04.system-design/01-foundation/system-design-basics/microservices/service-communication/README.md` — lines: 309, 363, 432, 448, 458, 470
- `note/04.system-design/01-foundation/system-design-basics/microservices/service-contract/README.md` — lines: 27, 502, 509, 518
- `note/04.system-design/01-foundation/system-design-basics/microservices/service-decomposition/README.md` — lines: 72, 137, 262, 274, 286, 299
- `note/04.system-design/01-foundation/system-design-basics/multi-tenant-architecture/README.md` — lines: 35, 215
- `note/04.system-design/01-foundation/system-design-basics/ood/README.md` — lines: 20, 110
- `note/04.system-design/01-foundation/system-design-basics/togaf/README.md` — lines: 84, 116
- `note/04.system-design/01-foundation/system-design-basics/togaf/adm.md` — lines: 17
- `note/04.system-design/01-foundation/system-design-basics/togaf/architecture-governance.md` — lines: 144, 170, 182, 285
- `note/04.system-design/01-foundation/system-design-basics/togaf/business-capability.md` — lines: 118, 143, 164
- `note/04.system-design/01-foundation/system-design-basics/togaf/conway-and-team-topology.md` — lines: 67

## FENCE-30: 04.system-design / 02-distributed
- Files: 7
- Openings: 24
- `note/04.system-design/02-distributed/README.md` — lines: 139, 152, 163, 173, 185
- `note/04.system-design/02-distributed/cap-and-base/README.md` — lines: 49
- `note/04.system-design/02-distributed/consensus-algorithms/raft/README.md` — lines: 56
- `note/04.system-design/02-distributed/distributed-cache/README.md` — lines: 24, 42, 73, 126, 185, 250, 294, 303
- `note/04.system-design/02-distributed/distributed-id/README.md` — lines: 55
- `note/04.system-design/02-distributed/distributed-id/ulid/README.md` — lines: 20
- `note/04.system-design/02-distributed/service-discovery/README.md` — lines: 26, 44, 63, 112, 143, 194, 213

## FENCE-31: 04.system-design / 03-high-availability
- Files: 3
- Openings: 16
- `note/04.system-design/03-high-availability/chaos-engineering/README.md` — lines: 185, 204, 232, 241, 250
- `note/04.system-design/03-high-availability/rate-limiting/README.md` — lines: 61, 81, 103, 130
- `note/04.system-design/03-high-availability/rate-limiting/seckill-without-redis.md` — lines: 24, 300, 308, 339, 350, 368, 484

## FENCE-32: 04.system-design / 04-high-performance
- Files: 18
- Openings: 101
- `note/04.system-design/04-high-performance/cache-patterns/README.md` — lines: 54, 61, 68, 82, 165, 183, 190, 240, 246, 302, 308, 376, 754, 839, 855
- `note/04.system-design/04-high-performance/connection-pool/README.md` — lines: 36, 52, 90, 122, 166, 245
- `note/04.system-design/04-high-performance/database-optimization/README.md` — lines: 35, 118
- `note/04.system-design/04-high-performance/database-optimization/sql/README.md` — lines: 410, 421, 486, 502, 570
- `note/04.system-design/04-high-performance/file-upload/01-architecture.md` — lines: 20, 50, 117
- `note/04.system-design/04-high-performance/file-upload/02-chunked-and-resumable.md` — lines: 22, 181
- `note/04.system-design/04-high-performance/file-upload/03-instant-upload-and-storage.md` — lines: 22, 92, 154
- `note/04.system-design/04-high-performance/file-upload/README.md` — lines: 20, 64, 115, 128, 143, 151, 158, 170, 189, 204, 211
- `note/04.system-design/04-high-performance/product-search/01-architecture.md` — lines: 20, 51, 123, 187
- `note/04.system-design/04-high-performance/product-search/02-inverted-index.md` — lines: 24, 34, 52, 65, 80, 89, 96, 107, 114, 133, 144, 162, 261
- `note/04.system-design/04-high-performance/product-search/03-ranking.md` — lines: 22, 33, 47, 96, 121, 142, 194
- `note/04.system-design/04-high-performance/product-search/README.md` — lines: 20, 75, 84, 102, 123, 133, 149, 188, 195, 205
- `note/04.system-design/04-high-performance/sensitive-word-filter/01-architecture.md` — lines: 20, 42, 78
- `note/04.system-design/04-high-performance/sensitive-word-filter/03-high-concurrency-optimization.md` — lines: 20, 41, 92
- `note/04.system-design/04-high-performance/sensitive-word-filter/04-selection-decision-tree.md` — lines: 20, 69, 78, 87
- `note/04.system-design/04-high-performance/sensitive-word-filter/05-anti-evasion.md` — lines: 59
- `note/04.system-design/04-high-performance/sensitive-word-filter/README.md` — lines: 20, 49, 183, 193, 212
- `note/04.system-design/04-high-performance/serialization/README.md` — lines: 35, 85, 168, 324

## FENCE-33: 04.system-design / 05-security
- Files: 22
- Openings: 60
- `note/04.system-design/05-security/access-control/01-traditional/README.md` — lines: 45
- `note/04.system-design/05-security/access-control/01-traditional/dac.md` — lines: 16
- `note/04.system-design/05-security/access-control/01-traditional/mac.md` — lines: 16
- `note/04.system-design/05-security/access-control/02-role-and-attribute/README.md` — lines: 45
- `note/04.system-design/05-security/access-control/02-role-and-attribute/abac.md` — lines: 124
- `note/04.system-design/05-security/access-control/03-relationship-and-hybrid/README.md` — lines: 40
- `note/04.system-design/05-security/access-control/03-relationship-and-hybrid/hybrid.md` — lines: 17, 110
- `note/04.system-design/05-security/access-control/03-relationship-and-hybrid/rebac.md` — lines: 16, 61
- `note/04.system-design/05-security/access-control/README.md` — lines: 26, 57, 97, 112
- `note/04.system-design/05-security/api-security/README.md` — lines: 39, 95, 232, 675
- `note/04.system-design/05-security/encryption/README.md` — lines: 192, 242
- `note/04.system-design/05-security/jwt-security/README.md` — lines: 38, 73, 104, 217
- `note/04.system-design/05-security/oauth2-oidc/README.md` — lines: 42, 79, 105, 117, 174, 230, 267, 330, 364
- `note/04.system-design/05-security/owasp-top10/README.md` — lines: 37, 377
- `note/04.system-design/05-security/secrets-management/README.md` — lines: 65, 174, 186
- `note/04.system-design/05-security/sso/01-sso-concept.md` — lines: 26, 41, 58, 87, 111
- `note/04.system-design/05-security/sso/02-six-schemes-comparison.md` — lines: 24, 68, 80, 130, 202, 234, 321
- `note/04.system-design/05-security/sso/03-spring-security-implementation.md` — lines: 20, 238, 283
- `note/04.system-design/05-security/sso/04-jwt-implementation.md` — lines: 33
- `note/04.system-design/05-security/sso/05-selection-decision-tree.md` — lines: 20, 121
- `note/04.system-design/05-security/sso/README.md` — lines: 20, 37, 83
- `note/04.system-design/05-security/web-security/README.md` — lines: 178

## FENCE-34: 04.system-design / 06-idempotency
- Files: 6
- Openings: 12
- `note/04.system-design/06-idempotency/README.md` — lines: 66
- `note/04.system-design/06-idempotency/deduplication-table/README.md` — lines: 31
- `note/04.system-design/06-idempotency/idempotency-key/README.md` — lines: 31, 78
- `note/04.system-design/06-idempotency/optimistic-lock/README.md` — lines: 29, 216
- `note/04.system-design/06-idempotency/state-machine/README.md` — lines: 32, 176
- `note/04.system-design/06-idempotency/vs-distributed-transaction/README.md` — lines: 79, 111, 141, 152

## FENCE-35: 04.system-design / 07-deployment
- Files: 3
- Openings: 38
- `note/04.system-design/07-deployment/capacity-planning/README.md` — lines: 43, 96, 133, 154, 161, 174, 188, 229, 423, 429, 436, 465, 550
- `note/04.system-design/07-deployment/deploy/README.md` — lines: 53, 73, 111, 131, 184, 253, 270, 324, 334, 412, 471, 518, 580
- `note/04.system-design/07-deployment/observability/README.md` — lines: 49, 68, 240, 299, 329, 384, 395, 414, 421, 442, 472, 517

## FENCE-36: 04.system-design / 08-observability
- Files: 5
- Openings: 18
- `note/04.system-design/08-observability/01-prometheus/README.md` — lines: 42, 96, 315, 321
- `note/04.system-design/08-observability/02-grafana/README.md` — lines: 34, 79, 88, 95, 149, 194, 204, 228
- `note/04.system-design/08-observability/03-loki/README.md` — lines: 43, 210
- `note/04.system-design/08-observability/04-tracing/README.md` — lines: 69, 117, 211
- `note/04.system-design/08-observability/05-slo-sli/README.md` — lines: 130

## FENCE-37: 04.system-design / 09-emerging-tech
- Files: 4
- Openings: 14
- `note/04.system-design/09-emerging-tech/01-ebpf/README.md` — lines: 42, 128
- `note/04.system-design/09-emerging-tech/02-wasm/README.md` — lines: 76, 178, 187
- `note/04.system-design/09-emerging-tech/03-service-mesh-deep/README.md` — lines: 21, 52, 118, 183
- `note/04.system-design/09-emerging-tech/04-cloud-native-trends/README.md` — lines: 86, 174, 217, 233, 248

## FENCE-38: 05.tools / devops
- Files: 7
- Openings: 35
- `note/05.tools/devops/01-jenkins/README.md` — lines: 39, 325
- `note/05.tools/devops/02-gitlab-ci/README.md` — lines: 33, 52, 279
- `note/05.tools/devops/03-github-actions/README.md` — lines: 56, 244, 258
- `note/05.tools/devops/04-pipeline-patterns/README.md` — lines: 43, 71, 90, 121, 213, 252, 317
- `note/05.tools/devops/05-deploy-strategies/README.md` — lines: 44, 59, 89, 132, 244, 293
- `note/05.tools/devops/06-cicd-vs-gitops/README.md` — lines: 39, 62, 94, 117, 173, 185, 193, 202, 227, 235, 242
- `note/05.tools/devops/README.md` — lines: 19, 33, 170

## FENCE-39: 05.tools / iac
- Files: 1
- Openings: 5
- `note/05.tools/iac/README.md` — lines: 44, 61, 167, 262, 392

## FENCE-40: 05.tools / kubernetes
- Files: 9
- Openings: 18
- `note/05.tools/kubernetes/01-architecture/README.md` — lines: 25, 164
- `note/05.tools/kubernetes/02-pod-and-workload/README.md` — lines: 23
- `note/05.tools/kubernetes/03-service-and-ingress/README.md` — lines: 21, 179
- `note/05.tools/kubernetes/04-configmap-and-secret/README.md` — lines: 21
- `note/05.tools/kubernetes/05-storage-and-pv/README.md` — lines: 19
- `note/05.tools/kubernetes/06-network-and-service-mesh/README.md` — lines: 31, 125, 171
- `note/05.tools/kubernetes/07-helm/README.md` — lines: 21, 41, 173
- `note/05.tools/kubernetes/08-operator-and-gitops/README.md` — lines: 32, 123
- `note/05.tools/kubernetes/README.md` — lines: 30, 52, 120

## FENCE-41: 06.spring / 01-core
- Files: 9
- Openings: 12
- `note/06.spring/01-core/aop/advice-order-and-best-practices.md` — lines: 171
- `note/06.spring/01-core/aop/pointcut-expression.md` — lines: 19, 43, 49
- `note/06.spring/01-core/configuration-lite-vs-full.md` — lines: 232
- `note/06.spring/01-core/core-externalized-configuration.md` — lines: 32
- `note/06.spring/01-core/ioc/bean-lifecycle.md` — lines: 140
- `note/06.spring/01-core/ioc/circular-dependency.md` — lines: 55
- `note/06.spring/01-core/minispring/README.md` — lines: 65
- `note/06.spring/01-core/minispring/microrest/README.md` — lines: 36
- `note/06.spring/01-core/tools-reference.md` — lines: 217, 272

## FENCE-42: 06.spring / 02-web
- Files: 2
- Openings: 2
- `note/06.spring/02-web/mvc/cors-and-static.md` — lines: 105
- `note/06.spring/02-web/mvc/i18n.md` — lines: 88

## FENCE-43: 06.spring / 03-data
- Files: 9
- Openings: 15
- `note/06.spring/03-data/cache/cache-annotations-and-usage.md` — lines: 30
- `note/06.spring/03-data/cache/cache-degradation-and-recovery.md` — lines: 44, 199, 282, 411, 451
- `note/06.spring/03-data/cache/implementations-and-best-practices.md` — lines: 358, 378
- `note/06.spring/03-data/cache/multi-level.md` — lines: 52, 62
- `note/06.spring/03-data/cache/patterns.md` — lines: 260
- `note/06.spring/03-data/mybatis/03-spring-integration/01-assembly-and-startup.md` — lines: 358
- `note/06.spring/03-data/mybatis/03-spring-integration/04-multi-datasource.md` — lines: 45
- `note/06.spring/03-data/transaction/failure-cases.md` — lines: 349
- `note/06.spring/03-data/transaction/jpa-transaction.md` — lines: 196

## FENCE-44: 06.spring / 04-spring-boot
- Files: 4
- Openings: 6
- `note/06.spring/04-spring-boot/auto-configuration.md` — lines: 110, 287
- `note/06.spring/04-spring-boot/boot-externalized-configuration.md` — lines: 165, 281
- `note/06.spring/04-spring-boot/graalvm-native.md` — lines: 41
- `note/06.spring/04-spring-boot/startup-flow.md` — lines: 155

## FENCE-45: 06.spring / 05-spring-cloud
- Files: 3
- Openings: 8
- `note/06.spring/05-spring-cloud/config-center.md` — lines: 112, 254, 268
- `note/06.spring/05-spring-cloud/distributed-tracing.md` — lines: 171, 222, 229, 314
- `note/06.spring/05-spring-cloud/rpc-and-feign.md` — lines: 328

## FENCE-46: 06.spring / 06-integration
- Files: 2
- Openings: 2
- `note/06.spring/06-integration/statemachine.md` — lines: 308
- `note/06.spring/06-integration/validation/custom-validator.md` — lines: 128

## FENCE-47: 06.spring / 07-observability
- Files: 4
- Openings: 9
- `note/06.spring/07-observability/actuator.md` — lines: 236
- `note/06.spring/07-observability/log-aggregation.md` — lines: 166, 240
- `note/06.spring/07-observability/micrometer.md` — lines: 180, 521
- `note/06.spring/07-observability/prometheus-grafana.md` — lines: 298, 347, 394, 528

## FENCE-48: 06.spring / 08-annotations
- Files: 3
- Openings: 4
- `note/06.spring/08-annotations/configuration.md` — lines: 303
- `note/06.spring/08-annotations/scheduling-and-async.md` — lines: 57, 68
- `note/06.spring/08-annotations/web.md` — lines: 161

## FENCE-49: 06.spring / 09-security
- Files: 6
- Openings: 26
- `note/06.spring/09-security/README.md` — lines: 81, 98, 215
- `note/06.spring/09-security/authentication/README.md` — lines: 193, 598
- `note/06.spring/09-security/authorization/README.md` — lines: 26, 237, 279
- `note/06.spring/09-security/cors-csrf/README.md` — lines: 30, 44, 189, 217, 328, 434
- `note/06.spring/09-security/filter-chain/README.md` — lines: 28, 255, 289, 310, 376
- `note/06.spring/09-security/oauth2/README.md` — lines: 26, 44, 94, 119, 299, 347, 365

## FENCE-50: 06.spring / README.md
- Files: 1
- Openings: 3
- `note/06.spring/README.md` — lines: 69, 81, 97

## FENCE-51: 07.workflow / process-engine
- Files: 1
- Openings: 1
- `note/07.workflow/process-engine/README.md` — lines: 154

## FENCE-52: 07.workflow / temporal
- Files: 1
- Openings: 3
- `note/07.workflow/temporal/README.md` — lines: 36, 183, 275

## FENCE-53: 08.application-systems / 02-production
- Files: 3
- Openings: 4
- `note/08.application-systems/02-production/aps/README.md` — lines: 66, 124
- `note/08.application-systems/02-production/mom/README.md` — lines: 109
- `note/08.application-systems/02-production/scada/README.md` — lines: 35

## FENCE-54: 08.application-systems / 03-supply-chain
- Files: 3
- Openings: 3
- `note/08.application-systems/03-supply-chain/scm/README.md` — lines: 24
- `note/08.application-systems/03-supply-chain/srm/README.md` — lines: 121
- `note/08.application-systems/03-supply-chain/tms/README.md` — lines: 37

## FENCE-55: 08.application-systems / 04-sales-service
- Files: 1
- Openings: 1
- `note/08.application-systems/04-sales-service/oms/README.md` — lines: 24

## FENCE-56: 08.application-systems / 05-operations
- Files: 1
- Openings: 1
- `note/08.application-systems/05-operations/bi/README.md` — lines: 24

## FENCE-57: 08.application-systems / 06-specialized
- Files: 1
- Openings: 1
- `note/08.application-systems/06-specialized/lims/README.md` — lines: 50

## FENCE-58: 09.front-end / 02-language
- Files: 4
- Openings: 6
- `note/09.front-end/02-language/angular/README.md` — lines: 37, 96
- `note/09.front-end/02-language/runtime/async-await-error-handling/01-promise-error-basics.md` — lines: 20
- `note/09.front-end/02-language/runtime/async-await-error-handling/03-react-vue-production.md` — lines: 20
- `note/09.front-end/02-language/runtime/async-await-error-handling/README.md` — lines: 20, 185

## FENCE-59: 09.front-end / 07-security
- Files: 1
- Openings: 1
- `note/09.front-end/07-security/cors/README.md` — lines: 23

## FENCE-60: 09.front-end / 08-cross-platform
- Files: 1
- Openings: 1
- `note/09.front-end/08-cross-platform/mobile-tech-stack/README.md` — lines: 150

## FENCE-61: 10.big-data / 03-realtime-compute
- Files: 1
- Openings: 4
- `note/10.big-data/03-realtime-compute/01-flink-vs-spark-streaming/README.md` — lines: 34, 85, 160, 170

## FENCE-62: 10.big-data / 04-data-lake
- Files: 1
- Openings: 7
- `note/10.big-data/04-data-lake/01-iceberg-vs-delta-vs-hudi/README.md` — lines: 57, 80, 102, 133, 161, 169, 177

## FENCE-63: 10.big-data / 05-olap
- Files: 1
- Openings: 3
- `note/10.big-data/05-olap/01-clickhouse-vs-doris-vs-starrocks/README.md` — lines: 106, 196, 203

## FENCE-64: 11.ai / 01-fundamentals
- Files: 7
- Openings: 14
- `note/11.ai/01-fundamentals/dropout-in-llm/single-epoch-and-config-evidence.md` — lines: 41, 54, 96, 144, 170, 178, 222
- `note/11.ai/01-fundamentals/flash-attention/README.md` — lines: 43
- `note/11.ai/01-fundamentals/llm-basics/README.md` — lines: 58
- `note/11.ai/01-fundamentals/moe-architecture/README.md` — lines: 31
- `note/11.ai/01-fundamentals/neural-layers/README.md` — lines: 62
- `note/11.ai/01-fundamentals/rope-position-encoding/README.md` — lines: 33, 39
- `note/11.ai/01-fundamentals/transformer/README.md` — lines: 85

## FENCE-65: 11.ai / 02-technology-stack
- Files: 24
- Openings: 73
- `note/11.ai/02-technology-stack/chunking-strategies/README.md` — lines: 20, 129
- `note/11.ai/02-technology-stack/context-engineering/README.md` — lines: 38, 97
- `note/11.ai/02-technology-stack/continuous-batching/README.md` — lines: 22, 34
- `note/11.ai/02-technology-stack/embedding-models/README.md` — lines: 33
- `note/11.ai/02-technology-stack/function-calling/README.md` — lines: 23, 363
- `note/11.ai/02-technology-stack/hybrid-search/README.md` — lines: 31
- `note/11.ai/02-technology-stack/inference-frameworks/README.md` — lines: 31
- `note/11.ai/02-technology-stack/inference-metrics/README.md` — lines: 30
- `note/11.ai/02-technology-stack/kv-cache/README.md` — lines: 28, 35
- `note/11.ai/02-technology-stack/llm-inference-optimization/README.md` — lines: 49
- `note/11.ai/02-technology-stack/lost-in-middle/README.md` — lines: 22, 79, 85, 91, 98
- `note/11.ai/02-technology-stack/moe-inference/README.md` — lines: 32, 43, 51
- `note/11.ai/02-technology-stack/multimodal/cross-modal-alignment/README.md` — lines: 38
- `note/11.ai/02-technology-stack/paged-attention/README.md` — lines: 22, 34
- `note/11.ai/02-technology-stack/prompt-engineering/README.md` — lines: 25, 49, 64, 85, 107, 129, 154, 169, 190, 207, 223, 240, 257, 275
- `note/11.ai/02-technology-stack/query-rewrite/README.md` — lines: 22, 29, 36, 109
- `note/11.ai/02-technology-stack/rag-pipeline/README.md` — lines: 20
- `note/11.ai/02-technology-stack/reranker/README.md` — lines: 21, 30
- `note/11.ai/02-technology-stack/speculative-decoding/README.md` — lines: 20
- `note/11.ai/02-technology-stack/structured-output/README.md` — lines: 207
- `note/11.ai/02-technology-stack/token-billing/README.md` — lines: 25, 50, 94, 151, 166
- `note/11.ai/02-technology-stack/vector-search-at-scale/README.md` — lines: 36, 49, 54, 76, 105, 124, 146, 158, 251, 386, 402
- `note/11.ai/02-technology-stack/vector-search-trillion/README.md` — lines: 53, 68, 85, 106, 125, 172, 240
- `note/11.ai/02-technology-stack/yarn-context-extension/README.md` — lines: 22

## FENCE-66: 11.ai / 03-engineering
- Files: 25
- Openings: 61
- `note/11.ai/03-engineering/agent-spec-tools/README.md` — lines: 37, 62, 88
- `note/11.ai/03-engineering/agent-spec-tools/openspec.md` — lines: 56, 111
- `note/11.ai/03-engineering/agent-spec-tools/spec-kit.md` — lines: 71, 110
- `note/11.ai/03-engineering/agent-spec-tools/superpowers.md` — lines: 86, 106, 117
- `note/11.ai/03-engineering/ai-platforms/README.md` — lines: 112
- `note/11.ai/03-engineering/ai-platforms/vllm-vs-ollama/01-paged-attention.md` — lines: 24, 85
- `note/11.ai/03-engineering/ai-platforms/vllm-vs-ollama/02-kv-cache-management.md` — lines: 20, 68
- `note/11.ai/03-engineering/ai-platforms/vllm-vs-ollama/03-batching-strategies.md` — lines: 22, 38, 54, 84, 150
- `note/11.ai/03-engineering/ai-platforms/vllm-vs-ollama/04-quantization.md` — lines: 109, 153
- `note/11.ai/03-engineering/ai-platforms/vllm-vs-ollama/05-distributed-inference.md` — lines: 33, 67, 164
- `note/11.ai/03-engineering/ai-platforms/vllm-vs-ollama/08-decision-tree.md` — lines: 20, 134
- `note/11.ai/03-engineering/ai-platforms/vllm-vs-ollama/README.md` — lines: 20
- `note/11.ai/03-engineering/claude-code-practices/skill-design.md` — lines: 24, 65, 72, 319
- `note/11.ai/03-engineering/claude-code-practices/skill-hit-rate.md` — lines: 22, 35, 101, 111, 209
- `note/11.ai/03-engineering/frameworks/README.md` — lines: 67
- `note/11.ai/03-engineering/harness-engineering/README.md` — lines: 38, 67, 82, 118, 134
- `note/11.ai/03-engineering/llm-alignment/01-sft.md` — lines: 22, 29, 38
- `note/11.ai/03-engineering/llm-alignment/02-rlhf.md` — lines: 20, 77
- `note/11.ai/03-engineering/llm-alignment/03-dpo.md` — lines: 22, 28, 34
- `note/11.ai/03-engineering/llm-alignment/04-constitutional-ai.md` — lines: 36, 67
- `note/11.ai/03-engineering/llm-alignment/05-newer-methods.md` — lines: 123, 142
- `note/11.ai/03-engineering/llm-alignment/README.md` — lines: 59
- `note/11.ai/03-engineering/llm-production-thinking/01-thinking-paradigm.md` — lines: 35, 90
- `note/11.ai/03-engineering/llm-production-thinking/02-cost-control-and-degradation.md` — lines: 36
- `note/11.ai/03-engineering/llm-production-thinking/03-consistency-and-failure-handling.md` — lines: 20, 134

## FENCE-67: 11.ai / 03-engineering
- Files: 10
- Openings: 39
- `note/11.ai/03-engineering/llm-production-thinking/04-timeout-and-circuit-breaker.md` — lines: 84, 159, 177
- `note/11.ai/03-engineering/llm-production-thinking/05-online-monitoring.md` — lines: 117
- `note/11.ai/03-engineering/llm-production-thinking/06-decision-tree.md` — lines: 22, 39, 53, 68, 82, 152
- `note/11.ai/03-engineering/llm-production-thinking/README.md` — lines: 20, 80
- `note/11.ai/03-engineering/local-deployment/linux-deploy/README.md` — lines: 101
- `note/11.ai/03-engineering/local-deployment/open-webui/README.md` — lines: 67
- `note/11.ai/03-engineering/loop-engineering/README.md` — lines: 38, 281, 306
- `note/11.ai/03-engineering/loop-engineering/fix-prompt-templates.md` — lines: 59, 84, 113, 118, 146, 206, 237, 244, 251, 258, 265, 321, 328, 335, 342, 349
- `note/11.ai/03-engineering/loop-engineering/ide-case-studies.md` — lines: 63, 75, 97, 205
- `note/11.ai/03-engineering/loop-engineering/ralph-wiggum-loop.md` — lines: 40, 56

## FENCE-68: 11.ai / 04-architecture
- Files: 20
- Openings: 60
- `note/11.ai/04-architecture/2026-trends/README.md` — lines: 76
- `note/11.ai/04-architecture/agent-architecture/README.md` — lines: 36, 73, 165
- `note/11.ai/04-architecture/agent-context/01-chunking.md` — lines: 128
- `note/11.ai/04-architecture/agent-context/02-rag-in-agent.md` — lines: 47, 55, 82, 93, 104, 157
- `note/11.ai/04-architecture/agent-context/03-memory-strategies.md` — lines: 151
- `note/11.ai/04-architecture/agent-context/04-sliding-window-attention.md` — lines: 42, 58, 72, 84, 109, 123
- `note/11.ai/04-architecture/agent-context/05-sub-agents-decomposition.md` — lines: 20, 40, 53, 64, 75, 105, 116, 126
- `note/11.ai/04-architecture/agent-context/06-long-context-models.md` — lines: 43
- `note/11.ai/04-architecture/agent-context/07-decision-tree.md` — lines: 20, 136
- `note/11.ai/04-architecture/agent-context/README.md` — lines: 20, 88
- `note/11.ai/04-architecture/agent-execution-patterns/01-react-deep-dive.md` — lines: 20, 71, 124, 140, 153, 165, 182
- `note/11.ai/04-architecture/agent-execution-patterns/02-plan-and-execute-deep-dive.md` — lines: 20, 85, 113, 127, 141, 267
- `note/11.ai/04-architecture/agent-execution-patterns/04-selection-decision-tree.md` — lines: 20, 117, 143, 155
- `note/11.ai/04-architecture/agent-execution-patterns/05-dag-deep-dive.md` — lines: 20
- `note/11.ai/04-architecture/agent-execution-patterns/06-multi-agent-deep-dive.md` — lines: 20
- `note/11.ai/04-architecture/agent-execution-patterns/README.md` — lines: 20, 86
- `note/11.ai/04-architecture/agent-memory/README.md` — lines: 40, 212
- `note/11.ai/04-architecture/bpmn-ai-integration.md` — lines: 194
- `note/11.ai/04-architecture/llm-control-evolution/README.md` — lines: 48, 88, 127
- `note/11.ai/04-architecture/routing-architecture/README.md` — lines: 38, 312

## FENCE-69: 11.ai / 05-applications
- Files: 3
- Openings: 7
- `note/11.ai/05-applications/README.md` — lines: 38
- `note/11.ai/05-applications/automotive/README.md` — lines: 34, 52, 108, 132, 148
- `note/11.ai/05-applications/automotive/ml-to-rl/README.md` — lines: 97

## FENCE-70: 11.ai / 07-research
- Files: 4
- Openings: 9
- `note/11.ai/07-research/README.md` — lines: 40
- `note/11.ai/07-research/efficiency/README.md` — lines: 55, 148
- `note/11.ai/07-research/reasoning/README.md` — lines: 41, 47, 89, 123
- `note/11.ai/07-research/safety/README.md` — lines: 39, 150

## FENCE-71: 11.ai / 08-llmops
- Files: 13
- Openings: 56
- `note/11.ai/08-llmops/01-rag-vs-finetuning/README.md` — lines: 53, 108, 138, 150
- `note/11.ai/08-llmops/02-llmops-stack/README.md` — lines: 21, 31, 104, 316, 331
- `note/11.ai/08-llmops/03-vector-db-vs-cache/README.md` — lines: 45, 96, 155, 221, 245
- `note/11.ai/08-llmops/04-llm-evaluation/README.md` — lines: 98, 122, 198, 217, 263, 325
- `note/11.ai/08-llmops/05-llm-security/README.md` — lines: 44, 51, 180, 216, 254, 297, 375
- `note/11.ai/08-llmops/agent-evaluation/01-six-metrics.md` — lines: 24, 67, 101, 138, 166, 199
- `note/11.ai/08-llmops/agent-evaluation/02-ab-testing-design/README.md` — lines: 291
- `note/11.ai/08-llmops/agent-evaluation/04-evaluation-pipeline.md` — lines: 20
- `note/11.ai/08-llmops/agent-evaluation/05-ali-interview.md` — lines: 20, 37, 47, 64, 80, 109, 132, 139, 150, 159, 167
- `note/11.ai/08-llmops/agent-evaluation/07-selection-decision-tree.md` — lines: 20
- `note/11.ai/08-llmops/agent-evaluation/09-rag-evaluation/README.md` — lines: 166, 184
- `note/11.ai/08-llmops/agent-evaluation/README.md` — lines: 34, 109, 180
- `note/11.ai/08-llmops/agentic-search-vs-rag/README.md` — lines: 24, 67, 96, 220

## FENCE-72: 12.story / 02-system-architecture-evolution.md
- Files: 1
- Openings: 2
- `note/12.story/02-system-architecture-evolution.md` — lines: 639, 659

## FENCE-73: 12.story / 37-vector-database-and-embedding.md
- Files: 1
- Openings: 3
- `note/12.story/37-vector-database-and-embedding.md` — lines: 665, 709, 729

## FENCE-74: 12.story / 42-ai-engineer-responsibility.md
- Files: 1
- Openings: 1
- `note/12.story/42-ai-engineer-responsibility.md` — lines: 86

## FENCE-75: 12.story / 43-ai-productivity-paradox.md
- Files: 1
- Openings: 6
- `note/12.story/43-ai-productivity-paradox.md` — lines: 74, 90, 103, 113, 144, 162

## FENCE-76: 12.story / 44-tech-debt-career-trap.md
- Files: 1
- Openings: 6
- `note/12.story/44-tech-debt-career-trap.md` — lines: 43, 77, 93, 108, 124, 176

## FENCE-77: 12.story / 45-skill-scheduling-restaurant.md
- Files: 1
- Openings: 7
- `note/12.story/45-skill-scheduling-restaurant.md` — lines: 26, 76, 137, 152, 168, 226, 232

## FENCE-78: 12.story / 46-llm-inference.md
- Files: 1
- Openings: 6
- `note/12.story/46-llm-inference.md` — lines: 13, 55, 73, 79, 95, 119

## FENCE-79: 12.story / STORY-FORMAT-SPEC.md
- Files: 1
- Openings: 2
- `note/12.story/STORY-FORMAT-SPEC.md` — lines: 22, 226

## FENCE-80: 13.split-hairs / 01.java
- Files: 23
- Openings: 62
- `note/13.split-hairs/01.java/aqs/README.md` — lines: 97, 114, 139
- `note/13.split-hairs/01.java/concurrency-vs-parallelism/README.md` — lines: 71, 185, 220
- `note/13.split-hairs/01.java/concurrent-hashmap/README.md` — lines: 40, 57
- `note/13.split-hairs/01.java/cpu-spike-troubleshooting/README.md` — lines: 15, 43, 79, 165, 198, 271
- `note/13.split-hairs/01.java/error-vs-exception/README.md` — lines: 46
- `note/13.split-hairs/01.java/generics-erasure/README.md` — lines: 135
- `note/13.split-hairs/01.java/hashmap-resizing/README.md` — lines: 43, 83, 213
- `note/13.split-hairs/01.java/jvm-memory-pitfall/README.md` — lines: 37, 79, 89, 105, 149, 191, 228, 258, 324
- `note/13.split-hairs/01.java/jvm-memory/README.md` — lines: 160
- `note/13.split-hairs/01.java/new-string/README.md` — lines: 108
- `note/13.split-hairs/01.java/parent-child-thread/README.md` — lines: 146
- `note/13.split-hairs/01.java/questions/README.md` — lines: 40, 48, 159, 166, 172, 179, 187, 207, 239, 248, 256
- `note/13.split-hairs/01.java/record-t/README.md` — lines: 220
- `note/13.split-hairs/01.java/reflection/README.md` — lines: 60, 92
- `note/13.split-hairs/01.java/replace-synchronized-with-atomic/README.md` — lines: 59, 66, 227
- `note/13.split-hairs/01.java/reuse-of-stringbuilder/README.md` — lines: 189
- `note/13.split-hairs/01.java/spi/README.md` — lines: 41, 91, 180
- `note/13.split-hairs/01.java/synchronized-lock-upgrade/README.md` — lines: 71
- `note/13.split-hairs/01.java/thread-sequential-execution/README.md` — lines: 46, 189
- `note/13.split-hairs/01.java/threadlocal/README.md` — lines: 73
- `note/13.split-hairs/01.java/try-catch-performance/README.md` — lines: 67
- `note/13.split-hairs/01.java/virtual-threads/README.md` — lines: 54
- `note/13.split-hairs/01.java/volatile/README.md` — lines: 50, 129, 168, 176

## FENCE-81: 13.split-hairs / 02.computer-basics
- Files: 5
- Openings: 26
- `note/13.split-hairs/02.computer-basics/greedy-algorithms/README.md` — lines: 53
- `note/13.split-hairs/02.computer-basics/port-reuse-so-reuseport/README.md` — lines: 153, 182
- `note/13.split-hairs/02.computer-basics/sensitive-word-filter/README.md` — lines: 51, 71, 85, 106, 133, 153, 177, 203, 239, 260, 419
- `note/13.split-hairs/02.computer-basics/sse-vs-websocket/README.md` — lines: 15, 41, 62, 74
- `note/13.split-hairs/02.computer-basics/tcp-handshake-teardown/README.md` — lines: 42, 73, 99, 131, 140, 167, 175, 202

## FENCE-82: 13.split-hairs / 03.database
- Files: 20
- Openings: 69
- `note/13.split-hairs/03.database/README.md` — lines: 77, 119
- `note/13.split-hairs/03.database/bplus-tree/README.md` — lines: 125, 164, 190, 195, 200, 223
- `note/13.split-hairs/03.database/cache-penetration-breakdown-avalanche/README.md` — lines: 15
- `note/13.split-hairs/03.database/deadlock/README.md` — lines: 28, 53, 160
- `note/13.split-hairs/03.database/mvcc/README.md` — lines: 44, 109, 186
- `note/13.split-hairs/03.database/mysql-deep-pagination/README.md` — lines: 54
- `note/13.split-hairs/03.database/mysql-index-failure/README.md` — lines: 202
- `note/13.split-hairs/03.database/mysql-isolation/README.md` — lines: 59, 68, 177, 187
- `note/13.split-hairs/03.database/mysql-join/README.md` — lines: 188, 207, 218, 227, 276, 285, 294
- `note/13.split-hairs/03.database/mysql-select-all-big-table/README.md` — lines: 63, 102
- `note/13.split-hairs/03.database/mysql-time-types/README.md` — lines: 189
- `note/13.split-hairs/03.database/mysql-tuning/README.md` — lines: 18, 313
- `note/13.split-hairs/03.database/redis-big-key/README.md` — lines: 51, 69, 96, 163, 214
- `note/13.split-hairs/03.database/redis-cluster/README.md` — lines: 15, 140, 169, 246
- `note/13.split-hairs/03.database/redis-eviction/README.md` — lines: 41, 117, 131, 181, 212, 226, 235, 251, 264
- `note/13.split-hairs/03.database/redis-persistence/README.md` — lines: 15, 48, 85, 120, 148, 186, 198, 231
- `note/13.split-hairs/03.database/redis-search/README.md` — lines: 30, 181
- `note/13.split-hairs/03.database/redis-single-thread/README.md` — lines: 53, 80, 124, 142, 207, 248
- `note/13.split-hairs/03.database/replication-lag/README.md` — lines: 46
- `note/13.split-hairs/03.database/sharding-resize/README.md` — lines: 60

## FENCE-83: 13.split-hairs / 04.system-design
- Files: 17
- Openings: 52
- `note/13.split-hairs/04.system-design/cache-consistency/README.md` — lines: 84, 196, 234, 246
- `note/13.split-hairs/04.system-design/cap-theorem/README.md` — lines: 17, 178
- `note/13.split-hairs/04.system-design/circuit-breaker/README.md` — lines: 15
- `note/13.split-hairs/04.system-design/distributed-id/README.md` — lines: 93, 115, 192, 230
- `note/13.split-hairs/04.system-design/distributed-lock/README.md` — lines: 141
- `note/13.split-hairs/04.system-design/distributed-transaction/README.md` — lines: 15, 173, 248
- `note/13.split-hairs/04.system-design/file-upload/README.md` — lines: 52, 144, 151, 158
- `note/13.split-hairs/04.system-design/idempotency/README.md` — lines: 15
- `note/13.split-hairs/04.system-design/microservices-vs-monolith/README.md` — lines: 107, 143, 163, 185, 210, 234, 261, 326, 342, 357, 407
- `note/13.split-hairs/04.system-design/mq-backlog/README.md` — lines: 15
- `note/13.split-hairs/04.system-design/multi-tenant-saas/README.md` — lines: 74, 164, 199
- `note/13.split-hairs/04.system-design/payment-message-lost/README.md` — lines: 37, 152
- `note/13.split-hairs/04.system-design/product-search/README.md` — lines: 44, 57, 78, 128, 202
- `note/13.split-hairs/04.system-design/rate-limiting/README.md` — lines: 15
- `note/13.split-hairs/04.system-design/seckill-without-redis/README.md` — lines: 50, 121
- `note/13.split-hairs/04.system-design/still-need-rocketmq/README.md` — lines: 15, 216, 253
- `note/13.split-hairs/04.system-design/url-shortener/README.md` — lines: 44, 67, 94, 216

## FENCE-84: 13.split-hairs / 05.security
- Files: 10
- Openings: 29
- `note/13.split-hairs/05.security/access-control-design/README.md` — lines: 44, 56, 133, 171, 262, 333
- `note/13.split-hairs/05.security/cors-preflight/README.md` — lines: 86
- `note/13.split-hairs/05.security/encryption-at-rest-transit/README.md` — lines: 80
- `note/13.split-hairs/05.security/https-handshake/README.md` — lines: 83
- `note/13.split-hairs/05.security/jwt-vs-session/README.md` — lines: 82
- `note/13.split-hairs/05.security/oauth2-flow/README.md` — lines: 54, 83
- `note/13.split-hairs/05.security/owasp-top10/README.md` — lines: 77
- `note/13.split-hairs/05.security/rate-limiting-algorithms/README.md` — lines: 95
- `note/13.split-hairs/05.security/sso/README.md` — lines: 46, 56, 101, 138, 160, 186, 213, 239, 264, 322, 337, 350, 362, 417
- `note/13.split-hairs/05.security/xss-csrf-csp/README.md` — lines: 81

## FENCE-85: 13.split-hairs / 06.spring
- Files: 7
- Openings: 11
- `note/13.split-hairs/06.spring/async-pitfalls/README.md` — lines: 53
- `note/13.split-hairs/06.spring/auto-configuration/README.md` — lines: 139, 220, 264
- `note/13.split-hairs/06.spring/cache-degradation/README.md` — lines: 159, 198, 261
- `note/13.split-hairs/06.spring/circular-dependency/README.md` — lines: 111
- `note/13.split-hairs/06.spring/clarify-various-o/README.md` — lines: 217
- `note/13.split-hairs/06.spring/spring-mvc-flow/README.md` — lines: 15
- `note/13.split-hairs/06.spring/transactional-propagation/README.md` — lines: 54

## FENCE-86: 13.split-hairs / 09.front-end
- Files: 14
- Openings: 40
- `note/13.split-hairs/09.front-end/async-await-try-catch/README.md` — lines: 112, 139, 159, 180, 201, 223, 247, 423
- `note/13.split-hairs/09.front-end/cors/README.md` — lines: 15, 52, 100
- `note/13.split-hairs/09.front-end/css-button-styling/README.md` — lines: 153, 278
- `note/13.split-hairs/09.front-end/css-render-blocking/README.md` — lines: 49
- `note/13.split-hairs/09.front-end/from-url-to-page/README.md` — lines: 15, 71, 81, 93
- `note/13.split-hairs/09.front-end/http-cache/README.md` — lines: 15, 74, 95, 99, 116, 120, 226
- `note/13.split-hairs/09.front-end/https-handshake/README.md` — lines: 15, 131
- `note/13.split-hairs/09.front-end/message/README.md` — lines: 54, 59, 64, 69, 75, 238
- `note/13.split-hairs/09.front-end/playwright-vs-selenium/README.md` — lines: 116
- `note/13.split-hairs/09.front-end/prototype-chain/README.md` — lines: 102
- `note/13.split-hairs/09.front-end/reflow-repaint/README.md` — lines: 54
- `note/13.split-hairs/09.front-end/script-async-defer/README.md` — lines: 91
- `note/13.split-hairs/09.front-end/this-binding/README.md` — lines: 160
- `note/13.split-hairs/09.front-end/virtual-dom-diff/README.md` — lines: 150, 211

## FENCE-87: 13.split-hairs / 11.ai
- Files: 25
- Openings: 93
- `note/13.split-hairs/11.ai/agent-ab-testing/README.md` — lines: 240, 275
- `note/13.split-hairs/11.ai/agent-dag-vs-react/README.md` — lines: 95
- `note/13.split-hairs/11.ai/ai-code-churn/README.md` — lines: 66, 72, 102, 116, 128
- `note/13.split-hairs/11.ai/ai-coding-roi/README.md` — lines: 155, 166, 173, 180
- `note/13.split-hairs/11.ai/ai-thinking/README.md` — lines: 121
- `note/13.split-hairs/11.ai/claude-code-agentic-search/README.md` — lines: 59
- `note/13.split-hairs/11.ai/context-engineering-interview/README.md` — lines: 44
- `note/13.split-hairs/11.ai/function-calling/README.md` — lines: 46, 137, 189, 209, 232, 253
- `note/13.split-hairs/11.ai/hallucination/README.md` — lines: 15, 164
- `note/13.split-hairs/11.ai/harness-engineering/README.md` — lines: 47
- `note/13.split-hairs/11.ai/incremental-embedding/README.md` — lines: 221, 257
- `note/13.split-hairs/11.ai/inference-engine-selection/README.md` — lines: 56, 77, 92, 120, 149, 174, 191, 210, 237, 256, 415
- `note/13.split-hairs/11.ai/long-context-agent-strategy/README.md` — lines: 94, 130, 151, 174, 198, 226, 247, 315, 329, 343, 404
- `note/13.split-hairs/11.ai/loop-engineering/README.md` — lines: 49
- `note/13.split-hairs/11.ai/multi-agent-shared-memory/README.md` — lines: 195, 232
- `note/13.split-hairs/11.ai/multi-agent-system-design/README.md` — lines: 182, 216
- `note/13.split-hairs/11.ai/multi-turn-tool-reasoning/README.md` — lines: 179, 213
- `note/13.split-hairs/11.ai/production-thinking-5q/README.md` — lines: 55, 68, 90, 108, 125, 149, 175, 202, 229, 267, 332, 344, 356, 402
- `note/13.split-hairs/11.ai/rag-out-of-domain-rejection/README.md` — lines: 67, 239, 280
- `note/13.split-hairs/11.ai/rag/README.md` — lines: 39
- `note/13.split-hairs/11.ai/react-vs-plan-execute/README.md` — lines: 65, 80, 115, 144, 173, 197, 223, 245, 267, 342, 351, 360, 369, 421
- `note/13.split-hairs/11.ai/skill-design/README.md` — lines: 46
- `note/13.split-hairs/11.ai/skill-hit-rate/README.md` — lines: 52
- `note/13.split-hairs/11.ai/temperature-zero-myth/README.md` — lines: 73, 194, 233
- `note/13.split-hairs/11.ai/token/README.md` — lines: 40

## FENCE-88: 13.split-hairs / 11.ai
- Files: 3
- Openings: 16
- `note/13.split-hairs/11.ai/transformer/README.md` — lines: 32
- `note/13.split-hairs/11.ai/vector-search-at-scale/README.md` — lines: 65, 70, 84, 89, 109, 134, 168, 177
- `note/13.split-hairs/11.ai/vector-search-trillion/README.md` — lines: 79, 97, 118, 139, 160, 213, 293

## FENCE-89: 13.split-hairs / QUESTION-FORMAT-SPEC.md
- Files: 1
- Openings: 2
- `note/13.split-hairs/QUESTION-FORMAT-SPEC.md` — lines: 57, 73

## FENCE-90: 14.project-management / agile-metrics
- Files: 1
- Openings: 6
- `note/14.project-management/agile-metrics/README.md` — lines: 79, 100, 126, 141, 186, 221

## FENCE-91: 14.project-management / risk-register
- Files: 1
- Openings: 2
- `note/14.project-management/risk-register/README.md` — lines: 57, 108

## FENCE-92: CONTRIBUTING.md / _root
- Files: 1
- Openings: 4
- `note/CONTRIBUTING.md` — lines: 32, 48, 94, 256
