package cn.wubo.multi.thread.demo03;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionDefinition;
import org.springframework.transaction.TransactionStatus;
import org.springframework.transaction.support.DefaultTransactionDefinition;
import org.springframework.transaction.support.TransactionCallbackWithoutResult;
import org.springframework.transaction.support.TransactionTemplate;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * TransactionTemplate编程式事务
 * 多线程事务回滚
 */
@Slf4j
@Service
public class Demo0304 {

    @Autowired
    private TransactionTemplate transactionTemplate;

    /**
     * 异步批量保存方法。
     * 该方法使用固定大小的线程池来执行事务内的业务逻辑，以实现异步处理。
     * 线程池的大小被设置为6，这意味着最多同时有6个任务在执行。
     * 每个任务都会在自己的事务上下文中执行一段业务逻辑。
     */
    public void asyncSaveBatch() {
        // 定义线程池的大小为6
        final int SIZE = 6;
        // 创建一个固定大小的线程池
        final ExecutorService pool = Executors.newFixedThreadPool(SIZE);

        // 提交一个任务给线程池执行
        pool.execute(() -> {
            // 在事务模板的上下文中执行业务逻辑
            transactionTemplate.execute(new TransactionCallbackWithoutResult() {
                @Override
                protected void doInTransactionWithoutResult(TransactionStatus status) {
                    // 在这里编写业务逻辑代码
                    /* 业务逻辑 */
                }
            });
        });
    }

}
