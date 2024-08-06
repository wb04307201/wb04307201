package cn.wubo.multi.thread.demo03;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class Demo0302Test {

    @Autowired
    Demo0302 demo0302;

    @Test
    void startCron() {
        demo0302.startCron("定时任务1");
        demo0302.startCron("定时任务2");

        try {
            Thread.sleep(60000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}