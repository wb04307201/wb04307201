# Spring Statemachine 状态机

**Spring Statemachine 是一个基于 Spring 框架的状态机实现，用于简化复杂状态转换逻辑的开发，适用于订单管理、工作流引擎、设备控制等需要严格状态管理的场景。**以下是其核心特性与实现方式的详细解析：

## 一、核心概念
1. **状态（State）**  
   系统所处的特定条件，如订单的“待支付”“已发货”“已完成”等。Spring Statemachine 支持多种状态类型：
    - **初始状态（Initial State）**：状态机的起点。
    - **结束状态（End State）**：状态机的终点。
    - **普通状态（Normal State）**：常规状态。
    - **选择状态（Choice State）**：基于条件分支（类似 `if/else`）。
    - **并行状态（Fork/Join State）**：支持并行执行分支（如多线程任务）。
    - **历史状态（History State）**：记录并恢复之前的状态。

2. **事件（Event）**  
   触发状态转换的动作，如用户点击“支付”按钮、定时器到期等。

3. **转换（Transition）**  
   状态之间的迁移规则，定义“从哪个状态”通过“什么事件”转移到“哪个状态”。

4. **守卫（Guard）**  
   转换的条件判断，如“仅当订单金额 < 1000 元时允许自动审批”。

5. **动作（Action）**  
   状态转换时执行的业务逻辑，如发送通知邮件、更新数据库记录等。

## 二、依赖配置
通过 Maven 或 Gradle 引入核心库：
```xml
<!-- Maven -->
<dependency>
    <groupId>org.springframework.statemachine</groupId>
    <artifactId>spring-statemachine-core</artifactId>
    <version>3.2.0</version> <!-- 或更高版本 -->
</dependency>
```
```groovy
// Gradle
implementation 'org.springframework.statemachine:spring-statemachine-core:3.2.0'
```

## 三、基础实现步骤
### 1. 定义状态与事件枚举
```java
public enum States {
    SI, // 初始状态
    S1, S2,
    SF  // 结束状态
}

public enum Events {
    E1, E2
}
```

### 2. 配置状态机
通过 `@Configuration` 和 `@EnableStateMachine` 注解启用状态机，并定义状态与转换规则：
```java
@Configuration
@EnableStateMachine
public class StateMachineConfig extends EnumStateMachineConfigurerAdapter<States, Events> {

    @Override
    public void configure(StateMachineStateConfigurer<States, Events> states) throws Exception {
        states.withStates()
              .initial(States.SI)  // 初始状态
              .states(EnumSet.allOf(States.class))  // 所有状态
              .end(States.SF);     // 结束状态
    }

    @Override
    public void configure(StateMachineTransitionConfigurer<States, Events> transitions) throws Exception {
        transitions.withExternal()  // 外部转换
                  .source(States.SI).target(States.S1).event(Events.E1)  // SI → S1 触发 E1
                  .and()
                  .withExternal()
                  .source(States.S1).target(States.S2).event(Events.E2);  // S1 → S2 触发 E2
    }
}
```

### 3. 添加守卫与动作
- **守卫**：控制转换是否允许执行。
```java
public class MyGuard implements Guard<States, Events> {
    @Override
    public boolean evaluate(StateContext<States, Events> context) {
        return context.getMessageHeader("key") != null; // 示例条件
    }
}

// 在配置中添加守卫
transitions.withExternal()
          .source(States.S1).target(States.S2).event(Events.E2)
          .guard(new MyGuard());
```

- **动作**：执行转换时的业务逻辑。
```java
public class MyAction implements Action<States, Events> {
    @Override
    public void execute(StateContext<States, Events> context) {
        System.out.println("Transition action executed");
    }
}

// 在配置中添加动作
transitions.withExternal()
          .source(States.SI).target(States.S1).event(Events.E1)
          .action(new MyAction());
```

## 四、高级特性
1. **层次状态（Hierarchical States）**  
   支持嵌套状态，例如：
   ```java
   @Override
   public void configure(StateMachineStateConfigurer<States, Events> states) throws Exception {
       states.withStates()
             .initial(States.SI)
             .state(States.S1)  // 父状态
             .and()
             .withStates()
             .parent(States.S1)  // 子状态
             .initial(States.S11)
             .state(States.S12);
   }
   ```

2. **状态机服务（StateMachineService）**  
   管理状态机实例的生命周期，支持多实例并发和持久化存储（如 Redis、JDBC）。
   ```java
   @Bean
   public StateMachineService<State, Event> stateMachineService(
           StateMachineFactory<State, Event> stateMachineFactory) {
       return new DefaultStateMachineService<>(stateMachineFactory);
   }

   // 使用示例
   @Autowired
   private StateMachineService<State, Event> stateMachineService;

   public void startProcess() {
       StateMachine<State, Event> stateMachine = stateMachineService.acquireStateMachine("machineId");
       stateMachine.start();
       stateMachine.sendEvent(Events.E1);
       stateMachineService.releaseStateMachine("machineId");
   }
   ```

3. **拦截器与监听器**
    - **拦截器**：在转换过程中插入自定义逻辑（如日志记录）。
    - **监听器**：响应状态机事件（如状态变更通知）。

4. **异常处理**  
   支持全局或局部异常处理，确保状态机在异常情况下仍能保持一致性。

## 五、典型应用场景
1. **订单管理系统**  
   定义状态：`待支付 → 已支付 → 已发货 → 已完成`，通过事件（如用户支付、物流更新）触发转换。

2. **工作流引擎**  
   管理审批流程，如 `提交 → 部门审批 → 财务审批 → 完成`，通过守卫控制权限（如仅财务可审批金额 > 10000 元的订单）。

3. **设备控制**  
   监控设备状态（如 `空闲 → 运行中 → 故障 → 维护中`），通过事件（如传感器信号）触发自动修复或报警。

## 六、优势总结
- **减少代码复杂度**：通过声明式配置替代大量 `if/else` 条件判断。
- **线程安全**：内置线程安全机制，支持高并发场景。
- **可扩展性**：支持层次状态、并行状态、持久化存储等高级特性。
- **与 Spring 生态无缝集成**：利用 Spring 的依赖注入、AOP 等特性简化开发。

**推荐场景**：需要严格状态管理、复杂业务逻辑或高可维护性的 Spring 应用。对于简单状态转换，可评估是否需要引入额外框架。