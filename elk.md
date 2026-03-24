## 安装docker
```shell
第一步：安装 Docker（适配阿里云 Linux 3）
# 1. 卸载旧版本（如有）
sudo yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine

# 2. 安装依赖
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 3. 添加阿里云 Docker 源（速度最快）
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 4. 安装 Docker 最新版
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin


第二步：配置 Docker 数据目录到 /dev/vda3（根目录 / 下）

sudo mkdir -p /docker-data
sudo chmod 701 /docker-data

# 2. 配置 daemon.json（指定数据目录）
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "data-root": "/docker-data",
  "registry-mirrors": ["https://mirror.aliyuncs.com"]
}
EOF

# 3. 重启 Docker 并设置开机自启
sudo systemctl daemon-reload
sudo systemctl start docker
sudo systemctl enable docker
sudo systemctl enable containerd


第三步：验证配置是否生效
# 1. 查看 Docker 数据目录
docker info | grep "Docker Root Dir"
# 正确输出：Docker Root Dir: /docker-data

# 2. 验证 Docker 功能
docker run --rm hello-world
# 能正常输出欢迎信息 → 配置成功

```

## 一、整体架构
```shell
业务服务器（多台）
    │
    │（Filebeat / Logstash）
    ▼
日志服务器
 ┌───────────────┐
 │   Logstash    │ ← 接收日志（5044）
 └──────┬────────┘
        ▼
 ┌───────────────┐
 │ Elasticsearch │ ← 存储日志
 └──────┬────────┘
        ▼
 ┌───────────────┐
 │   Kibana      │ ← 可视化
 └───────────────┘
```

## 二、日志服务器（ELK）部署
#####  1️⃣ 创建目录
```shell
mkdir -p /data/elk/{elasticsearch,logstash,kibana}
cd /data/elk
```

#### 2️⃣ docker-compose.yml
```yaml
version: '3.8'

services:

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
    volumes:
      - ./elasticsearch/data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - elk

  logstash:
    image: docker.elastic.co/logstash/logstash:8.12.0
    container_name: logstash
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch
    networks:
      - elk

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    container_name: kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - elk

networks:
  elk:
    driver: bridge
```

#### 3️⃣ Logstash 配置
```shell
# 创建目录：
mkdir -p /data/elk/logstash/pipeline
# 创建文件：
vim /data/elk/logstash/pipeline/logstash.conf
```
##### 内容：
```yaml
input {
  beats {
    port => 5044
  }
}

filter {
  # 可根据日志格式自定义解析
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

#### 4️⃣ 启动 ELK
```shell
docker-compose up -d

# 验证：访问elasticsearch:
curl http://你的服务器IP:9200
# 访问 Kibana：
http://你的服务器IP:5601
```


## 三、业务服务器（日志采集）
推荐用 Filebeat（更轻量）
#### 首先创建一个目录结构（推荐）：
```
mkdir -p /opt/filebeat/logs
mkdir -p /opt/filebeat/config
touch /opt/filebeat/config/filebeat.yml
touch /opt/filebeat/docker-compose.yml
```

#### 1.然后编写 docker-compose.yml 文件：
```shell
version: '3.8'

services:
  filebeat:
    container_name: filebeat
    image: docker.elastic.co/beats/filebeat:8.12.0
    user: root  # 赋予root权限以读取宿主机日志
    restart: always  # 容器异常退出时自动重启
    volumes:
      # 挂载宿主机日志目录
      - /var/log:/var/log
      # 挂载自定义日志目录（业务日志）
      - /www/wwwroot/feimao/server/logs:/app/logs
      # 挂载filebeat配置文件
      - ./config/filebeat.yml:/usr/share/filebeat/filebeat.yml
      # 挂载filebeat数据目录（持久化状态）
      - ./logs:/usr/share/filebeat/logs
#      # 必要的系统目录挂载（解决权限和日志读取问题）
#      - /var/lib/docker/containers:/var/lib/docker/containers:ro
#      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - elk_network
    # 可选：设置环境变量
    environment:
      - TZ=Asia/Shanghai  # 时区同步

networks:
  elk_network:
    driver: bridge
```
#### 2. 对应的 filebeat.yml 配置（/opt/filebeat/config/filebeat.yml）
```yaml
# 日志输入配置
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      # 宿主机系统日志
      - /var/log/*.log
      # 业务应用日志
      - /app/logs/*.log
    # 可选：添加自定义标签，方便在Kibana中筛选
    tags: ["business-server", "docker"]
    # 可选：设置编码（解决中文乱码）
    encoding: utf-8
    # 可选：多行日志处理（Java堆栈等）
    multiline.type: pattern
    multiline.pattern: '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
    multiline.negate: true
    multiline.match: after

# 输出到Logstash
output.logstash:
  hosts: ["日志服务器IP:5044"]
  # 可选：设置超时时间
  timeout: 15s

# 可选：开启filebeat自身日志（调试用）
logging.level: info
logging.to_files: true
logging.files:
  path: /usr/share/filebeat/logs
  name: filebeat
  keepfiles: 7
  permissions: 0644
```

#### 3. 使用方法
```shell
# 1.进入配置目录：
cd /opt/filebeat
# 2.启动容器：
docker-compose up -d
# 3.查看容器状态：
docker-compose ps
# 4.查看 filebeat 日志（调试）：
docker-compose logs -f filebeat
# 5.测试日志采集：
echo "hello elk $(date)" >> /var/log/test.log
```

#### 3️⃣ 测试日志
```shell
echo "hello elk" >> /var/log/test.log
```
