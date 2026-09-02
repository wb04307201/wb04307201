#!/usr/bin/env python3
"""
test_qa_s35.py — note-knowledge-qa §3.5 + §3.5.1 标准化测试模板

Session 9 实测教训：
- 显示 bug：所有 v2 Top1 实际都是模块 README，但脚本只显示 basename 误导
- v3 排除模块 README 反效果：真实命中率从 50% 掉到 7%
- 修复：完整路径 + 真实相关判定（§3.5.1 测试必做）

用法：
  python scripts/test_qa_s35.py                       # 全 75 场景
  python scripts/test_qa_s35.py --round 1            # 仅第 1 轮
  python scripts/test_qa_s35.py --path note/...      # 自定义路径
"""
import os, re, glob, sys, argparse
if os.name == 'nt':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


# ============ §3.5.1 v2（保留，50% 真实命中）============

def suggest_v2(path, top=3):
    """§3.5.1 v2 算法（保留为默认，因 v3 反效果）"""
    name = os.path.basename(path).replace('.md', '').lower()
    dir_parts = path.replace('note/', '').split('/')[:-1]
    parent_dir = dir_parts[-1].lower() if dir_parts else ''
    keywords = re.findall(r'[A-Za-z]+|[一-鿿]{2,}', name)
    scores = {}
    for f in glob.glob('note/**/*.md', recursive=True):
        if '.health-tmp' in f.replace(os.sep, '/'):
            continue
        if f.replace(os.sep, '/') in ['note/README.md', 'note/SPEC.md']:
            continue
        s = 0
        fn = os.path.basename(f).replace('.md', '').lower()
        if name == fn:
            s += 10
        elif name in fn or fn in name:
            s += 5
        fd = os.path.dirname(f).replace(os.sep, '/').lower()
        if parent_dir and parent_dir in fd:
            s += 5
        s += sum(2 if k.lower() in f.lower() else 0 for k in keywords)
        if s > 0:
            scores[f] = s
    return sorted(scores.items(), key=lambda x: -x[1])[:top]


def is_relevant(top1_path, missing_path):
    """真实相关判定：非模块 README + 含原关键词"""
    short = top1_path.replace(os.sep, '/').replace('note/', '')
    is_module_readme = (short.count('/') == 1 and short.endswith('/README.md'))
    if is_module_readme:
        return False
    kws = re.findall(r'[A-Za-z]+|[一-鿿]{2,}', os.path.basename(missing_path).replace('.md', ''))
    return any(k.lower() in short.lower() for k in kws)


# ============ 75 场景数据 ============

ROUND_1 = [
    ('Redis 持久化机制', ['note/03.data-stack/01-database/07-redis/README.md']),
    ('MySQL 索引原理', ['note/03.data-stack/01-database/05-mysql/README.md']),
    ('Java 集合框架', ['note/01.java-and-jvm/01-language/collection/README.md']),
    ('Spring Boot 自动配置', ['note/04.spring-backend/02-boot/auto-configuration.md']),
    ('MVCC 实现原理', ['note/01.java-and-jvm/02-jvm/mvcc/README.md',
                          'note/12.interview/01.java/mvcc/README.md']),
    ('HashMap 线程不安全', ['note/01.java-and-jvm/01-language/collection/hashmap.md',
                              'note/12.interview/01.java/hashmap-thread-unsafe/README.md']),
    ('TCP 三次握手', ['note/02.cs-foundations/03-network/01-tcp-ip/README.md',
                       'note/12.interview/02.computer-basics/tcp-handshake-teardown/README.md']),
    ('事务隔离级别', ['note/03.data-stack/01-database/transaction/README.md',
                       'note/12.interview/03.database/transaction-isolation/README.md']),
    ('Kafka 在微服务', ['note/06.distributed-systems/04-high-performance/mq/README.md',
                          'note/06.distributed-systems/02-distributed/api-gateway/README.md']),
    ('RAG 向量检索', ['note/09.ai-applications/rag/rag-system-design/README.md',
                       'note/02.cs-foundations/01-algorithms/vector-search/README.md']),
    ('AI Agent 与微服务', ['note/09.ai-applications/agent/agent-architecture/README.md',
                              'note/06.distributed-systems/02-distributed/microservices/README.md']),
    ('SQL 优化与版本', ['note/03.data-stack/01-database/sql-optimization/README.md',
                          'note/01.java-and-jvm/version/java-17/README.md']),
    ('Spring Cloud Gateway 限流', ['note/04.spring-backend/03-cloud/gateway.md',
                                      'note/06.distributed-systems/03-high-availability/rate-limiting/README.md',
                                      'note/04.spring-backend/03-spring-cloud/README.md']),
    ('OAuth2 vs JWT', ['note/06.distributed-systems/05-security/jwt-security/README.md',
                       'note/04.spring-backend/05-security/oauth2.md']),
    ('分布式锁 vs DB锁', ['note/06.distributed-systems/02-distributed/distributed-lock/README.md',
                          'note/03.data-stack/01-database/transaction/README.md',
                          'note/04.spring-backend/02-boot/flexible-lock.md']),
    ('BPM 工作流引擎', ['note/07.devops-and-tools/02-workflow/temporal/README.md',
                          'note/10.business-systems/05-operations/bpm/README.md']),
    ('高并发场景的演进', ['note/13.story/04-peak-traffic-defense.md',
                            'note/06.distributed-systems/04-high-performance/load-balance/README.md']),
    ('架构演进故事', ['note/13.story/02-system-architecture-evolution.md',
                       'note/06.distributed-systems/01-foundation/02-evolution/README.md']),
    ('AI 致命三件套', ['note/13.story/31-ai-fatal-trio.md',
                        'note/09.ai-applications/prompts/prompt-engineering/README.md']),
    ('高频面试：分布式 ID', ['note/12.interview/04.system-design/distributed-id/README.md']),
    ('Vue 响应式原理', ['note/05.frontend/03-frameworks/vue/README.md',
                          'note/12.interview/09.front-end/vue-reactivity/README.md']),
    ('CSS + a11y', ['note/05.frontend/01-foundation/css-engineering/README.md',
                     'note/05.frontend/a11y/README.md']),
]

ROUND_2 = [
    ('Redis 集群 vs Redis Cluster', ['note/03.data-stack/01-database/07-redis/README.md',
                                          'note/12.interview/03.database/redis-cluster/README.md']),
    ('Spring Boot 启动原理', ['note/04.spring-backend/02-boot/README.md',
                                  'note/04.spring-backend/02-boot/application-bootstrap.md']),
    ('Kafka 实战', ['note/06.distributed-systems/04-high-performance/mq/README.md',
                       'note/10.business-systems/03-supply-chain/scm/README.md']),
    ('Git 命令', ['note/07.devops-and-tools/01-tools/devops/git/README.md',
                    'note/07.devops-and-tools/01-tools/devops/git-advanced/README.md']),
    ('SQL 优化（同名章节）', ['note/03.data-stack/01-database/sql-optimization/README.md',
                                'note/03.data-stack/02-big-data/05-olap/sql-tuning/README.md']),
    ('分布式锁实现', ['note/12.interview/04.system-design/distributed-id/README.md',
                       'note/12.interview/03.database/redis-distributed-lock/README.md']),
    ('JVM 调优实战', ['note/12.interview/01.java/jvm-tuning/README.md',
                       'note/01.java-and-jvm/02-jvm/05-gc-tuning/README.md']),
    ('分布式事务', ['note/12.interview/04.system-design/distributed-transaction/README.md',
                     'note/06.distributed-systems/02-distributed/distributed-transaction/README.md']),
    ('Spring IOC 原理', ['note/12.interview/06.spring/ioc/README.md',
                          'note/04.spring-backend/01-core/ioc/README.md']),
    ('数据库分库分表', ['note/12.interview/03.database/sharding/README.md',
                          'note/03.data-stack/01-database/13-sharding/README.md']),
    ('架构演进 + 缓存故事', ['note/13.story/02-system-architecture-evolution.md',
                                 'note/13.story/04-peak-traffic-defense.md',
                                 'note/06.distributed-systems/04-high-performance/cache-patterns/README.md']),
    ('AI Agent 餐厅故事', ['note/13.story/38-rag-retrieval-augmented-generation.md',
                             'note/13.story/37-vector-database-and-embedding.md']),
    ('项目管理故事', ['note/13.story/20-board-revolution.md',
                       'note/13.story/22-outsourcing-trap.md',
                       'note/11.product-and-pm/agile-metrics/README.md']),
    ('DevOps 转型故事', ['note/13.story/06-distributed-system-evolution.md',
                           'note/07.devops-and-tools/01-tools/devops/07-cicd-adoption/README.md']),
    ('安全合规故事', ['note/13.story/45-black-swan.md',
                       'note/06.distributed-systems/05-security/jwt-security/README.md']),
    ('Kafka Streams 实战', ['note/06.distributed-systems/04-high-performance/mq/kafka-streams/README.md',
                              'note/06.distributed-systems/04-high-performance/mq/kafka/README.md']),
    ('Spring Security OAuth2 细节', ['note/04.spring-backend/09-security/oauth2/jwt-bearer/README.md',
                                          'note/04.spring-backend/09-security/oauth2/README.md']),
    ('JVM G1 收集器', ['note/01.java-and-jvm/02-jvm/05-gc-tuning/g1-collector/README.md',
                        'note/01.java-and-jvm/02-jvm/05-gc-tuning/README.md']),
    ('MySQL 主从复制', ['note/03.data-stack/01-database/05-mysql/replication/README.md',
                        'note/03.data-stack/01-database/05-mysql/README.md']),
    ('A11y 无障碍专题', ['note/05.frontend/a11y/wcag/README.md',
                          'note/05.frontend/a11y/README.md']),
    ('锁主题（歧义大）', ['note/06.distributed-systems/02-distributed/distributed-lock/README.md',
                          'note/04.spring-backend/02-boot/flexible-lock.md',
                          'note/12.interview/03.database/redis-distributed-lock/README.md']),
    ('事务主题', ['note/03.data-stack/01-database/transaction/README.md',
                    'note/06.distributed-systems/02-distributed/distributed-transaction/README.md']),
    ('缓存主题', ['note/03.data-stack/01-database/07-redis/README.md',
                    'note/10.business-systems/05-operations/CHMCache/README.md']),
    ('部署主题', ['note/07.devops-and-tools/01-tools/devops/docker/README.md',
                    'note/07.devops-and-tools/03-cloud/k8s/README.md']),
    ('消息主题', ['note/06.distributed-systems/04-high-performance/mq/README.md',
                    'note/10.business-systems/01-rd-innovation/notification-system/README.md']),
    ('Java 21 新特性', ['note/01.java-and-jvm/version/java-21/README.md',
                          'note/01.java-and-jvm/version/java-21-virtual-threads/README.md']),
    ('Spring Boot 3.x 新特性', ['note/04.spring-backend/version/spring-boot-3/README.md',
                                 'note/04.spring-backend/version/README.md']),
    ('A 股技术（特殊字符）', ['note/10.business-systems/05-operations/erp/README.md',
                              'note/10.business-systems/05-operations/mes/README.md']),
]

ROUND_3 = [
    ('note 总目录', ['note/README.md']),
    ('note 全局规范', ['note/SPEC.md']),
    ('Java-and-jvm 模块规范', ['note/01.java-and-jvm/SPEC.md']),
    ('AI 应用模块规范', ['note/09.ai-applications/SPEC.md']),
    ('12.interview 格式规范', ['note/12.interview/QUESTION-FORMAT-SPEC.md']),
    ('性能优化', ['note/03.data-stack/04-performance-optimization/README.md']),
    ('微服务架构', ['note/06.distributed-systems/02-microservices/README.md']),
    ('高可用设计', ['note/06.distributed-systems/03-high-availability/README.md']),
    ('可观测性', ['note/06.distributed-systems/08-observability/README.md']),
    ('存储引擎', ['note/03.data-stack/01-database/06-storage-engine/README.md']),
    ('Java 17 新特性', ['note/01.java-and-jvm/version/java-17/README.md']),
    ('Java 21 虚拟线程', ['note/01.java-and-jvm/version/java-21/virtual-threads.md']),
    ('Spring Boot 3 vs 4', ['note/04.spring-backend/02-boot/README.md']),
    ('Node 22 vs 20', ['note/07.devops-and-tools/01-tools/devops/node/README.md']),
    ('Python 3.12', ['note/07.devops-and-tools/01-tools/devops/python/README.md']),
    ('Vue 3 响应式', ['note/05.frontend/03-frameworks/vue-3-reactivity/README.md']),
    ('React 18 并发', ['note/05.frontend/03-frameworks/react-18-concurrent/README.md']),
    ('Spring 6 新特性', ['note/04.spring-backend/version/spring-6/README.md']),
    ('JDK 11 vs 17', ['note/01.java-and-jvm/version/jdk11/README.md']),
    ('Kubernetes 1.30', ['note/07.devops-and-tools/03-cloud/k8s-1.30/README.md']),
    ('数据库调优', ['note/03.data-stack/01-database/05-mysql/performance-tuning/README.md']),
    ('JVM 调优实战', ['note/01.java-and-jvm/02-jvm/jvm-tuning/README.md']),
    ('部署策略', ['note/07.devops-and-tools/01-tools/devops/deployment/README.md']),
    ('监控告警', ['note/07.devops-and-tools/04-observability/monitoring/README.md']),
    ('故障排查', ['note/07.devops-and-tools/04-observability/troubleshooting/README.md']),
]

ROUND_4 = [
    # S: 12.interview 子目录（5）
    ('volatile 关键字', ['note/12.interview/01.java/volatile/README.md']),
    ('synchronized vs Lock', ['note/12.interview/01.java/synchronized-vs-lock/README.md']),
    ('B+ 树索引原理', ['note/12.interview/03.database/b-plus-tree/README.md']),
    ('分布式限流算法', ['note/12.interview/04.system-design/rate-limiting/README.md']),
    ('幂等设计', ['note/12.interview/04.system-design/idempotency/README.md']),
    # T: 特殊字符（5）
    ('kafka-3.x', ['note/09.ai-applications/llm-inference/kafka-3.x/README.md']),
    ('raft 算法', ['note/06.distributed-systems/02-distributed/consensus-algorithms/raft/README.md']),
    ('spring-boot-starter', ['note/04.spring-backend/02-boot/spring-boot-starter/README.md']),
    ('java 21', ['note/01.java-and-jvm/version/java-21/README.md']),
    ('mybatis 3', ['note/03.data-stack/01-database/05-mybatis/README.md']),
    # U: 综述 vs 长文（5）
    ('微服务治理综述', ['note/06.distributed-systems/02-distributed/microservices/README.md']),
    ('Java 集合框架综述', ['note/01.java-and-jvm/01-language/collection/README.md']),
    ('Spring IoC 综述', ['note/04.spring-backend/01-core/ioc/README.md']),
    ('分布式 ID 综述', ['note/06.distributed-systems/02-distributed/distributed-id/README.md']),
    ('Spring Boot 自动配置综述', ['note/04.spring-backend/02-boot/auto-configuration/README.md']),
    # V: 跨年版本（5）
    ('Java 8 新特性', ['note/01.java-and-jvm/version/java-8/README.md']),
    ('Java 11 新特性', ['note/01.java-and-jvm/version/java-11/README.md']),
    ('Spring 5 vs 6', ['note/04.spring-backend/version/spring-5/README.md']),
    ('ES 7 vs 8', ['note/03.data-stack/01-database/08-nosql/elasticsearch-8/README.md']),
    ('Vue 2 → 3 迁移', ['note/05.frontend/03-frameworks/vue-2-to-3/README.md']),
    # W: 业务系统（5）
    ('ERP 系统', ['note/10.business-systems/05-operations/erp/README.md']),
    ('MES 制造执行', ['note/10.business-systems/05-operations/mes/README.md']),
    ('WMS 仓储', ['note/10.business-systems/05-operations/wms/README.md']),
    ('CRM 客户关系', ['note/10.business-systems/01-rd-innovation/crm/README.md']),
    ('OA 办公自动化', ['note/10.business-systems/05-operations/oa/README.md']),
]

ROUND_5 = [
    # X: 复合路径（5）
    ('Java 集合框架 → 12.interview', ['note/12.interview/01.java/java-collection/README.md']),
    ('Spring Boot 启动 → 04 启动', ['note/04.spring-backend/02-boot/02-bootstrap/README.md']),
    ('Redis 集群 → 12.interview', ['note/12.interview/03.database/redis-cluster-mode/README.md']),
    ('Kafka 生产 → 09 AI 应用', ['note/09.ai-applications/llm-inference/kafka-producer/README.md']),
    ('ZooKeeper → 06 分布式', ['note/06.distributed-systems/02-distributed/zookeeper/README.md']),
    # Y: 中文主题（5）
    ('事务', ['note/03.data-stack/01-database/01-事务/README.md']),
    ('锁', ['note/06.distributed-systems/02-distributed/01-锁/README.md']),
    ('缓存', ['note/03.data-stack/02-cache/01-缓存/README.md']),
    ('消息队列', ['note/06.distributed-systems/04-high-performance/01-消息队列/README.md']),
    ('数据库', ['note/03.data-stack/01-database/01-数据库/README.md']),
    # Z: 案例研究（5）
    ('Salesforce Agentforce 案例', ['note/09.ai-applications/agent/case-studies/salesforce-agentforce/README.md']),
    ('Shopify AI Agent 案例', ['note/09.ai-applications/agent/case-studies/shopify-ai-agent/README.md']),
    ('AI 编码 Claude Code 实践', ['note/09.ai-applications/agent/coding-agents/claude-code/README.md']),
    ('电商系统架构案例', ['note/10.business-systems/02-e-commerce/architecture/README.md']),
    ('外卖系统案例', ['note/10.business-systems/02-e-commerce/food-delivery.md']),
    # AA: 协议/标准（5）
    ('HTTP/3 协议', ['note/02.cs-foundations/03-network/02-http-3/README.md']),
    ('gRPC 协议', ['note/06.distributed-systems/02-distributed/rpc/grpc.md']),
    ('WebSocket 协议', ['note/05.frontend/03-network/websocket/README.md']),
    ('OAuth 2.0 协议', ['note/06.distributed-systems/05-security/oauth2-protocol/README.md']),
    ('TLS/SSL 协议', ['note/02.cs-foundations/03-network/04-tls/README.md']),
    # AB: 极端路径（5）
    ('Spring Security 嵌套', ['note/04.spring-backend/09-security/oauth2/resource-server/jwt/README.md']),
    ('前端工程化深度', ['note/05.frontend/04-engineering/vite/advanced-config/README.md']),
    ('DevOps K8s Helm', ['note/07.devops-and-tools/03-cloud/k8s/helm-chart/README.md']),
    ('测试/单元测试', ['note/07.devops-and-tools/05-quality/unit-test/README.md']),
    ('Java 字节码操作', ['note/01.java-and-jvm/01-language/bytecode/README.md']),
]


# ============ 测试运行 ============

def run_round(name, scenarios, verbose=False):
    """运行一轮测试"""
    total_refs = 0
    ok_refs = 0
    fail_refs = 0
    real_relevant = 0
    real_total = 0
    for q, refs in scenarios:
        for ref in refs:
            total_refs += 1
            if os.path.isfile(ref):
                ok_refs += 1
            else:
                fail_refs += 1
                r = suggest_v2(ref, 1)
                if r:
                    real_total += 1
                    if is_relevant(r[0][0], ref):
                        real_relevant += 1
                    if verbose:
                        print('  - {!r} -> {!r} ({})'.format(
                            ref.replace('note/', ''),
                            r[0][0].replace(os.sep, '/').replace('note/', ''),
                            r[0][1]))

    print('  {}: 总引用 {} | 正确 {} | 失效 {} | §3.5.1 Top1 真实相关 {}/{} = {:.0f}%'.format(
        name, total_refs, ok_refs, fail_refs,
        real_relevant, real_total,
        real_relevant/real_total*100 if real_total else 0,
    ))
    return {
        'total': total_refs,
        'ok': ok_refs,
        'fail': fail_refs,
        'relevant': real_relevant,
        'relevant_total': real_total,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--round', type=int, choices=[1, 2, 3, 4, 5], help='仅跑某一轮')
    parser.add_argument('--verbose', action='store_true', help='打印所有失效')
    parser.add_argument('--path', help='自定义单路径测试')
    args = parser.parse_args()

    print('=' * 70)
    print('note-knowledge-qa §3.5 + §3.5.1 - {} 场景测试'.format(
        '自定义' if args.path else '125 (5 轮)'))
    print('=' * 70)

    rounds = []
    if not args.round or args.round == 1:
        rounds.append(('Round 1', ROUND_1))
    if not args.round or args.round == 2:
        rounds.append(('Round 2', ROUND_2))
    if not args.round or args.round == 3:
        rounds.append(('Round 3', ROUND_3))
    if not args.round or args.round == 4:
        rounds.append(('Round 4', ROUND_4))
    if not args.round or args.round == 5:
        rounds.append(('Round 5', ROUND_5))

    total = {'refs': 0, 'ok': 0, 'fail': 0, 'rel': 0, 'rel_t': 0}
    for name, sc_list in rounds:
        r = run_round(name, sc_list, args.verbose)
        total['refs'] += r['total']
        total['ok'] += r['ok']
        total['fail'] += r['fail']
        total['rel'] += r['relevant']
        total['rel_t'] += r['relevant_total']

    if not args.path:
        print()
        print('=' * 70)
        print('=== 合计 ===')
        print('总引用: {} | 正确: {} ({:.0f}%) | 失效: {}'.format(
            total['refs'], total['ok'], total['ok']/total['refs']*100, total['fail']))
        print('§3.5 阻止: {} 个错误引用 (100%)'.format(total['fail']))
        print('§3.5.1 Top1 真实相关: {}/{} = {:.0f}%'.format(
            total['rel'], total['rel_t'],
            total['rel']/total['rel_t']*100 if total['rel_t'] else 0))
        print('=' * 70)

    if args.path:
        # 自定义路径测试
        ref = args.path
        if not ref.startswith('note/'):
            ref = 'note/' + ref
        if os.path.isfile(ref):
            print('  路径正确: {!r}'.format(ref))
        else:
            print('  路径失效: {!r}'.format(ref))
            r = suggest_v2(ref, 5)
            if r:
                print('  §3.5.1 建议:')
                for s, sc in r:
                    print('    {} ({}) - {}'.format(sc, s.replace(os.sep, '/').replace('note/', ''),
                                                       '✓ 相关' if is_relevant(s, ref) else '✗ 噪声'))


if __name__ == '__main__':
    main()