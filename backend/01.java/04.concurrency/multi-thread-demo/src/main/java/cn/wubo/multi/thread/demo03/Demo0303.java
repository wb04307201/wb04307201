package cn.wubo.multi.thread.demo03;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionDefinition;
import org.springframework.transaction.TransactionStatus;
import org.springframework.transaction.support.DefaultTransactionDefinition;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Spring事务管理器PlatformTransactionManager
 * 多线程事务回滚
 */
@Slf4j
@Service
public class Demo0303 {

    @Autowired
    public PlatformTransactionManager transactionManager;

    /**
     * 异步批量保存数据的方法。
     * 该方法通过创建一个固定大小的线程池，执行批量保存操作。每个线程在执行过程中，
     * 会开启一个新的事务来保证数据的隔离性和一致性。如果某个线程在执行过程中发生异常，
     * 会记录失败次数，并在所有线程执行完毕后，决定是否回滚所有事务。
     */
    public void asyncSaveBatch() {
        // 定义线程池大小
        final int SIZE = 6;
        // 用于统计失败的线程数
        final AtomicInteger failedCounter = new AtomicInteger();

        // 使用CountDownLatch来等待所有线程执行完毕
        final CountDownLatch latch = new CountDownLatch(SIZE);

        // 创建一个固定大小的线程池
        final ExecutorService pool = Executors.newFixedThreadPool(SIZE);

        // 用于存放每个线程的事务状态
        List<TransactionStatus> transactionStatuses = Collections.synchronizedList(new ArrayList<TransactionStatus>());

        // 记录开始时间
        long beginTime = System.currentTimeMillis();

        // 提交任务给线程池执行
        for (int i = 0; i < SIZE; i++) {
            pool.execute(() -> {
                // 随机决定当前线程是否成功
                final boolean success = Math.random() > 0.1;
                log.info(Thread.currentThread().getName() + ", success = " + success);

                // 初始化事务定义并开启新事务
                DefaultTransactionDefinition def = new DefaultTransactionDefinition();
                def.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRES_NEW);
                TransactionStatus status = transactionManager.getTransaction(def);
                transactionStatuses.add(status);

                try {
                    // 执行业务逻辑
                } catch (Exception e) {
                    // 如果发生异常，失败计数器加一
                    failedCounter.getAndIncrement();
                } finally {
                    // 无论成功或失败，都提交事务
                    transactionManager.commit(status);
                }
                // 计数器减一，表示当前线程执行完毕
                latch.countDown();
            });
        }

        try {
            // 等待所有线程执行完毕
            latch.await();
            // 如果有线程执行失败，则回滚所有事务
            if (failedCounter.get() > 0) {
                for (TransactionStatus transactionStatus : transactionStatuses) {
                    transactionStatus.setRollbackOnly();
                }
                log.info("执行了回滚过程，回滚事物数据集合大小" + transactionStatuses.size());
            }
            // 计算并记录执行时间
            long endTime = System.currentTimeMillis();
            log.info("执行批量插入数据耗时" + (int) ((endTime - beginTime)) / 1000 + "秒");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

    }
}
