# Camunda 7

## SpringBoot集成Camunda 7
### 从maven集成Camunda7到SpringBoot
1. 创建SpringBoot项目(包含Mybatis和h2数据库驱动)
2. 添加依赖
```xml
    <dependency>
        <groupId>org.camunda.bpm.springboot</groupId>
        <artifactId>camunda-bpm-spring-boot-starter</artifactId>
        <version>7.21.0</version>
    </dependency>
    <dependency>
        <groupId>org.camunda.bpm.springboot</groupId>
        <artifactId>camunda-bpm-spring-boot-starter-rest</artifactId>
        <version>7.21.0</version>
    </dependency>
    <dependency>
        <groupId>org.camunda.bpm.springboot</groupId>
        <artifactId>camunda-bpm-spring-boot-starter-webapp</artifactId>
        <version>7.21.0</version>
    </dependency>
```
3. 添加配置
```yaml
# camunda登录信息配置
camunda.bpm:
  admin-user:
    id: admin  #???
    password: 123456  #??
    firstName: wu
  filter:
    create: All tasks

# h2连接信息
spring:
  datasource:
    url: jdbc:h2:file:./data/demo;AUTO_SERVER=TRUE
    username: sa
    password:
    driverClassName: org.h2.Driver
```
4. 启动
启动时生成Camunda 7数据库表结构

| 模块      | 表明                | 说明                                                     |
|---------|-------------------|--------------------------------------------------------|
| ACT_ID_ |                   | 用户模块                                                   |
| ACT_HI_ |                   | 流程历史记录                                                 |
| ACT_HI_ | act_hi_actinst    | 执行的活动历史                                                |
| ACT_HI_ | act_hi_taskinst   | 执行任务历史                                                 |
| ACT_HI_ | act_hi_procinst   | 执行流程实例历史                                               |
| ACT_HI_ | act_hi_varinst    | 流程变量历史表                                                |
| ACT_RE  |                   | 流程资源存储                                                 |
| ACT_RE  | act_re_procdef    | 流程定义存储                                                 |
| ACT_RE  | act_re_deployment | 自动部署，springboot每次启动都会重新部署，生成记录                         |
| ACT_RU_ |                   | 流程运行时表数据，流程结束后会删除                                      |
| ACT_RU  | act_ru_execution  | 运行时流程实例                                                |
| ACT_RU  | act_ru_task       | 运行时的任务                                                 |
| ACT_RU  | act_ru_variable   | 运行时的流程变量                                               |
| ACT_GE_ |                   | 流程通用数据                                                 |
| ACT_GE_ | act_ge_bytearray  | 每次部署的文件2进制数据，所以如果文件修改后，重启也没用，因为重新生成了记录，需要清掉数据库，或者这个表记录 |

启动时[控制台](http://localhost:8080/)界面  
![img.png](img.png)

5. 添加Camunda 7的swagger
添加仓库
```xml
    <repositories>
        <repository>
            <id>camunda</id>
            <name>camunda</name>
            <url>https://artifacts.camunda.com/artifactory/public/</url>
        </repository>
    </repositories>
```
添加依赖
```xml
        <dependency>
            <groupId>org.camunda.bpm.run</groupId>
            <artifactId>camunda-bpm-run-modules-swaggerui</artifactId>
            <version>${camunda7.version}</version>
        </dependency>
```
访问[Swagger](http://localhost:8080/swaggerui/)
![img_1.png](img_1.png)

6. 创建ui以及编译前端插件
创建vite+react前端项目ui  

7. 后端添加前端编译插件  
```xml
<plugin>
    <groupId>com.github.eirslett</groupId>
    <artifactId>frontend-maven-plugin</artifactId>
    <configuration>
        <workingDirectory>./ui</workingDirectory>
    </configuration>
    <executions>
        <execution>
            <id>install node and yarn</id>
            <goals>
                <goal>install-node-and-yarn</goal>
            </goals>
            <configuration>
                <nodeVersion>v18.20.4</nodeVersion>
                <yarnVersion>v1.22.19</yarnVersion>
            </configuration>
        </execution>
        <execution>
            <id>yarn install</id>
            <goals>
                <goal>yarn</goal>
            </goals>
            <phase>generate-resources</phase>
            <configuration>
                <arguments>install</arguments>
            </configuration>
        </execution>
        <execution>
            <id>yarn build</id>
            <goals>
                <goal>yarn</goal>
            </goals>
            <phase>generate-resources</phase>
            <configuration>
                <arguments>build</arguments>
            </configuration>
        </execution>
    </executions>
</plugin>
```
修改vite.config.js调整编译输出位置
```javascript
import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    build: {
        outDir: '../target/classes/META-INF/resources',
    },
})
```
mvn install后启动项目
![img_2.png](img_2.png)

8. 添加less
```shell
yarn add less --dev
```
修改vite.config.js添加less
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../target/classes/META-INF/resources',
  },
  css: {
    preprocessorOptions: {
      less: {
        javascriptEnabled: true, // 支持内联 JavaScript
        modifyVars: { // 更改主题
        }
      }
    }
  }
})
```

9. 增加bpmn.js
```shell
yarn add bpmn-js bpmn-js-properties-panel @bpmn-io/properties-panel camunda-bpmn-moddle
```
添加自定义的国际化i18n
```javascript
// translations.jsx

export default {
    "Activate create/remove space tool": "激活创建/移除空间工具",
    "Activate global connect tool": "激活全局连接工具",
    "Activate hand tool": "激活手动工具",
    "Activate lasso tool": "激活套索工具",
    "Ad-hoc": "临时",
    "Add lane above": "在上方添加泳道",
    "Add lane below": "在下方添加泳道",
    "Add text annotation": "添加文本注释",
    "Align elements": "对齐元素",
    "Align elements bottom": "元素底部对齐",
    "Align elements center": "元素居中对齐",
    "Align elements left": "元素左对齐",
    "Align elements middle": "元素中间对齐",
    "Align elements right": "元素右对齐",
    "Align elements top": "元素顶部对齐",
    "Append compensation activity": "追加补偿活动",
    "Append conditional intermediate catch event": "追加条件中间捕获事件",
    "Append end event": "追加结束事件",
    "Append gateway": "追加网关",
    "Append intermediate/boundary event": "追加中间/边界事件",
    "Append message intermediate catch event": "追加消息中间捕获事件",
    "Append receive task": "追加接收任务",
    "Append signal intermediate catch event": "追加信号中间捕获事件",
    "Append task": "追加任务",
    "Append timer intermediate catch event": "追加定时器中间捕获事件",
    "Business rule task": "业务规则任务",
    "Call activity": "调用活动",
    "Cancel boundary event": "取消边界事件",
    "Cancel end event": "取消结束事件",
    "Change element": "改变元素",
    "Collection": "集合",
    "Compensation boundary event": "补偿边界事件",
    "Compensation end event": "补偿结束事件",
    "Compensation intermediate throw event": "补偿中间抛出事件",
    "Compensation start event": "补偿开始事件",
    "Complex gateway": "复杂网关",
    "Conditional boundary event": "条件边界事件",
    "Conditional boundary event (non-interrupting)": "条件边界事件（非中断）",
    "Conditional flow": "条件流",
    "Conditional intermediate catch event": "条件中间捕获事件",
    "Conditional start event": "条件开始事件",
    "Conditional start event (non-interrupting)": "条件开始事件（非中断）",
    "Connect to other element": "连接到其他元素",
    "Connect using association": "使用关联连接",
    "Connect using data input association": "使用数据输入关联连接",
    "Create data object reference": "创建数据对象引用",
    "Create data store reference": "创建数据存储引用",
    "Create end event": "创建结束事件",
    "Create expanded sub-process": "创建扩展子流程",
    "Create gateway": "创建网关",
    "Create group": "创建组",
    "Create intermediate/boundary event": "创建中间/边界事件",
    "Create pool/participant": "创建池/参与者",
    "Create start event": "创建开始事件",
    "Create task": "创建任务",
    "Data object reference": "数据对象引用",
    "Data store reference": "数据存储引用",
    "Default flow": "默认流",
    "Delete": "删除",
    "Distribute elements horizontally": "水平分布元素",
    "Distribute elements vertically": "垂直分布元素",
    "Divide into three lanes": "分成三条泳道",
    "Divide into two lanes": "分成两条泳道",
    "Empty pool/participant": "空的池/参与者",
    "Empty pool/participant (removes content)": "空的池/参与者（删除内容）",
    "End event": "结束事件",
    "Error boundary event": "错误边界事件",
    "Error end event": "错误结束事件",
    "Error start event": "错误开始事件",
    "Escalation boundary event": "升级边界事件",

    "Process": "流程",
    "Name": "名称",
    "Value": "值",
    "ID": "唯一标识(ID)",
    "General": "基础属性",
    "Documentation": "文档",
    "Element documentation": "元素文档",

    "Create": "创建",
    "Priority": "优先级",
    "Job execution": "作业执行器",
    "Execution listeners": "执行器监听",
    "Event type": "事件类型",
    "start": "开始",
    "end": "结束",
    "Listener type": "监听类型",
    "Java class": "Java类",
    "Expression": "表达式",
    "Delegate expression": "委托表达式",
    "Script": "脚本",
    "Format": "格式",
    "<none>": "<无>",
    "Field injection": "字段注入",
    "Type": "类型",
    "String": "字符串",
    "Extension properties": "扩展属性",
};
```
```javascript
// customTranslate.jsx

import translations from './translations';

export default function customTranslate(template, replacements) {
    replacements = replacements || {};

    // Translate
    template = translations[template] || template;

    // Replace
    return template.replace(/{([^}]+)}/g, function(_, key) {
        return replacements[key] || '{' + key + '}';
    });
}
```
添加编辑器CustomModeler并使用国际化进行汉化
```javascript
// Camunda7Modeler/index.jsx

import {useEffect, useState} from "react";
import css from './index.module.less'
import BpmnModeler from 'camunda-bpmn-js/lib/camunda-platform/Modeler';
import 'camunda-bpmn-js/dist/assets/camunda-platform-modeler.css';
import customTranslate from '../i18n/customTranslate/customTranslate.jsx';


const Camunda7Modeler = () => {

    const [modelerInstance, setModelerInstance] = useState({})

    useEffect(() => {
        const customTranslateModule = {
            translate: ['value', customTranslate]
        };

        const modeler = new BpmnModeler({
            container: '#js-canvas',
            keyboard: {
                bindTo: window
            },
            propertiesPanel: {
                parent: '#js-properties-panel'
            },
            additionalModules: [
                customTranslateModule
            ],
        });

        // 注册bpmn实例
        const instance = {
            modeler: modeler,
            modeling: modeler.get("modeling"),
            moddle: modeler.get("moddle"),
            eventBus: modeler.get("eventBus"),
            bpmnFactory: modeler.get("bpmnFactory"),
            elementRegistry: modeler.get("elementRegistry"),
            replace: modeler.get("replace"),
            selection: modeler.get("selection"),
        };

        setModelerInstance(instance)

        modeler.importXML('<?xml version="1.0" encoding="UTF-8"?>\n' +
            '<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:omgdi="http://www.omg.org/spec/DD/20100524/DI" xmlns:omgdc="http://www.omg.org/spec/DD/20100524/DC" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="sid-38422fae-e03e-43a3-bef4-bd33b32041b2" targetNamespace="http://bpmn.io/bpmn" exporter="bpmn-js (https://demo.bpmn.io)" exporterVersion="16.3.0">\n' +
            '  <process id="Process_1" isExecutable="false">\n' +
            '    <startEvent id="StartEvent_1y45yut" name="hunger noticed">\n' +
            '      <outgoing>SequenceFlow_0h21x7r</outgoing>\n' +
            '    </startEvent>\n' +
            '    <task id="Task_1hcentk" name="choose recipe">\n' +
            '      <incoming>SequenceFlow_0h21x7r</incoming>\n' +
            '      <outgoing>SequenceFlow_0wnb4ke</outgoing>\n' +
            '    </task>\n' +
            '    <sequenceFlow id="SequenceFlow_0h21x7r" sourceRef="StartEvent_1y45yut" targetRef="Task_1hcentk" />\n' +
            '    <exclusiveGateway id="ExclusiveGateway_15hu1pt" name="desired dish?">\n' +
            '      <incoming>SequenceFlow_0wnb4ke</incoming>\n' +
            '    </exclusiveGateway>\n' +
            '    <sequenceFlow id="SequenceFlow_0wnb4ke" sourceRef="Task_1hcentk" targetRef="ExclusiveGateway_15hu1pt" />\n' +
            '  </process>\n' +
            '  <bpmndi:BPMNDiagram id="BpmnDiagram_1">\n' +
            '    <bpmndi:BPMNPlane id="BpmnPlane_1" bpmnElement="Process_1">\n' +
            '      <bpmndi:BPMNShape id="StartEvent_1y45yut_di" bpmnElement="StartEvent_1y45yut">\n' +
            '        <omgdc:Bounds x="152" y="102" width="36" height="36" />\n' +
            '        <bpmndi:BPMNLabel>\n' +
            '          <omgdc:Bounds x="134" y="145" width="73" height="14" />\n' +
            '        </bpmndi:BPMNLabel>\n' +
            '      </bpmndi:BPMNShape>\n' +
            '      <bpmndi:BPMNShape id="Task_1hcentk_di" bpmnElement="Task_1hcentk">\n' +
            '        <omgdc:Bounds x="240" y="80" width="100" height="80" />\n' +
            '      </bpmndi:BPMNShape>\n' +
            '      <bpmndi:BPMNShape id="ExclusiveGateway_15hu1pt_di" bpmnElement="ExclusiveGateway_15hu1pt" isMarkerVisible="true">\n' +
            '        <omgdc:Bounds x="395" y="95" width="50" height="50" />\n' +
            '        <bpmndi:BPMNLabel>\n' +
            '          <omgdc:Bounds x="388" y="152" width="65" height="14" />\n' +
            '        </bpmndi:BPMNLabel>\n' +
            '      </bpmndi:BPMNShape>\n' +
            '      <bpmndi:BPMNEdge id="SequenceFlow_0h21x7r_di" bpmnElement="SequenceFlow_0h21x7r">\n' +
            '        <omgdi:waypoint x="188" y="120" />\n' +
            '        <omgdi:waypoint x="240" y="120" />\n' +
            '      </bpmndi:BPMNEdge>\n' +
            '      <bpmndi:BPMNEdge id="SequenceFlow_0wnb4ke_di" bpmnElement="SequenceFlow_0wnb4ke">\n' +
            '        <omgdi:waypoint x="340" y="120" />\n' +
            '        <omgdi:waypoint x="395" y="120" />\n' +
            '      </bpmndi:BPMNEdge>\n' +
            '    </bpmndi:BPMNPlane>\n' +
            '  </bpmndi:BPMNDiagram>\n' +
            '</definitions>');

        modeler.get('canvas').zoom('fit-viewport');
    }, []);

    return (
        <div className={css.customModeler}>
            <div id="js-canvas" className={css.jsCanvas}></div>
            <div id="js-properties-panel" className={css.jsPropertiesPanel}></div>
            <button onClick={async () => {
                const xml = await modelerInstance.modeler.saveXML({format: true})
                console.log(xml)
            }}>printxml</button>
        </div>
    )
}

export default Camunda7Modeler;
```
![img_3.png](img_3.png)


