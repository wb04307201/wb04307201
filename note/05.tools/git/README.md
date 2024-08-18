# Git

## Git Bash Here
### 统计每个人增删行数
```shell
git log --format='%aN' | sort -u | while read name; do echo -en "$name\t"; git log --author="$name" --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "added lines: %s, removed lines: %s, total lines: %s\n", add, subs, loc }' -; done
```

### 统计该项目所有的代码数
```shell
git log  --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "added lines: %s, removed lines: %s, total lines: %s\n", add, subs, loc }'
```

### 统计每个人增删行数
```shell
git log --format='%aN' | sort -u | while read name; do echo -en "$name\t"; git log --author="$name" --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "added lines: %s, removed lines: %s, total lines: %s\n", add, subs, loc }' -; done
```


## 子模块
### 子模块操作命令
```shell
git submodule add -b [branch] https://gitlab.com/b-project

#所有子模块查看标签
git submodule foreach git tag
#所有子模块按照标签拉取
git submodule foreach git pull origin 0.5.02-release

git submodule init
git submodule sync
git submodule update
git submodule update --init --remote 
```
### 删除子模块
1) $ git rm --cached [path]
根据路径删除子模块的记录
2) 编辑“.gitmodules”文件，将子模块的相关配置节点删除掉
清理子模块配置
3) 编辑“ .git/config”文件，将子模块的相关配置节点删除掉
清理子模块配置
4) 手动删除子模块残留的目录
清理脏文件

## [分支版本管理](version-controller%2FREADME.md)






