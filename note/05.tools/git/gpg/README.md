gpg --full-generate-key
密钥类型：RSA and RSA
密钥长度：4096
gpg --list-keys

上传公钥到密钥服务器：
gpg --keyserver keyserver.ubuntu.com --send-keys YOUR_KEY_ID

gpg --armor --export-secret-keys YOUR_KEY_ID > private-key.asc

OSSRH_USERNAME  Sonatype 用户名
OSSRH_PASSWORD  Sonatype 密码或 token
GPG_PRIVATE_KEY  GPG 私钥
GPG_PASSPHRASE  GPG 密钥密码