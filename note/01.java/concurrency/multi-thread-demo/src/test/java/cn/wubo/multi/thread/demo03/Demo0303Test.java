package cn.wubo.multi.thread.demo03;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class Demo0303Test {

    @Autowired
    Demo0303 demo0303;

    @Test
    public void asyncSaveBatch(){
        demo0303.asyncSaveBatch();
    }
}