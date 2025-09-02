# Docker数据库使用指南

## 启动数据库容器

```bash
# 启动MySQL和Redis容器
cd backend/docker
./start_databases.sh
```

## 停止数据库容器

```bash
# 停止容器
cd backend/docker
./stop_databases.sh
```

## 数据库连接信息

### MySQL
- **主机**: localhost
- **端口**: 3306
- **数据库**: agentics_db
- **用户名**: agentics_user
- **密码**: agentics_password
- **Root密码**: rootpassword

### Redis
- **主机**: localhost
- **端口**: 6379
- **无密码**

## 手动操作

### 连接MySQL
```bash
# 进入MySQL容器
docker exec -it agentics_mysql mysql -u agentics_user -p agentics_db

# 或使用root用户
docker exec -it agentics_mysql mysql -u root -p
```

### 连接Redis
```bash
# 进入Redis容器
docker exec -it agentics_redis redis-cli
```

## 数据持久化

数据会自动持久化到Docker volumes:
- `mysql_data`: MySQL数据
- `redis_data`: Redis数据

## 故障排除

### 端口冲突
如果3306或6379端口被占用，修改`docker-compose.yml`中的端口映射：
```yaml
ports:
  - "3307:3306"  # 改为3307
```

### 重置数据库
```bash
cd backend/docker
docker-compose down -v  # 删除volumes
docker-compose up -d
```